<!-- Generated from assets/rubric.json by scripts/check_rubric.py --write. -->
# Local-first rubric

Based on [Evolu’s comparison](https://www.evolu.dev/docs/comparison) at commit
`4eedb2272841bdeb2d7c3387784ba157d2f33f1c` (2026-11-21).
Adopted on 2026-11-27. Evolu checked the comparison on 2026-11-20.

The definitions below paraphrase Evolu’s criteria and rating rules.
[Rating rules](https://github.com/evoluhq/evolu/blob/4eedb2272841bdeb2d7c3387784ba157d2f33f1c/.agents/skills/comparison-update/SKILL.md) · [Category code](https://github.com/evoluhq/evolu/blob/4eedb2272841bdeb2d7c3387784ba157d2f33f1c/apps/web/src/comparison/comparison.ts) · [Comparison data](https://github.com/evoluhq/evolu/blob/4eedb2272841bdeb2d7c3387784ba157d2f33f1c/apps/web/src/comparison/comparison.json) · [Evolu repository license (MIT)](https://github.com/evoluhq/evolu/blob/4eedb2272841bdeb2d7c3387784ba157d2f33f1c/LICENSE)

## Criteria

### 1. Durable offline reads and writes (`offline`)

Without a network, the default configuration accepts reads and writes and preserves data across restarts.

Opt-in persistence or offline changes held only in memory are partial. Refusing offline writes misses the criterion.

### 2. Device authority (`devicePrimary`)

Each device merges its own state and determines which changes stand.

Server ordering, rollback after server rejection, and replacement by server state miss. A relay that can refuse to forward a change can still meet this criterion if the device keeps the change.

### 3. Complete change history (`fullHistory`)

The system keeps changes even after later writes replace their values, so devices can merge after long disconnections.

Default pruning, compaction, garbage collection, or snapshot bootstrap misses when it discards overwritten changes.

### 4. Replaceable sync infrastructure (`anyServer`)

Peers can synchronize directly or use interchangeable servers, including a self-hosted one.

For server-based sync, verify that switching providers preserves user data.

### 5. Mandatory end-to-end encryption (`e2ee`)

Sync servers lack the keys to read user data, and the product provides no way to disable that protection.

Optional built-in protection is partial. Encryption that the application developer must implement through a hook, transformer, or other extension misses.

### 6. Quantum-resistant protection (`postQuantum`)

Protection covers both the exchange of data keys and stored signatures used to authorize access or authenticate changes.

Key exchange or wrapping that depends on classical public-key security, for example X25519 or RSA alone, and classical stored signatures, for example Ed25519 or ECDSA, miss. Examples that can meet the rule include ML-KEM, X-Wing or PQXDH for key exchange, ML-DSA or SLH-DSA for signatures, and symmetric keys that never travel over public-key cryptography. Without end-to-end encryption this misses. If end-to-end encryption is optional, assess that mode and use partial if it otherwise meets.

### 7. Device-held identity keys (`keysNotAccounts`)

Keys on the device establish identity and access. A provider account can handle billing separately.

Use n/a only when the tool has no concept of users.

### 8. Open-source client and required server (`openSource`)

Both the client and every server component the tool requires are available under OSI-approved licenses.

Client-only open source is partial if a proprietary server is required. An OSI-licensed client suffices when the tool requires no server of its own or just runs in the application's backend.

## Ratings

- ✓ `meets`. The feature applies by default and in every applicable case. Passes.
- ◐ `partial`. The feature covers only some cases or is optional, experimental, unfinished, or enterprise-only. Fails the all-criteria check.
- ✗ `misses`. Primary evidence shows that the criterion fails. Fails the all-criteria check.
- – `n/a`. The tool has no users, so there is no user identity or account authority to assess. Passes. Allowed only for `keysNotAccounts`.
- ? `unclear`. Available primary evidence leaves the criterion unresolved. Fails the all-criteria check.

## Evidence, claim, and maturity

- Record one sentence of evidence and a primary source for every rating. Use an absolute HTTPS URL for the relevant code lines, first-party documentation, a release, or repository metadata. Prefer commit permalinks for code.
- Use a verbatim first-party quote containing a spelling of local-first as the claim. Preserve its source and add an English translation if needed. Package keywords alone are insufficient. Use null when the authors make no such claim.
- Record maturity from the authors, separately from criterion ratings. Map preview to beta, pre-alpha or work in progress to experimental, and general availability to stable. With no author label, use stable for a release at or above 1.0 and unclear otherwise. Use maintenance for a tool the authors still fix while developing features elsewhere. Explicitly announced maintenance mode belongs in Evolu's discontinued list.
- Use the version listed as latest by the primary package registry or release page, without a leading v. For an audit scoped to a newer major available only as a prerelease, use that major's newest prerelease.

Maturity labels are `stable`, `beta`, `alpha`, `experimental`, `maintenance`, `unclear`, `pre-1.0`.

## Category

1. If every criterion passes, assign **Local-first**. Assign **Not local-first yet** when maturity is one of `alpha`, `experimental`, `pre-1.0`, or the release has major version 0 or is a prerelease of 1.0.0. A missing version uses the recorded maturity.
2. Otherwise, if the project claims local-first, assign **Not local-first yet** when all of these checks pass (`offline` in `meets`, `devicePrimary` in `meets` or `partial` or `unclear`, `e2ee` in `meets` or `partial` or `unclear`, `openSource` in `meets`). Otherwise assign **Marketed as local-first**.
3. Otherwise, if the project makes no local-first claim, assign **Offline-first** when all of these checks pass (`offline` in `meets`). Otherwise assign **Sync engine**.

## Worked examples

Criteria start as `meets` except for the overrides shown.

| Example | Claim | Maturity | Version | Overrides | Category |
| --- | --- | --- | --- | --- | --- |
| All criteria pass, no claim | No | `stable` | 1.0.0 | — | Local-first |
| All criteria pass before 1.0 | No | `stable` | 0.9.0 | — | Not local-first yet |
| First stable release is still a prerelease | Yes | `stable` | 1.0.0-rc.1 | — | Not local-first yet |
| Current release is labelled alpha | Yes | `alpha` | 2.1.0 | — | Not local-first yet |
| Claim with server authority | Yes | `stable` | 1.2.0 | `devicePrimary=misses` | Marketed as local-first |
| Offline by default, no claim | No | `stable` | 1.2.0 | `fullHistory=misses` | Offline-first |
| Optional offline support, no claim | No | `stable` | 1.2.0 | `offline=partial` | Sync engine |
| Criterion 7 has no users | Yes | `stable` | 1.2.0 | `keysNotAccounts=n/a` | Local-first |
| Criterion 5 is unclear and the tool claims local-first | Yes | `stable` | 1.2.0 | `e2ee=unclear` | Not local-first yet |
| Criterion 5 explicitly fails and the tool claims local-first | Yes | `stable` | 1.2.0 | `e2ee=misses` | Marketed as local-first |

## Applications

- Identify the audited product version, platform, data flow, and sync mode. Include any setting or provider choice that changes how data moves.
- Rate each user-data flow on its own. For example, trace notes and attachments separately from device writes through the sync queue, merge, server storage, encryption keys, and recovery.
- Report practical behavior separately, including access without an account, use of data in another program, and availability during a provider outage. These findings do not enter the category calculation.
- The policy for an overall application category and the requirement to audit a separate sync-disabled configuration are open.

## Calibration targets

These are expected categories from the pinned Evolu comparison.

| Tool | Version in the source | Expected category |
| --- | --- | --- |
| Evolu | — | Local-first |
| Automerge | 3.5.0 | Not local-first yet |
| PowerSync | 1.29.1 | Marketed as local-first |
| PouchDB | 9.0.0 | Offline-first |
| Hocuspocus | 4.7.1 | Sync engine |
