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

## Runtime receipts and dirty workspaces

Each parse/read invocation (including resumes) keeps an immutable directory at
`<output>/_runtime/provenance/<invocation_id>/`. It contains `invocation.json`, an
append-only `requests.jsonl` and the first complete logical request for each node.
Full messages, fixed examples, template values, tool schemas/choice, tool history and
repair instructions enter `request_sha256` before the provider call; this identifies
the provider-neutral input, not provider-specific HTTP encoding. Generation settings
remain in the existing allowlisted model/sampling receipt. No provider configuration,
headers, API keys or environment variables are included in the sample.

Standard success/error traces and run configuration link request hashes and invocation
IDs, without requiring debug mode. `prompt_releases` records the separate stable
`release_sha256` (version files, resolved fixed text including few-shot, dependencies).
Actual request hashes vary with book/source/context; a release hash does not.

At every invocation start, a dirty workspace saves `git diff --binary HEAD` as
`workspace.patch`, including staged and unstaged tracked changes across the repository.
The receipt binds the patch hash and base commit. Untracked nonignored files are listed
with hashes, not copied; `reproduction_complete=false` explicitly marks that limitation.
Ignored private assets are covered separately by release hashes. Patches and raw model
inputs are always ignored and must be retained privately with the run. The event stream
and invocation directories preserve earlier resume receipts after the current
`run_configuration.json` advances. No historical patch is fabricated for Q1.
