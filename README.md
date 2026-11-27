# is-local-first

An Agent Skill in development for auditing open-source applications, databases, and sync engines against the [Evolu comparison criteria](https://www.evolu.dev/docs/comparison). The goal is to show how a specific version handles user data and link each finding to primary evidence.

The project is before its first release. The rubric is available for review and the audit workflow is under development.

## Contributing

GitLab is the canonical home for code, [issues](https://gitlab.com/ownctrl/local-first/is-local-first/-/issues), and [merge requests](https://gitlab.com/ownctrl/local-first/is-local-first/-/merge_requests). Report security issues via [SECURITY.md](SECURITY.md).

Run the same [Agent Skills validation](https://agentskills.io/specification#validation) used by CI from the repository root with Python 3.12 and Git.

```sh
python3.12 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements-ci.txt
skills-ref validate skills/is-local-first
python scripts/check_rubric.py
```

Edit [rubric.json](skills/is-local-first/assets/rubric.json) to update the criteria or examples, then run `python scripts/check_rubric.py --write` to regenerate the [rubric reference](skills/is-local-first/references/rubric.md).
