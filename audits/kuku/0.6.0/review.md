# Second review of the Kuku 0.6.0 audits

A second agent read every citation in [markdown-notes.audit.json](markdown-notes.audit.json) and [png-vault-files.audit.json](png-vault-files.audit.json) in the Kuku repository at commit `c690bb6e952472c788acb7e3ae948c84b03f2268` and checked whether the cited lines support the rating. The audits were written by Codex on 2026-11-27. Claude Code reviewed them the same day. Both audits pass the validator against a local clone of the tag.

The review confirmed 15 of 16 ratings. One rating is contested and waits for the project owner. One rating was changed afterwards under rubric revision 2 and has no independent review yet.

## Markdown notes

| Criterion | Rating | Review |
| --- | --- | --- |
| Durable offline reads and writes | Meets | Confirmed. The cited command writes note text to the local vault. |
| Device authority | Misses | Confirmed. The server accepts a commit only when the client's expected head equals the stored workspace head, so the server orders writes. |
| Complete change history | Unclear | Confirmed. In this release the server deletes only expired orphan objects ([gc.go L132-L141](https://github.com/kuku-mom/kuku/blob/c690bb6e952472c788acb7e3ae948c84b03f2268/apps/server/internal/sync/gc.go#L132-L141)) and reports older reachable history as candidates. The code read does not show that every local edit becomes a commit. |
| Replaceable sync infrastructure | Partial | Contested. The desktop client takes its server address at build time ([config.rs L1-L7](https://github.com/kuku-mom/kuku/blob/c690bb6e952472c788acb7e3ae948c84b03f2268/apps/desktop/src-tauri/src/config.rs#L1-L7)), so the released app cannot switch to a self-hosted server. The reviewer reads this as `misses` for the released build. The category stays the same either way. |
| Mandatory end-to-end encryption | Meets | Confirmed for the cited path. The client encrypts sync packs with a key derived from the workspace key. The review found no setting that turns encryption off and did not prove that none exists. |
| Quantum-resistant protection | Misses | Confirmed. Commits are verified with Ed25519 signatures. |
| Device-held identity keys | Misses | Confirmed. The server looks up the device inside the authenticated user account. |
| Open-source client and required server | Meets | Confirmed. The repository with the client and the server carries the MIT license. |

## PNG vault files

| Criterion | Rating | Review |
| --- | --- | --- |
| Durable offline reads and writes | Meets | Confirmed. The binary vault commands read and write bytes on the local filesystem. |
| Device authority, change history, sync infrastructure, encryption, quantum resistance | Misses | Confirmed. The cited scanner lines show that only Markdown files enter sync. Rubric revision 2 rates criteria 2 to 6 of an excluded flow as `misses` on that evidence. |
| Device-held identity keys | Misses (was Unclear) | Changed by the reviewer on 2026-11-27. Rubric revision 2 gives a flow excluded from sync the rating of the product's sync identity model, which the Markdown audit rates as `misses` from the same server check. The original `unclear` was confirmed under revision 1. |
| Open-source client and required server | Meets | Confirmed. |

An independent audit of the same flow, run in OpenCode with a different model, reached the same eight ratings and the same category from other line ranges in `scanner.rs` and `applier.rs`.

## Result

Both flows are `Marketed as local-first` for Kuku 0.6.0 on macOS with built-in sync enabled. PNG files in the vault do not reach a second device through Kuku sync. The [rendered report](report.md) comes from `audit.py render`.

Open points: the contested rating above waits for the owner, and the changed identity rating of the PNG flow needs a second reviewer.
