# Q1 iteration provenance

## Published prompts

Runtime prompt text is loaded from `src/attentional_v2/prompts/versions/<family>/<version>.md`.
The exact text is between `<!-- prompt:key -->` and `<!-- /prompt -->`; the surrounding
newline is a delimiter, not prompt content. Python retains rendering logic, not a second
copy of these texts. Shared reader role and language rules are versioned dependencies.
`versions/published.json` binds each release to its dependency files and resolved text.
Never edit a published file or its lock entry. Copy to a new version and add a release.
When checking a branch, pass the trusted pre-change base commit to the checker so a
simultaneous edit to an old file and its lock cannot masquerade as a new release.

```sh
cd reading-companion-backend
.venv/bin/python scripts/check_prompt_releases.py --base-ref HEAD
.venv/bin/python -m pytest -q tests/test_prompt_releases.py
```

The migration fixture contains only nine complete prompt-pair SHA-256 values captured
before extraction. Acceptance compared the complete system/user strings byte for byte
across chapter classification, Digest languages/source shapes, and Ingest source shapes;
no model was called. Existing prompt/call contract tests remain applicable.

### Private few-shot assets

The original Digest examples (including quoted book passages) live only in ignored
`state/prompt_assets/<sha256>.txt`. Version files contain their SHA-256 references.
Restore exact assets from the operator's private copy/backup of that directory. No
external download or public distribution is configured. For this initial release only,
an existing local historical Git object also permits explicit offline recovery:

```sh
.venv/bin/python scripts/restore_private_prompt_assets.py --legacy-ref d414030c149bc56590bed890421eb59aad22aa05
.venv/bin/python scripts/check_prompt_releases.py
```

The recovery command verifies the expected content address before writing. It requires
that object to exist locally; a shallow clone without it needs the private backup.
It never fetches anything. Missing or mismatched assets raise a clear error while loading
the prompt module; a fresh checkout must provision these files before starting the API
or importing the reader in tests. There is no silent removal of examples or substitute
prompt. Existing Git history is retained; this task does not rewrite it. The original
few-shot file must be backed up privately alongside runtime artifacts.

Raw migration captures are ignored under `state/prompt_migration/`; tracked fixtures and
release records contain hashes only. Never commit rendered prompts or example bodies.
