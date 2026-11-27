# Resolve an audit input

The first result is a project identity and an immutable source revision. The sample inputs below illustrate the resolution step.

| Input | Example | Expected resolution |
| --- | --- | --- |
| Name | `Kuku Markdown workspace` | Find the official project site and confirm its repository is `kuku-mom/kuku`. Resolve the latest public release. |
| Product site or docs | `https://www.evolu.dev/docs/sync` | Follow Evolu's source link to `evoluhq/evolu`. Scope the audit to the documented platform or component. |
| Release link | `https://github.com/kuku-mom/kuku/releases/tag/0.6.0` | Use Kuku 0.6.0 and resolve the tag, including an annotated tag's target, to its commit. |
| GitHub repository | `https://github.com/kuku-mom/kuku` | Verify the repository and resolve its latest public release. |
| GitLab repository | `https://gitlab.com/example/subgroup/project` | Keep the full group path. Resolve the release and use GitLab's `/-/blob/<commit>/...` permalinks. |
| Codeberg repository | `https://codeberg.org/example/project` | Resolve the release from that repository and use its `/src/commit/<commit>/...` permalinks. |
| Self-hosted Forgejo | `https://forge.example.org/team/project` | Resolve the revision using the supplied forge. Validate from a local clone or allow that host explicitly for HTTPS validation. |
| Tag | `kuku-mom/kuku @ 0.6.0` | Resolve the tag in the named repository. For a tag alone, use the repository already established in the conversation or ask for it. |
| Commit | `kuku-mom/kuku @ c690bb6` | Confirm the prefix uniquely resolves in that repository and record `c690bb6e952472c788acb7e3ae948c84b03f2268`. |
| Local checkout | `/work/kuku` | Identify the repository from its remote and inspect `HEAD` when no revision is supplied. Use committed Git objects for evidence. |

For a local checkout, `git -C /path/to/clone rev-parse --verify HEAD^{commit}` reports the committed snapshot. A dirty worktree may contain material outside that revision. With an explicit tag or commit, verify and inspect that object directly. If a clone has no remote, use a canonical URL supplied or verified for the same project before constructing source permalinks.

Examples for GitLab, Codeberg, and self-hosted Forgejo use illustrative repository names. If an input cannot be resolved to one project and revision, explain the gap in the report.
