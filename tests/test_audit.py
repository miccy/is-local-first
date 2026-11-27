import copy
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from email.message import Message
from pathlib import Path
from unittest.mock import Mock
from urllib.error import HTTPError

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "is-local-first"
FIXTURES = Path(__file__).with_name("fixtures")
EVIDENCE = FIXTURES / "evidence.md"
sys.path.insert(0, str(SKILL / "scripts"))

from audit import ASSETS, check_schema, load_json, validate_audit
from audit_sources import AuditError, HttpReader, NoRedirect, parse_repository, parse_source
from report import render_report


class AuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls.temp.cleanup)
        cls.root = Path(cls.temp.name)
        cls.repo = cls.root / "clone"
        cls.repo.mkdir()
        env = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}
        env.update({
            "GIT_CONFIG_GLOBAL": os.devnull,
            "GIT_CONFIG_NOSYSTEM": "1",
            "GIT_AUTHOR_NAME": "Fixture",
            "GIT_AUTHOR_EMAIL": "fixture@example.invalid",
            "GIT_COMMITTER_NAME": "Fixture",
            "GIT_COMMITTER_EMAIL": "fixture@example.invalid",
            "GIT_AUTHOR_DATE": "2020-01-01T00:00:00+00:00",
            "GIT_COMMITTER_DATE": "2020-01-01T00:00:00+00:00",
        })

        def git(*args):
            return subprocess.check_output([
                "git", "-C", str(cls.repo), "-c", "core.autocrlf=false",
                "-c", "commit.gpgsign=false", "-c", f"core.hooksPath={os.devnull}", *args,
            ], env=env, text=True).strip()

        git("init", "-q", "--initial-branch=main", "--object-format=sha1", "--template=")
        cls.worktree_file = cls.repo / "README.md"
        cls.worktree_file.write_bytes(EVIDENCE.read_bytes())
        git("add", "--", "README.md")
        git("commit", "-qm", "test: add audit evidence fixture")
        cls.example = load_json(ASSETS / "example.audit.json")
        if git("rev-parse", "HEAD") != cls.example["commit"]:
            raise RuntimeError("fixture commit differs from example.audit.json")

    def setUp(self):
        self.audit = copy.deepcopy(self.example)
        self.path = self.root / "audit.json"

    def run_cli(self, document=None, *options):
        self.path.write_text(document if document is not None else json.dumps(self.audit), encoding="utf-8")
        return subprocess.run(
            [sys.executable, str(SKILL / "scripts" / "audit.py"), "validate", str(self.path),
             "--repo", str(self.repo), *options],
            capture_output=True, text=True, timeout=30,
        )

    def assert_invalid(self, message):
        result = self.run_cli()
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertIn(message, result.stderr)
        self.assertEqual(result.stdout, "")

    def render_cli(self, *args):
        return subprocess.run(
            [sys.executable, str(SKILL / "scripts" / "audit.py"), "render", *map(str, args)],
            capture_output=True, text=True, encoding="utf-8", timeout=30,
        )

    def assert_report(self, snapshot, *args):
        """Compare a rendered report with its snapshot. UPDATE_SNAPSHOTS=1 rewrites it."""
        result = self.render_cli(*args)
        self.assertEqual(result.returncode, 0, result.stderr)
        if os.environ.get("UPDATE_SNAPSHOTS"):
            snapshot.write_text(result.stdout, encoding="utf-8")
        self.assertEqual(result.stdout, snapshot.read_text(encoding="utf-8"))
        return result.stdout

    def write_audit(self, name="audit.json"):
        path = self.root / name
        path.write_text(json.dumps(self.audit), encoding="utf-8")
        return path

    def test_render_database_report(self):
        report = self.assert_report(
            ASSETS / "example.report.md", ASSETS / "example.audit.json", "--repo", self.repo,
        )
        self.assertIn("citations machine-verified", report)
        self.assertNotIn("|", report)

    def test_render_application_with_two_flows(self):
        report = self.assert_report(
            ASSETS / "example-application.report.md",
            FIXTURES / "app-records.audit.json", FIXTURES / "app-attachments.audit.json",
            "--repo", self.repo,
        )
        self.assertIn("## Local-first\n", report)
        self.assertIn("## Not local-first yet\n", report)

    def test_render_unverified_report_says_so(self):
        report = self.assert_report(
            FIXTURES / "report-unverified.md", ASSETS / "example.audit.json", "--unverified",
        )
        self.assertIn("## Local-first (provisional)", report)
        self.assertIn("**Not machine-verified.**", report)
        self.assertNotIn("citations machine-verified", report)

    def test_render_checks_evidence_unless_unverified(self):
        self.audit["criteria"]["offline"]["quote"] = "A quote that the source does not contain."
        path = self.write_audit()
        result = self.render_cli(path, "--repo", self.repo)
        self.assertEqual(result.returncode, 1)
        self.assertIn("quote does not match", result.stderr)
        self.assertEqual(result.stdout, "")
        self.assertEqual(self.render_cli(path, "--unverified").returncode, 0)

    def test_render_unverified_takes_no_source_options(self):
        result = self.render_cli(self.write_audit(), "--unverified", "--repo", self.repo)
        self.assertEqual(result.returncode, 1)
        self.assertIn("--unverified reads no sources", result.stderr)

    def test_render_requires_one_snapshot(self):
        first = self.write_audit("first.json")
        self.audit["maturity"] = "beta"
        result = self.render_cli(first, self.write_audit("second.json"), "--repo", self.repo)
        self.assertEqual(result.returncode, 1)
        self.assertIn("maturity differs", result.stderr)

    def test_render_keeps_audit_text_literal(self):
        self.audit["project"]["name"] = "Example\n# Records"
        self.audit["scope"]["dataFlow"] = "<img src=x> records"
        self.audit["criteria"]["offline"]["evidence"] = "See [this](https://example.invalid) *now*."
        result = self.render_cli(self.write_audit(), "--repo", self.repo)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(result.stdout.startswith("# Example # Records 1.2.0\n"))
        self.assertIn("**\\<img src=x\\> records**", result.stdout)
        self.assertIn("See \\[this\\](https://example.invalid) \\*now\\*.", result.stdout)

    def test_render_fences_quotes_that_contain_fences(self):
        from report import fenced
        self.assertEqual(fenced("a\n```\nb"), "````text\na\n```\nb\n````")

    def test_pinned_git_blob_wins_over_dirty_checkout(self):
        self.addCleanup(self.worktree_file.write_bytes, EVIDENCE.read_bytes())
        self.worktree_file.write_text("A dirty checkout must not change the evidence.\n", encoding="utf-8")
        result = self.run_cli()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout), {"category": "Local-first"})
        self.assertIn("dirty checkout", self.worktree_file.read_text(encoding="utf-8"))

    def test_branch_url(self):
        proof = self.audit["criteria"]["offline"]
        proof["source"] = proof["source"].replace(self.audit["commit"], "main")
        self.assert_invalid("full lowercase commit ID")

    def test_out_of_bounds_line(self):
        proof = self.audit["criteria"]["offline"]
        proof["source"] = proof["source"].replace("#L2", "#L200")
        self.assert_invalid("outside the source")

    def test_shifted_line(self):
        proof = self.audit["criteria"]["offline"]
        proof["source"] = proof["source"].replace("#L2", "#L3")
        self.assert_invalid("quote does not match the cited source lines")

    def test_required_evidence(self):
        del self.audit["criteria"]["offline"]["evidence"]
        self.assert_invalid("criteria.offline.evidence: required field is missing")

    def test_unknown_rating(self):
        self.audit["criteria"]["offline"]["value"] = "maybe"
        self.assert_invalid("unknown rating 'maybe'")

    def test_na_outside_criterion_seven(self):
        self.audit["criteria"]["offline"]["value"] = "n/a"
        self.assert_invalid("n/a is only allowed for keysNotAccounts")

    def test_missing_anchor(self):
        proof = self.audit["criteria"]["offline"]
        proof["source"] = proof["source"].split("#")[0]
        self.assert_invalid("requires a source line anchor")

    def test_claim_quote_must_be_present(self):
        self.audit["localFirstClaim"]["quote"] = "unproven local-first claim"
        self.assert_invalid("localFirstClaim: quote does not match")

    def test_project_commit_mismatch(self):
        self.audit["commit"] = "0" * 40
        self.assert_invalid("project citation must use the audit commit")

    def test_local_mode_requires_explicit_mapping_for_other_repository(self):
        self.audit["criteria"]["offline"]["source"] = (
            self.audit["criteria"]["offline"]["source"].replace("example/", "other/")
        )
        self.assert_invalid("no local clone mapped for https://github.com/other/")

    def test_explicit_local_mapping_for_other_repository(self):
        proof = self.audit["criteria"]["offline"]
        proof["source"] = proof["source"].replace("example/", "other/")
        result = self.run_cli(
            None, "--repo-map", f"https://github.com/other/is-local-first-audit-fixture={self.repo}"
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout), {"category": "Local-first"})

    def test_rubric_pin_mismatch(self):
        self.audit["rubricVersion"]["adoptedOn"] = "2000-01-01"
        self.assert_invalid("rubricVersion does not match")

    def test_duplicate_json_keys(self):
        result = self.run_cli('{"schemaVersion":1,"schemaVersion":2}')
        self.assertEqual(result.returncode, 1)
        self.assertIn("duplicate JSON key 'schemaVersion'", result.stderr)


