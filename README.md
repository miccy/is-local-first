# is-local-first

An Agent Skill for auditing open-source apps, databases, and sync engines against the [Evolu comparison criteria](https://www.evolu.dev/docs/comparison). Each finding points to the lines at a specific commit that support it.

The project is before its first release. The development version includes the audit workflow, rubric, and evidence validator.

## Run an audit

Load the [`is-local-first` skill directory](skills/is-local-first/) into a client that supports Agent Skills. Ask a question like this:

> Is this project local-first? Audit the latest public release, evaluate notes and attachments separately, and show the evidence for each rating.

Provide a project name, official site, repository link, release, or local checkout. The skill records the exact version, platform, sync mode, and data flow it examined. It inspects the audited source statically.

- [Audit workflow](skills/is-local-first/SKILL.md)
- [Scoring rubric](skills/is-local-first/references/rubric.md)
- [Example audit JSON](skills/is-local-first/assets/example.audit.json)

## Validate an audit

Use Python 3.12 to check an [audit](skills/is-local-first/references/audit-format.md) against the bundled schema and compute its category.

```sh
python skills/is-local-first/scripts/audit.py validate audit.json
python skills/is-local-first/scripts/audit.py validate audit.json --repo /path/to/clone
```

The first command reads public commit-pinned evidence over HTTPS. The second reads Git objects offline.

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
