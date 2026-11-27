# Example Records 1.2.0

## Local-first

**records** · application · macOS desktop · default relay synchronization

Claims local-first: “local-first database” [README.md L1](https://github.com/example/is-local-first-audit-fixture/blob/705c2fa1357119e6910de4386eea2cadc8627d0e/README.md#L1)

✓ **Meets: Durable offline reads and writes.** The default configuration persists offline reads and writes across restarts. [README.md L2](https://github.com/example/is-local-first-audit-fixture/blob/705c2fa1357119e6910de4386eea2cadc8627d0e/README.md#L2)

✓ **Meets: Device authority.** Devices merge their state locally. [README.md L3](https://github.com/example/is-local-first-audit-fixture/blob/705c2fa1357119e6910de4386eea2cadc8627d0e/README.md#L3)

✓ **Meets: Complete change history.** Overwritten changes remain in the record history. [README.md L4](https://github.com/example/is-local-first-audit-fixture/blob/705c2fa1357119e6910de4386eea2cadc8627d0e/README.md#L4)

✓ **Meets: Replaceable sync infrastructure.** The user can select a compatible relay or self-host one. [README.md L5](https://github.com/example/is-local-first-audit-fixture/blob/705c2fa1357119e6910de4386eea2cadc8627d0e/README.md#L5)

✓ **Meets: Mandatory end-to-end encryption.** All synced record contents are encrypted end to end. [README.md L6](https://github.com/example/is-local-first-audit-fixture/blob/705c2fa1357119e6910de4386eea2cadc8627d0e/README.md#L6)

✓ **Meets: Quantum-resistant protection.** Key exchange and signatures use post-quantum schemes. [README.md L7](https://github.com/example/is-local-first-audit-fixture/blob/705c2fa1357119e6910de4386eea2cadc8627d0e/README.md#L7)

– **Not applicable: Device-held identity keys.** The library has no concept of users. [README.md L8](https://github.com/example/is-local-first-audit-fixture/blob/705c2fa1357119e6910de4386eea2cadc8627d0e/README.md#L8)

✓ **Meets: Open-source client and required server.** The client and required relay are MIT licensed. [README.md L9](https://github.com/example/is-local-first-audit-fixture/blob/705c2fa1357119e6910de4386eea2cadc8627d0e/README.md#L9)

### Evidence

**Durable offline reads and writes** · [README.md L2](https://github.com/example/is-local-first-audit-fixture/blob/705c2fa1357119e6910de4386eea2cadc8627d0e/README.md#L2)

```text
Records can be read and written offline. Changes survive a restart with default settings.
```

**Device authority** · [README.md L3](https://github.com/example/is-local-first-audit-fixture/blob/705c2fa1357119e6910de4386eea2cadc8627d0e/README.md#L3)

```text
Every device merges its own copy.
```

**Complete change history** · [README.md L4](https://github.com/example/is-local-first-audit-fixture/blob/705c2fa1357119e6910de4386eea2cadc8627d0e/README.md#L4)

```text
All prior record changes are retained.
```

**Replaceable sync infrastructure** · [README.md L5](https://github.com/example/is-local-first-audit-fixture/blob/705c2fa1357119e6910de4386eea2cadc8627d0e/README.md#L5)

```text
Clients can use any compatible relay, including a self-hosted relay.
```

**Mandatory end-to-end encryption** · [README.md L6](https://github.com/example/is-local-first-audit-fixture/blob/705c2fa1357119e6910de4386eea2cadc8627d0e/README.md#L6)

```text
Every synced record is end-to-end encrypted by default. No option disables encryption.
```

**Quantum-resistant protection** · [README.md L7](https://github.com/example/is-local-first-audit-fixture/blob/705c2fa1357119e6910de4386eea2cadc8627d0e/README.md#L7)

```text
Synced keys are exchanged using ML-KEM and changes are signed with ML-DSA.
```

**Device-held identity keys** · [README.md L8](https://github.com/example/is-local-first-audit-fixture/blob/705c2fa1357119e6910de4386eea2cadc8627d0e/README.md#L8)

```text
This library has no concept of user identities.
```

**Open-source client and required server** · [README.md L9](https://github.com/example/is-local-first-audit-fixture/blob/705c2fa1357119e6910de4386eea2cadc8627d0e/README.md#L9)

```text
The client and relay are released under the MIT license.
```

## Not local-first yet

**attachments** · application · macOS desktop · default relay synchronization

Claims local-first: “local-first database” [README.md L1](https://github.com/example/is-local-first-audit-fixture/blob/705c2fa1357119e6910de4386eea2cadc8627d0e/README.md#L1)

✓ **Meets: Durable offline reads and writes.** Attachments are stored as records, so they stay readable and writable offline. [README.md L2](https://github.com/example/is-local-first-audit-fixture/blob/705c2fa1357119e6910de4386eea2cadc8627d0e/README.md#L2)

✓ **Meets: Device authority.** Devices merge their state locally. [README.md L3](https://github.com/example/is-local-first-audit-fixture/blob/705c2fa1357119e6910de4386eea2cadc8627d0e/README.md#L3)

? **Unclear: Complete change history.** The cited statement covers records. Retention of replaced attachment contents is not documented. [README.md L4](https://github.com/example/is-local-first-audit-fixture/blob/705c2fa1357119e6910de4386eea2cadc8627d0e/README.md#L4)

✓ **Meets: Replaceable sync infrastructure.** The user can select a compatible relay or self-host one. [README.md L5](https://github.com/example/is-local-first-audit-fixture/blob/705c2fa1357119e6910de4386eea2cadc8627d0e/README.md#L5)

◐ **Partial: Mandatory end-to-end encryption.** Record contents are encrypted. Attachment file names are not covered by the cited guarantee. [README.md L6](https://github.com/example/is-local-first-audit-fixture/blob/705c2fa1357119e6910de4386eea2cadc8627d0e/README.md#L6)

✓ **Meets: Quantum-resistant protection.** Key exchange and signatures use post-quantum schemes. [README.md L7](https://github.com/example/is-local-first-audit-fixture/blob/705c2fa1357119e6910de4386eea2cadc8627d0e/README.md#L7)

– **Not applicable: Device-held identity keys.** The library has no concept of users. [README.md L8](https://github.com/example/is-local-first-audit-fixture/blob/705c2fa1357119e6910de4386eea2cadc8627d0e/README.md#L8)

✓ **Meets: Open-source client and required server.** The client and required relay are MIT licensed. [README.md L9](https://github.com/example/is-local-first-audit-fixture/blob/705c2fa1357119e6910de4386eea2cadc8627d0e/README.md#L9)

### Evidence

**Durable offline reads and writes** · [README.md L2](https://github.com/example/is-local-first-audit-fixture/blob/705c2fa1357119e6910de4386eea2cadc8627d0e/README.md#L2)

```text
Records can be read and written offline. Changes survive a restart with default settings.
```

**Device authority** · [README.md L3](https://github.com/example/is-local-first-audit-fixture/blob/705c2fa1357119e6910de4386eea2cadc8627d0e/README.md#L3)

```text
Every device merges its own copy.
```

**Complete change history** · [README.md L4](https://github.com/example/is-local-first-audit-fixture/blob/705c2fa1357119e6910de4386eea2cadc8627d0e/README.md#L4)

```text
All prior record changes are retained.
```

**Replaceable sync infrastructure** · [README.md L5](https://github.com/example/is-local-first-audit-fixture/blob/705c2fa1357119e6910de4386eea2cadc8627d0e/README.md#L5)

```text
Clients can use any compatible relay, including a self-hosted relay.
```

**Mandatory end-to-end encryption** · [README.md L6](https://github.com/example/is-local-first-audit-fixture/blob/705c2fa1357119e6910de4386eea2cadc8627d0e/README.md#L6)

```text
Every synced record is end-to-end encrypted by default. No option disables encryption.
```

**Quantum-resistant protection** · [README.md L7](https://github.com/example/is-local-first-audit-fixture/blob/705c2fa1357119e6910de4386eea2cadc8627d0e/README.md#L7)

```text
Synced keys are exchanged using ML-KEM and changes are signed with ML-DSA.
```

**Device-held identity keys** · [README.md L8](https://github.com/example/is-local-first-audit-fixture/blob/705c2fa1357119e6910de4386eea2cadc8627d0e/README.md#L8)

```text
This library has no concept of user identities.
```

**Open-source client and required server** · [README.md L9](https://github.com/example/is-local-first-audit-fixture/blob/705c2fa1357119e6910de4386eea2cadc8627d0e/README.md#L9)

```text
The client and relay are released under the MIT license.
```

Rated against the [Evolu criteria](https://www.evolu.dev/docs/comparison) · rubric `4eedb2272841` revision 2, adopted 2026-11-27

Version 1.2.0 · stable · commit `705c2fa13571` · static audit · citations machine-verified
