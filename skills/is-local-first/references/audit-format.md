# Audit format v1

An audit describes one product version, platform, data flow, and sync mode. Use the [schema](../assets/audit.schema.json), the [rubric](rubric.md), and the [example](../assets/example.audit.json). The example uses a fictional project and a Git commit recreated by the repository's offline tests.

- `commit` is the full lowercase commit ID of the audited repository. Use `version: null` when no release version applies. Set `rubricVersion` to the bundled rubric's source commit, adoption date, and `revision`. An audit without a revision counts as revision 1. Set `verification` to `static`.
- Each criterion has its rubric `value`, a concise explanation in `evidence`, the commit-pinned file permalink in `source`, and the literal lines in `quote`. Cite a line or range, for example `#L5-L8`. Copy the entire selection with its whitespace, excluding the final line terminator. The validator treats CRLF and LF as equivalent.
- Use `localFirstClaim: null` when the project makes no such claim. A claim has a literal `quote` and a commit-pinned `source`. The quote can be a fragment of a line. Add `translation` if needed.
- Cite the audited commit for sources from the audited repository. At least one source must come from that snapshot. When the release tree leaves out the documentation, cite the documentation file at another commit of the same repository. The report marks that commit. Evidence from a separate component's repository uses that repository's own commit.

## Validation

Run `python scripts/audit.py validate audit.json` from a copy of the skill directory. The command prints a JSON object with the computed `category` after the checks pass. On failure, it prints a diagnostic to stderr and exits with a nonzero status.

By default the validator reads raw UTF-8 files over HTTPS from GitHub, GitLab.com, or Codeberg. The source links follow each forge's commit permalink format. Use `--allow-host forge.example.org` to allow a trusted self-hosted GitLab or Forgejo host for that invocation. HTTPS redirects require a direct permalink.

For offline use, pass `--repo /path/to/clone`. Supply additional local clones with `--repo-map https://github.com/OWNER/REPO=/path/to/clone`. Local mode reads pinned Git objects and uses the bytes stored in the commit even if the checkout has changed.

The checks establish that citations exist and their quoted text matches. Assess whether each citation supports its rating as part of the audit review.
