# Kuku 0.6.0

## Marketed as local-first

**Markdown notes** · application · macOS desktop · Built-in Kuku Sync with sync enabled for the vault

Claims local-first: “A local-first Markdown knowledge workspace for macOS.” [README.md L10](https://github.com/kuku-mom/kuku/blob/c690bb6e952472c788acb7e3ae948c84b03f2268/README.md#L10)

✓ **Meets: Durable offline reads and writes.** The vault reads note text from local files and writes note changes to the local filesystem. [commands.rs L325-L335](https://github.com/kuku-mom/kuku/blob/c690bb6e952472c788acb7e3ae948c84b03f2268/apps/desktop/src-tauri/src/vault/commands.rs#L325-L335)

✗ **Misses: Device authority.** The server rejects publication when the client's expected head differs from the stored workspace head. [commit.go L120-L126](https://github.com/kuku-mom/kuku/blob/c690bb6e952472c788acb7e3ae948c84b03f2268/apps/server/internal/sync/commit.go#L120-L126)

? **Unclear: Complete change history.** The server inventories history older than a checkpoint, while the reviewed code does not establish preservation of every local edit. [gc.go L123-L130](https://github.com/kuku-mom/kuku/blob/c690bb6e952472c788acb7e3ae948c84b03f2268/apps/server/internal/sync/gc.go#L123-L130)

◐ **Partial: Replaceable sync infrastructure.** Self-hosted deployments are documented, while the reviewed instructions do not establish a lossless provider switch. [development.md L88-L94](https://github.com/kuku-mom/kuku/blob/c690bb6e952472c788acb7e3ae948c84b03f2268/docs/development.md#L88-L94)

✓ **Meets: Mandatory end-to-end encryption.** Sync packs are encrypted on the client with a key derived from the workspace key. [packer.rs L62-L70](https://github.com/kuku-mom/kuku/blob/c690bb6e952472c788acb7e3ae948c84b03f2268/apps/desktop/src-tauri/src/sync/packer.rs#L62-L70)

✗ **Misses: Quantum-resistant protection.** The server uses Ed25519 to verify commits for this sync flow. [commit.go L146-L148](https://github.com/kuku-mom/kuku/blob/c690bb6e952472c788acb7e3ae948c84b03f2268/apps/server/internal/sync/commit.go#L146-L148)

✗ **Misses: Device-held identity keys.** The server checks active device access in the context of the authenticated user account. [commit.go L129-L136](https://github.com/kuku-mom/kuku/blob/c690bb6e952472c788acb7e3ae948c84b03f2268/apps/server/internal/sync/commit.go#L129-L136)

✓ **Meets: Open-source client and required server.** The repository containing the desktop client and server carries the MIT license. [LICENSE L1-L3](https://github.com/kuku-mom/kuku/blob/c690bb6e952472c788acb7e3ae948c84b03f2268/LICENSE#L1-L3)

### Evidence

**Durable offline reads and writes** · [commands.rs L325-L335](https://github.com/kuku-mom/kuku/blob/c690bb6e952472c788acb7e3ae948c84b03f2268/apps/desktop/src-tauri/src/vault/commands.rs#L325-L335)

```text
    let root = get_vault_root(&state)?;
    let resolved = resolve_vault_path_strict(&root, &path).await?;
    let mutation = state.expected_mutations.record_write(&path, false);
    if let Some(parent) = resolved.parent()
        && let Err(error) = tokio::fs::create_dir_all(parent).await
    {
        state.expected_mutations.cancel(mutation);
        return Err(error.to_string());
    }
    if let Err(error) = tokio::fs::write(&resolved, &content).await {
        state.expected_mutations.cancel(mutation);
```

**Device authority** · [commit.go L120-L126](https://github.com/kuku-mom/kuku/blob/c690bb6e952472c788acb7e3ae948c84b03f2268/apps/server/internal/sync/commit.go#L120-L126)

```text
		currentHead := textValue(workspace.CurrentHeadCommitID)
		if currentHead != normalized.ExpectedHeadCommitID {
			return &HeadConflictError{
				WorkspaceID:   normalized.WorkspaceID.String(),
				CurrentHeadID: currentHead,
				HeadVersion:   workspace.HeadVersion,
			}
```

**Complete change history** · [gc.go L123-L130](https://github.com/kuku-mom/kuku/blob/c690bb6e952472c788acb7e3ae948c84b03f2268/apps/server/internal/sync/gc.go#L123-L130)

```text
		graph := buildReachableObjectGraph(workspace, commits, commitObjects)
		report.LatestCheckpoint = graph.LatestCheckpoint
		report.HasLatestCheckpoint = graph.HasLatestCheckpoint
		report.ReachableCommitCount = len(graph.CommitIDs)
		report.ReachableObjectCount = len(graph.ObjectIDs)
		report.PreservedCommitCount = len(graph.PreservedCommitIDs)
		report.PreservedObjectCount = len(graph.PreservedObjectIDs)
		report.OldReachableHistoryCandidates = graph.OldReachableHistoryCommits
```

**Replaceable sync infrastructure** · [development.md L88-L94](https://github.com/kuku-mom/kuku/blob/c690bb6e952472c788acb7e3ae948c84b03f2268/docs/development.md#L88-L94)

```text
## Self-Hosting References

Kuku's server is built with Go + Postgres and ships with Docker Compose configurations. Use these as starting points for your own deployment rather than assuming they are the only supported topology.

- `infra/docker/local`: local development with web + server + postgres + mailpit
- `infra/docker/preview`: preview environment
- `infra/docker/prod`: production API server behind Cloudflare Tunnel
```

**Mandatory end-to-end encryption** · [packer.rs L62-L70](https://github.com/kuku-mom/kuku/blob/c690bb6e952472c788acb7e3ae948c84b03f2268/apps/desktop/src-tauri/src/sync/packer.rs#L62-L70)

```text
    let pack = create_plain_pack(object_id, entries)?;
    let compressed = zstd::stream::encode_all(Cursor::new(pack), 0)?;
    let key = object_key(workspace_key, workspace_id, object_kind)?;
    let aad = PackAad::new(workspace_id, object_id, object_kind, commit_id);
    let blob = encrypt_blob(&key, &aad, &compressed)?;
    Ok(EncryptedPack {
        object_id: object_id.into(),
        metadata: encrypted_blob_metadata(&blob),
        blob,
```

**Quantum-resistant protection** · [commit.go L146-L148](https://github.com/kuku-mom/kuku/blob/c690bb6e952472c788acb7e3ae948c84b03f2268/apps/server/internal/sync/commit.go#L146-L148)

```text
		if !ed25519.Verify(ed25519.PublicKey(device.SigningPublicKey), canonicalPayload, normalized.Signature) {
			return ErrInvalidSignature
		}
```

**Device-held identity keys** · [commit.go L129-L136](https://github.com/kuku-mom/kuku/blob/c690bb6e952472c788acb7e3ae948c84b03f2268/apps/server/internal/sync/commit.go#L129-L136)

```text
		device, err := q.GetActiveSyncDeviceForUpdate(ctx, sqlc.GetActiveSyncDeviceForUpdateParams{
			WorkspaceID: normalized.WorkspaceID,
			ID:          normalized.AuthorDeviceID,
			UserID:      userID,
		})
		if errors.Is(err, pgx.ErrNoRows) {
			return ErrPermissionDenied
		}
```

**Open-source client and required server** · [LICENSE L1-L3](https://github.com/kuku-mom/kuku/blob/c690bb6e952472c788acb7e3ae948c84b03f2268/LICENSE#L1-L3)

```text
MIT License

Copyright (c) 2026 kuku-mom
```

## Marketed as local-first

**PNG vault files** · application · macOS desktop · Built-in Kuku Sync with sync enabled for the vault

Claims local-first: “A local-first Markdown knowledge workspace for macOS.” [README.md L10](https://github.com/kuku-mom/kuku/blob/c690bb6e952472c788acb7e3ae948c84b03f2268/README.md#L10)

✓ **Meets: Durable offline reads and writes.** The binary vault API reads and writes file bytes directly on the local filesystem. [commands.rs L346-L370](https://github.com/kuku-mom/kuku/blob/c690bb6e952472c788acb7e3ae948c84b03f2268/apps/desktop/src-tauri/src/vault/commands.rs#L346-L370)

✗ **Misses: Device authority.** PNG bytes stay in the local vault and are excluded from the device merge path. [scanner.rs L124-L128](https://github.com/kuku-mom/kuku/blob/c690bb6e952472c788acb7e3ae948c84b03f2268/apps/desktop/src-tauri/src/sync/scanner.rs#L124-L128)

✗ **Misses: Complete change history.** The sync scanner excludes these files, which have no change history in the sync protocol. [scanner.rs L124-L128](https://github.com/kuku-mom/kuku/blob/c690bb6e952472c788acb7e3ae948c84b03f2268/apps/desktop/src-tauri/src/sync/scanner.rs#L124-L128)

✗ **Misses: Replaceable sync infrastructure.** The built-in sync client sends these file bytes to none of its compatible servers. [scanner.rs L124-L128](https://github.com/kuku-mom/kuku/blob/c690bb6e952472c788acb7e3ae948c84b03f2268/apps/desktop/src-tauri/src/sync/scanner.rs#L124-L128)

✗ **Misses: Mandatory end-to-end encryption.** The built-in end-to-end encrypted sync path excludes the PNG bytes. [scanner.rs L124-L128](https://github.com/kuku-mom/kuku/blob/c690bb6e952472c788acb7e3ae948c84b03f2268/apps/desktop/src-tauri/src/sync/scanner.rs#L124-L128)

✗ **Misses: Quantum-resistant protection.** The built-in sync path excludes these bytes and provides no post-quantum protection for their transfer. [scanner.rs L124-L128](https://github.com/kuku-mom/kuku/blob/c690bb6e952472c788acb7e3ae948c84b03f2268/apps/desktop/src-tauri/src/sync/scanner.rs#L124-L128)

? **Unclear: Device-held identity keys.** The exclusion establishes that the file stays out of sync, while it does not show how cryptographic identity applies to this file flow. [scanner.rs L124-L128](https://github.com/kuku-mom/kuku/blob/c690bb6e952472c788acb7e3ae948c84b03f2268/apps/desktop/src-tauri/src/sync/scanner.rs#L124-L128)

✓ **Meets: Open-source client and required server.** The repository containing the desktop client and server carries the MIT license. [LICENSE L1-L3](https://github.com/kuku-mom/kuku/blob/c690bb6e952472c788acb7e3ae948c84b03f2268/LICENSE#L1-L3)

### Evidence

**Durable offline reads and writes** · [commands.rs L346-L370](https://github.com/kuku-mom/kuku/blob/c690bb6e952472c788acb7e3ae948c84b03f2268/apps/desktop/src-tauri/src/vault/commands.rs#L346-L370)

```text
pub async fn vault_read_binary(
    state: State<'_, VaultState>,
    path: String,
) -> Result<Vec<u8>, String> {
    let root = get_vault_root(&state)?;
    let resolved = resolve_vault_path_strict(&root, &path).await?;
    tokio::fs::read(&resolved).await.map_err(|e| e.to_string())
}

#[command]
pub async fn vault_write_binary(
    state: State<'_, VaultState>,
    path: String,
    data: Vec<u8>,
) -> Result<(), String> {
    let root = get_vault_root(&state)?;
    let resolved = resolve_vault_path_strict(&root, &path).await?;
    if let Some(parent) = resolved.parent() {
        tokio::fs::create_dir_all(parent)
            .await
            .map_err(|e| e.to_string())?;
    }
    tokio::fs::write(&resolved, &data)
        .await
        .map_err(|e| e.to_string())
```

**Device authority** · [scanner.rs L124-L128](https://github.com/kuku-mom/kuku/blob/c690bb6e952472c788acb7e3ae948c84b03f2268/apps/desktop/src-tauri/src/sync/scanner.rs#L124-L128)

```text
        if !file_type.is_file() || !is_markdown_path(&path) {
            continue;
        }

        files.push(scan_file(root, &path)?);
```

**Complete change history** · [scanner.rs L124-L128](https://github.com/kuku-mom/kuku/blob/c690bb6e952472c788acb7e3ae948c84b03f2268/apps/desktop/src-tauri/src/sync/scanner.rs#L124-L128)

```text
        if !file_type.is_file() || !is_markdown_path(&path) {
            continue;
        }

        files.push(scan_file(root, &path)?);
```

**Replaceable sync infrastructure** · [scanner.rs L124-L128](https://github.com/kuku-mom/kuku/blob/c690bb6e952472c788acb7e3ae948c84b03f2268/apps/desktop/src-tauri/src/sync/scanner.rs#L124-L128)

```text
        if !file_type.is_file() || !is_markdown_path(&path) {
            continue;
        }

        files.push(scan_file(root, &path)?);
```

**Mandatory end-to-end encryption** · [scanner.rs L124-L128](https://github.com/kuku-mom/kuku/blob/c690bb6e952472c788acb7e3ae948c84b03f2268/apps/desktop/src-tauri/src/sync/scanner.rs#L124-L128)

```text
        if !file_type.is_file() || !is_markdown_path(&path) {
            continue;
        }

        files.push(scan_file(root, &path)?);
```

**Quantum-resistant protection** · [scanner.rs L124-L128](https://github.com/kuku-mom/kuku/blob/c690bb6e952472c788acb7e3ae948c84b03f2268/apps/desktop/src-tauri/src/sync/scanner.rs#L124-L128)

```text
        if !file_type.is_file() || !is_markdown_path(&path) {
            continue;
        }

        files.push(scan_file(root, &path)?);
```

**Device-held identity keys** · [scanner.rs L124-L128](https://github.com/kuku-mom/kuku/blob/c690bb6e952472c788acb7e3ae948c84b03f2268/apps/desktop/src-tauri/src/sync/scanner.rs#L124-L128)

```text
        if !file_type.is_file() || !is_markdown_path(&path) {
            continue;
        }

        files.push(scan_file(root, &path)?);
```

**Open-source client and required server** · [LICENSE L1-L3](https://github.com/kuku-mom/kuku/blob/c690bb6e952472c788acb7e3ae948c84b03f2268/LICENSE#L1-L3)

```text
MIT License

Copyright (c) 2026 kuku-mom
```

Rated against the [Evolu criteria](https://www.evolu.dev/docs/comparison) · rubric `4eedb2272841` adopted 2026-11-27

Version 0.6.0 · unclear · commit `c690bb6e9524` · static audit · citations machine-verified