class ReaderTests(unittest.TestCase):
    commit = "a" * 40

    def test_forge_permalink_shapes(self):
        cases = [
            ("https://github.com/o/r/blob/", "https://raw.githubusercontent.com/o/r/", "#L1-L2"),
            ("https://gitlab.com/g/sub/r/-/blob/", "https://gitlab.com/g/sub/r/-/raw/", "#L1-2"),
            ("https://codeberg.org/o/r/src/commit/", "https://codeberg.org/o/r/raw/commit/", "#L1-L2"),
            ("https://forge.example/o/r/src/commit/", "https://forge.example/o/r/raw/commit/", "#L1-L2"),
        ]
        for permalink, raw, anchor in cases:
            with self.subTest(permalink=permalink):
                citation = parse_source(permalink + self.commit + "/a%20b.md" + anchor)
                self.assertEqual(citation.file.path, ("a b.md",))
                self.assertEqual(citation.file.raw_url, raw + self.commit + "/a%20b.md")
                self.assertEqual((citation.first, citation.last), (1, 2))

    def test_invalid_urls_are_rejected(self):
        base = f"github.com/o/r/blob/{self.commit}/"
        for url in [
            "http://" + base + "a.md#L1",
            "https://user@" + base + "a.md#L1",
            "https://" + base + "%2e%2e/a.md#L1",
            "https://" + base + "%2Fetc#L1",
            "https://" + base + "a.md?ref=main#L1",
            "https://" + base + "a.md#L2-L1",
        ]:
            with self.subTest(url=url), self.assertRaises(ValueError):
                parse_source(url)

    def test_http_reader_requests_raw_url_and_preserves_whitespace(self):
        citation = parse_source(f"https://github.com/o/r/blob/{self.commit}/README.md#L1")
        reader = HttpReader()
        response = io.BytesIO(b"  line  \r\n")
        response.headers = Message()
        response.headers["Content-Type"] = "text/plain"
        reader.opener = Mock()
        reader.opener.open.return_value = response
        self.assertEqual(reader(citation.file), "  line  \n")
        request = reader.opener.open.call_args.args[0]
        self.assertEqual(request.full_url, citation.file.raw_url)

    def test_http_error_does_not_follow_redirect(self):
        citation = parse_source(f"https://github.com/o/r/blob/{self.commit}/README.md#L1")
        reader = HttpReader()
        reader.opener = Mock()
        reader.opener.open.side_effect = HTTPError(
            citation.file.raw_url, 302, "Found", Message(), io.BytesIO()
        )
        with self.assertRaisesRegex(AuditError, "HTTP 302"):
            reader(citation.file)
        self.assertIsNone(NoRedirect().redirect_request(
            None, None, 302, "Found", {}, "https://internal.example/"
        ))

    def test_custom_forge_requires_opt_in_before_request(self):
        citation = parse_source(f"https://forge.example/o/r/src/commit/{self.commit}/README.md#L1")
        reader = HttpReader()
        reader.opener = Mock()
        with self.assertRaisesRegex(AuditError, "not allowed"):
            reader(citation.file)
        reader.opener.open.assert_not_called()
        response = io.BytesIO(b"line\n")
        response.headers = Message()
        allowed = HttpReader(["forge.example"])
        allowed.opener = Mock()
        allowed.opener.open.return_value = response
        self.assertEqual(allowed(citation.file), "line\n")

    def test_reviewed_audits_match_schema_and_recorded_reports(self):
        """Reviewed audits stay valid offline; their citations were checked against the source at review time."""
        schema = load_json(ASSETS / "audit.schema.json")
        rubric = load_json(ASSETS / "rubric.json")
        folders = sorted({path.parent for path in (ROOT / "audits").glob("*/*/*.audit.json")})
        self.assertTrue(folders)
        for folder in folders:
            with self.subTest(folder=folder.relative_to(ROOT).as_posix()):
                self.assertTrue((folder / "review.md").is_file())
                audits, categories = [], []
                for path in sorted(folder.glob("*.audit.json")):
                    audit = load_json(path)
                    check_schema(audit, schema, schema, "audit")
                    project = parse_repository(audit["project"]["repository"])
                    audits.append(audit)
                    categories.append(validate_audit(audit, rubric, project, None))
                report = render_report(audits, categories, rubric, True)
                self.assertEqual(report, (folder / "report.md").read_text(encoding="utf-8"))

    def test_rubric_examples_and_cached_evidence(self):
        sample = load_json(ASSETS / "example.audit.json")
        rubric = load_json(ASSETS / "rubric.json")
        project = parse_repository(sample["project"]["repository"])
        for example in rubric["examples"]:
            with self.subTest(name=example["name"]):
                audit = copy.deepcopy(sample)
                if not example["claim"]:
                    audit["localFirstClaim"] = None
                audit["version"] = example["version"]
                audit["maturity"] = example["maturity"]
                for key, entry in audit["criteria"].items():
                    entry["value"] = example["overrides"].get(key, "meets")
                reader = Mock(return_value=EVIDENCE.read_text(encoding="utf-8"))
                self.assertEqual(validate_audit(audit, rubric, project, reader), example["expected"])
                self.assertEqual(reader.call_count, 1)


if __name__ == "__main__":
    unittest.main()
