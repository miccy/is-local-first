"""Read commit-pinned evidence as UTF-8 text from a Git object or HTTPS."""

import os
import re
import subprocess
from dataclasses import dataclass
from http.client import HTTPException
from urllib.error import HTTPError, URLError
from urllib.parse import quote, unquote, urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener


COMMIT = re.compile(r"(?:[0-9a-f]{40}|[0-9a-f]{64})")
REPO_PART = re.compile(r"[A-Za-z0-9_.-]+")
HOST = re.compile(r"[a-z0-9](?:[a-z0-9-]*[a-z0-9])?(?:\.[a-z0-9](?:[a-z0-9-]*[a-z0-9])?)*")
LINES = re.compile(r"L([1-9][0-9]{0,8})(?:-L?([1-9][0-9]{0,8}))?")
PUBLIC_HOSTS = frozenset({"github.com", "gitlab.com", "codeberg.org"})
MAX_SOURCE_BYTES = 4 * 1024 * 1024
SOURCE_TIMEOUT = 15


class AuditError(ValueError):
    """An audit or its evidence could not be validated."""


@dataclass(frozen=True)
class Repository:
    host: str
    path: tuple[str, ...]

    def __str__(self):
        return "https://" + self.host + "/" + "/".join(self.path)


@dataclass(frozen=True)
class SourceFile:
    repository: Repository
    commit: str
    path: tuple[str, ...]
    raw_url: str


@dataclass(frozen=True)
class Citation:
    file: SourceFile
    first: int | None
    last: int | None


def split_url(url):
    if any(ord(char) <= 32 or ord(char) >= 127 for char in url):
        raise AuditError("URL must be ASCII with non-ASCII characters percent-encoded")
    parts = urlsplit(url)
    if (
        parts.scheme != "https"
        or not HOST.fullmatch(parts.netloc.lower())
        or "?" in url
        or not parts.path.startswith("/")
    ):
        raise AuditError("expected an HTTPS URL without credentials, port, or query")
    path = []
    for raw in parts.path[1:].split("/"):
        if re.search(r"%(?![0-9A-Fa-f]{2})", raw):
            raise AuditError("invalid percent encoding in URL path")
        segment = unquote(raw, errors="strict")
        if (
            segment in {"", ".", ".."}
            or any(char in "/\\" or ord(char) < 32 or ord(char) == 127 for char in segment)
        ):
            raise AuditError("invalid URL path segment")
        path.append(segment)
    return parts.netloc.lower(), tuple(path), parts.fragment


def repository_from_parts(host, path):
    if len(path) < 2 or (host in {"github.com", "codeberg.org"} and len(path) != 2):
        raise AuditError("expected a repository path with a namespace and project")
    if path[-1].endswith(".git") or not all(REPO_PART.fullmatch(part) for part in path):
        raise AuditError("expected a canonical repository URL without .git")
    if host == "github.com":
        path = tuple(part.lower() for part in path)
    return Repository(host, path)


def parse_repository(url):
    host, path, fragment = split_url(url)
    if fragment or "#" in url or host == "raw.githubusercontent.com":
        raise AuditError("expected a repository URL without a fragment")
    return repository_from_parts(host, path)


