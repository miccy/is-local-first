"""Validate a static is-local-first audit and compute its category."""

import argparse
import json
import re
import sys
from pathlib import Path

# The CLI reads audits and source repositories without writing bytecode beside the skill.
sys.dont_write_bytecode = True

from audit_sources import AuditError, HOST, HttpReader, LocalReader, parse_repository, parse_source
from rubric import classify


ASSETS = Path(__file__).resolve().parents[1] / "assets"
MAX_AUDIT_BYTES = 1024 * 1024
CLAIM_TERM = re.compile(r"\blocal[-\s–‑]+first\b", re.IGNORECASE)
SCHEMA_KEYWORDS = {
    "$schema", "$defs", "$ref", "title", "description", "type", "const", "enum",
    "required", "properties", "additionalProperties", "pattern", "maxLength",
}
JSON_TYPES = {"object": dict, "string": str, "null": type(None)}


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise AuditError(f"duplicate JSON key {key!r}")
        result[key] = value
    return result


def invalid_constant(value):
    raise AuditError(f"invalid JSON constant {value!r}")


def load_json(path):
    with path.open("rb") as stream:
        content = stream.read(MAX_AUDIT_BYTES + 1)
    if len(content) > MAX_AUDIT_BYTES:
        raise AuditError(f"{path.name} exceeds {MAX_AUDIT_BYTES} bytes")
    try:
        return json.loads(
            content.decode("utf-8"), object_pairs_hook=unique_object,
            parse_constant=invalid_constant,
        )
    except (ValueError, RecursionError) as error:
        raise AuditError(f"{path.name}: {error}") from error


def matches_type(value, expected):
    if expected == "integer":
        return type(value) is int or (type(value) is float and value.is_integer())
    return type(value) is JSON_TYPES[expected]


def check_schema(value, rule, root, location):
    """Apply the JSON Schema vocabulary used by the bundled audit schema."""
    unsupported = rule.keys() - SCHEMA_KEYWORDS
    if unsupported:
        raise AuditError(f"unsupported bundled schema keyword {min(unsupported)!r}")
    if "$ref" in rule:
        ref = rule["$ref"]
        if not ref.startswith("#/$defs/"):
            raise AuditError(f"unsupported bundled schema reference {ref!r}")
        check_schema(value, root["$defs"][ref.removeprefix("#/$defs/")], root, location)

    if "type" in rule:
        types = rule["type"] if isinstance(rule["type"], list) else [rule["type"]]
        if not any(matches_type(value, expected) for expected in types):
            raise AuditError(f"{location}: expected {' or '.join(types)}")
    if "const" in rule and value != rule["const"]:
        raise AuditError(f"{location}: expected {rule['const']!r}")
    if "enum" in rule and value not in rule["enum"]:
        if location.endswith(".value"):
            if value == "n/a":
                raise AuditError(f"{location}: n/a is only allowed for keysNotAccounts")
            raise AuditError(f"{location}: unknown rating {value!r}")
        raise AuditError(f"{location}: expected one of {', '.join(rule['enum'])}")
    if isinstance(value, str):
        if any(0xD800 <= ord(char) <= 0xDFFF for char in value):
            raise AuditError(f"{location}: expected valid Unicode text")
        if "pattern" in rule and re.search(rule["pattern"], value) is None:
            raise AuditError(f"{location}: invalid text or format")
        if "maxLength" in rule and len(value) > rule["maxLength"]:
            raise AuditError(f"{location}: maximum length is {rule['maxLength']}")
    if isinstance(value, dict):
        properties = rule.get("properties", {})
        for key in rule.get("required", ()):
            if key not in value:
                raise AuditError(f"{location}.{key}: required field is missing")
        if rule.get("additionalProperties") is False:
            extra = value.keys() - properties.keys()
            if extra:
                raise AuditError(f"{location}: unexpected field {min(extra)!r}")
        for key, child_rule in properties.items():
            if key in value:
                check_schema(value[key], child_rule, root, f"{location}.{key}")


