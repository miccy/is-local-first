# Report format

The report is plain Markdown that reads top to bottom on a narrow phone screen. It is generated from the saved audits, so the same data always gives the same text.

## Render the report

Run the renderer from the skill directory with one `audit.json` per data flow. All audits in one report share the project, version, commit, maturity, and rubric version.

```sh
python scripts/audit.py render /path/to/audit.json
python scripts/audit.py render notes.audit.json attachments.audit.json --repo /path/to/local/clone
python scripts/audit.py render /path/to/audit.json --unverified
```

`render` runs the same checks as `validate` and takes the same source options. It prints the report only when every citation matches its source. Use `--unverified` when the sources cannot be read. That report marks each category as provisional and says **Not machine-verified**.

## Present the result

1. Answer the user's question in one or two sentences. For a data flow that the audited sync mode excludes, say first that this data does not sync.
2. Paste the rendered report unchanged. Keep its order, wording, symbols, and links.
3. For an application, add a `## Practical behavior` section after the report. Cover the account or server needed for first use, where data is stored locally, the sync backend, use of the data in another program, and availability during a provider outage. Cite the audited release and label observations from source reading as static. State that this section does not affect the category.

Without Python, write the same layout by hand from the audit, take the category from the [rubric decision rules](rubric.md#category), and mark it as the `--unverified` report does.

## Layout

Each data flow is one section, in the order the audits were given.

- **Category.** A second-level heading. An unverified report adds `(provisional)`.
- **Scope.** One line with the data flow in bold, then the kind, platform, and sync mode.
- **Claim.** The project's quoted local-first claim with its source, or a statement that none was found.
- **Eight criteria.** One paragraph each, in rubric order. A paragraph has the status symbol and word, the criterion title, one sentence of explanation, and a link to the cited lines. A link to the audited repository at another commit names that commit, for example `guide.md L4 at 0ec5a68736e3`.
- **Evidence.** The quoted source lines for each criterion in a code block.

The report closes with the rubric version and revision and a line with the version, maturity, commit, and verification.

| Symbol | Word |
| --- | --- |
| ✓ | Meets |
| ◐ | Partial |
| ✗ | Misses |
| – | Not applicable |
| ? | Unclear |

A status always appears as symbol and word together, because plain Markdown carries no color. The main report contains no tables.

A client that supports collapsible sections or color may fold each **Evidence** section or tint the status symbols. The plain report stays complete without them.

## Examples

- [Database with one data flow](../assets/example.report.md), rendered from the [example audit](../assets/example.audit.json).
- [Application with two data flows](../assets/example-application.report.md), where records and attachments reach different categories.