def parse_source(url):
    host, path, fragment = split_url(url)
    if host == "raw.githubusercontent.com":
        repo, rest = path[:2], path[2:]
        host, raw_host, marker = "github.com", host, ()
    elif host == "github.com" and path[2:3] == ("blob",):
        repo, rest = path[:2], path[3:]
        raw_host, marker = "raw.githubusercontent.com", ()
    elif host not in {"github.com", "gitlab.com"} and path[2:4] in {
        ("src", "commit"), ("raw", "commit")
    }:
        repo, rest = path[:2], path[4:]
        raw_host, marker = host, ("raw", "commit")
    elif host not in {"github.com", "codeberg.org"} and "-" in path:
        boundary = path.index("-")
        if path[boundary + 1:boundary + 2] not in {("blob",), ("raw",)}:
            raise AuditError("expected a GitLab blob or raw URL")
        repo, rest = path[:boundary], path[boundary + 2:]
        raw_host, marker = host, ("-", "raw")
    else:
        raise AuditError("expected a GitHub, GitLab, or Forgejo file permalink")

    repository = repository_from_parts(host, repo)
    if len(rest) < 2 or not COMMIT.fullmatch(rest[0]):
        raise AuditError("expected a full lowercase commit ID in the file URL")
    commit, *file_path = rest
    raw_path = "/".join(quote(part, safe="") for part in (*repo, *marker, *rest))
    file = SourceFile(repository, commit, tuple(file_path), f"https://{raw_host}/{raw_path}")

    if not fragment and "#" not in url:
        return Citation(file, None, None)
    match = LINES.fullmatch(fragment)
    if match is None:
        raise AuditError("expected a line anchor such as #L5-L8")
    first = int(match[1])
    last = int(match[2] or match[1])
    if last < first:
        raise AuditError("line range ends before it starts")
    return Citation(file, first, last)


def read_utf8(body):
    if len(body) > MAX_SOURCE_BYTES:
        raise AuditError(f"source exceeds {MAX_SOURCE_BYTES} bytes")
    try:
        return body.decode("utf-8").replace("\r\n", "\n")
    except UnicodeError as error:
        raise AuditError("source is not UTF-8 text") from error


class LocalReader:
    def __init__(self, clones):
        self.clones = clones
        self.verified_commits = set()
        self.env = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}
        self.env.update({
            "GIT_ALLOW_PROTOCOL": "",
            "GIT_CONFIG_GLOBAL": os.devnull,
            "GIT_CONFIG_NOSYSTEM": "1",
            "GIT_NO_LAZY_FETCH": "1",
            "GIT_NO_REPLACE_OBJECTS": "1",
            "GIT_OPTIONAL_LOCKS": "0",
            "GIT_TERMINAL_PROMPT": "0",
        })

    def git(self, clone, *args):
        try:
            return subprocess.run(
                ["git", "-C", str(clone), "cat-file", *args],
                env=self.env, capture_output=True, check=True, timeout=SOURCE_TIMEOUT,
            ).stdout
        except (subprocess.SubprocessError, OSError) as error:
            raise AuditError("Git could not read the requested object from the local clone") from error

    def __call__(self, file):
        clone = self.clones.get(file.repository)
        if clone is None:
            raise AuditError(f"no local clone mapped for {file.repository}")
        pinned = (clone, file.commit)
        if pinned not in self.verified_commits:
            if self.git(clone, "-t", file.commit) != b"commit\n":
                raise AuditError("source ID must identify a commit object")
            self.verified_commits.add(pinned)
        object_name = file.commit + ":" + "/".join(file.path)
        if int(self.git(clone, "-s", object_name)) > MAX_SOURCE_BYTES:
            raise AuditError(f"source exceeds {MAX_SOURCE_BYTES} bytes")
        return read_utf8(self.git(clone, "blob", object_name))


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


class HttpReader:
    def __init__(self, allowed_hosts=()):
        self.hosts = PUBLIC_HOSTS.union(allowed_hosts)
        self.opener = build_opener(NoRedirect())

    def __call__(self, file):
        if file.repository.host not in self.hosts:
            raise AuditError(f"HTTPS host {file.repository.host} is not allowed")
        request = Request(file.raw_url, headers={
            "Accept": "application/octet-stream, text/plain",
            "User-Agent": "is-local-first/audit-v1",
        })
        try:
            with self.opener.open(request, timeout=SOURCE_TIMEOUT) as response:
                if response.headers.get_content_type() == "text/html":
                    raise AuditError("expected raw source text, received HTML")
                return read_utf8(response.read(MAX_SOURCE_BYTES + 1))
        except HTTPError as error:
            error.close()
            raise AuditError(f"raw source returned HTTP {error.code}") from error
        except (URLError, HTTPException, OSError) as error:
            raise AuditError("could not read raw source over HTTPS") from error