def audit_citations(audit, project):
    entries = [
        (f"criteria.{key}", entry, True)
        for key, entry in audit["criteria"].items()
    ]
    claim = audit["localFirstClaim"]
    if claim is not None:
        if not CLAIM_TERM.search(claim["quote"]):
            raise AuditError("localFirstClaim.quote: quote must contain the term local-first")
        entries.append(("localFirstClaim", claim, False))

    citations = []
    has_project_source = False
    for location, entry, needs_lines in entries:
        try:
            citation = parse_source(entry["source"])
            if citation.file.repository == project:
                if citation.file.commit != audit["commit"]:
                    raise AuditError("project citation must use the audit commit")
                has_project_source = True
            if needs_lines and citation.first is None:
                raise AuditError("criterion evidence requires a source line anchor")
        except ValueError as error:
            raise AuditError(f"{location}.source: {error}") from error
        citations.append((location, citation, entry["quote"], needs_lines))
    if not has_project_source:
        raise AuditError("at least one source must cite the audited repository and commit")
    return citations


def check_quote(text, citation, quote, exact_lines):
    expected = quote.replace("\r\n", "\n")
    selected = text
    if citation.first is not None:
        lines = text.removesuffix("\n").split("\n") if text else []
        if citation.last > len(lines):
            raise AuditError(f"line range L{citation.first}-L{citation.last} is outside the source")
        selected = "\n".join(lines[citation.first - 1:citation.last])
    if exact_lines and expected != selected:
        raise AuditError("quote does not match the cited source lines")
    if not exact_lines and expected not in selected:
        raise AuditError("quote does not match the cited source")


def validate_audit(audit, rubric, project, reader):
    expected_rubric = {
        "commit": rubric["source"]["commit"], "adoptedOn": rubric["source"]["adoptedOn"],
    }
    if audit["rubricVersion"] != expected_rubric:
        raise AuditError("rubricVersion does not match the bundled rubric")

    ratings = {key: entry["value"] for key, entry in audit["criteria"].items()}
    category = classify(
        rubric, ratings, audit["localFirstClaim"] is not None,
        audit["maturity"], audit["version"],
    )
    cache = {}
    for location, citation, quote, exact_lines in audit_citations(audit, project):
        try:
            if citation.file not in cache:
                cache[citation.file] = reader(citation.file)
            check_quote(cache[citation.file], citation, quote, exact_lines)
        except AuditError as error:
            raise AuditError(f"{location}: {error}") from error
    return category


def make_reader(args, project):
    if args.repo is None:
        if args.repo_map:
            raise AuditError("--repo-map requires --repo")
        if any(not HOST.fullmatch(host) for host in args.allow_host):
            raise AuditError("--allow-host requires a hostname without a scheme or port")
        return HttpReader(args.allow_host)
    if args.allow_host:
        raise AuditError("--allow-host is only available in HTTPS mode")
    clones = {project: args.repo}
    for mapping in args.repo_map:
        url, separator, path = mapping.partition("=")
        if not separator or not path:
            raise AuditError("--repo-map requires REPOSITORY_URL=PATH")
        repository = parse_repository(url)
        if repository in clones:
            raise AuditError(f"duplicate local clone mapping for {repository}")
        clones[repository] = Path(path)
    for clone in clones.values():
        bare = (clone / "HEAD").is_file() and (clone / "objects").is_dir()
        if not ((clone / ".git").exists() or bare):
            raise AuditError(f"expected a local Git clone root: {clone}")
    return LocalReader(clones)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    validate = commands.add_parser("validate", help="validate evidence and print the computed category")
    validate.add_argument("audit", type=Path, help="path to audit.json")
    validate.add_argument("--repo", type=Path, help="read only from this local Git clone")
    validate.add_argument("--repo-map", action="append", default=[], metavar="URL=PATH")
    validate.add_argument("--allow-host", type=str.lower, action="append", default=[], metavar="HOST")
    args = parser.parse_args()

    try:
        audit = load_json(args.audit)
        schema = load_json(ASSETS / "audit.schema.json")
        check_schema(audit, schema, schema, "audit")
        rubric = load_json(ASSETS / "rubric.json")
        project = parse_repository(audit["project"]["repository"])
        category = validate_audit(audit, rubric, project, make_reader(args, project))
    except (ValueError, OSError) as error:
        print(f"Invalid audit: {error}", file=sys.stderr)
        return 1
    print(json.dumps({"category": category}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
