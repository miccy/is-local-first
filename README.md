# is-local-first

An Agent Skill for auditing open-source apps, databases, and sync engines against the [Evolu comparison criteria](https://www.evolu.dev/docs/comparison). Each finding points to the lines at a specific commit that support it.

The project is before its first release. The development version includes the audit workflow, rubric, and evidence validator.

## Install in Claude

### Claude chat or Desktop

1. [Download the skill ZIP from the latest successful GitLab main pipeline](https://gitlab.com/ownctrl/local-first/is-local-first/-/jobs/artifacts/main/download?job=validate-skill). Keep it zipped.
2. In Claude, open **Customize → Skills → + → Create skill → Upload a skill**. Choose the ZIP and enable **is-local-first**. [Claude's upload guide](https://support.claude.com/en/articles/12512180-use-skills-in-claude)
3. Start a new chat and paste the first audit below.

To build the upload from a local checkout, run this in the repository root:

```sh
mkdir -p dist
git archive --format=zip --prefix=is-local-first/ --output=dist/is-local-first.zip HEAD:skills/is-local-first
```

### Claude Code

Run these commands in your terminal:

```sh
claude plugin marketplace add miccy/is-local-first
claude plugin install is-local-first@ownctrl-local-first
```

For a local checkout, use `claude plugin marketplace add "$PWD"` from the repository root for the first command. Open a new Claude Code session after installation. Type `/is-local-first:is-local-first` followed by a project URL or the question below.

## Install in Codex

Run these commands in your terminal:

```sh
codex plugin marketplace add miccy/is-local-first
codex plugin add is-local-first@ownctrl-local-first
```

For a local checkout, use `codex plugin marketplace add "$PWD"` from the repository root for the first command. Start a new Codex session after installation. Run `/skills` or type `$` to pick **is-local-first**, then add a project URL or the question below. [Codex skills guide](https://learn.chatgpt.com/docs/build-skills)

To uninstall, run `codex plugin remove is-local-first@ownctrl-local-first` and then `codex plugin marketplace remove ownctrl-local-first`.

## Try your first audit

> Use is-local-first to audit https://github.com/kuku-mom/kuku at tag 0.6.0 on macOS. With sync enabled, do PNG attachments reach my second device? Show the source lines behind the answer.

Provide a project name, official site, repository link, release, or local checkout. The skill records the exact version, platform, sync mode, and data flow it examined. It inspects the audited source statically.

- [Audit workflow](skills/is-local-first/SKILL.md)
- [Scoring rubric](skills/is-local-first/references/rubric.md)
- [Example audit JSON](skills/is-local-first/assets/example.audit.json)
- [Report format](skills/is-local-first/references/output.md) and an [example report](skills/is-local-first/assets/example.report.md)

## Validate an audit

Use Python 3.12 to check an [audit](skills/is-local-first/references/audit-format.md) against the bundled schema and compute its category.

```sh
python skills/is-local-first/scripts/audit.py validate audit.json
python skills/is-local-first/scripts/audit.py validate audit.json --repo /path/to/clone
```

The first command reads public commit-pinned evidence over HTTPS. The second reads Git objects offline.

Print the chat report for one or more validated audits of the same release:

```sh
python skills/is-local-first/scripts/audit.py render audit.json
```

## Contributing

GitLab is the canonical home for code, issues, and merge requests. The public GitHub mirror follows GitLab. [Issues](https://gitlab.com/ownctrl/local-first/is-local-first/-/issues) · [Merge requests](https://gitlab.com/ownctrl/local-first/is-local-first/-/merge_requests) · [Security reports](SECURITY.md)

Run the same [Agent Skills validation](https://agentskills.io/specification#validation) used by CI from the repository root with Python 3.12 and Git.

```sh
python3.12 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements-ci.txt
skills-ref validate skills/is-local-first
python scripts/check_rubric.py
python -B -m unittest discover -s tests
```

Edit [rubric.json](skills/is-local-first/assets/rubric.json) to update the criteria or examples, then run `python scripts/check_rubric.py --write` to regenerate the [rubric reference](skills/is-local-first/references/rubric.md).
