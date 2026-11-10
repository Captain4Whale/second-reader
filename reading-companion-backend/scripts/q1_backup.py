"""Explicit local-only Q1 backup and independent restoration verification. No scheduler."""

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import shutil
import subprocess
import sys

BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))
from scripts.q1_private_snapshot import capture, fingerprint, inventory, verify  # noqa: E402


def backup(annotation_root, destination=None):
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    output = destination or Path.home() / "Backups/second-reader" / stamp
    work = BACKEND / "state/backup_verification" / stamp
    stage = work / "staging"
    payload = stage / "reading-companion-backend"
    payload.mkdir(parents=True, exist_ok=False)
    sources = {
        name: BACKEND / name
        for name in [
            "state/experiments/Q1-DIGEST-DIAG-001",
            "state/scorings",
            "state/q1_rubric_reviews/Q1-DIGEST-DIAG-001-q1-v0",
            "state/prompt_assets",
            "state/rubric_examples",
            "state/eval_local_datasets/q1_fullbooks_d414030_20261103",
        ]
    }
    # This source intentionally lives in the old annotation worktree. Never traverse
    # unrelated workspace links or configuration/credential directories.
    batch_ids = set()
    for name in ["dev-v1", "holdout-v1"]:
        manifest = json.loads(
            (BACKEND / f"experiments/unit-sets/{name}.json").read_bytes()
        )
        batch_ids.update(u["batch_id"] for u in manifest["units"])
    for batch_id in sorted(batch_ids):
        sources[f"state/q1_annotation/{batch_id}"] = annotation_root / batch_id
    inventories = {}
    for name, source in sources.items():
        inventories[name] = inventory(source)
        shutil.copytree(source.resolve(strict=True), payload / name, symlinks=True)
        if inventory(payload / name) != inventories[name]:
            raise ValueError("Staging copy mismatch")
    # Only tracked replay dependencies/configuration; no environment or credentials.
    tracked = subprocess.check_output(
        ["git", "-C", str(BACKEND.parent), "ls-files"], text=True
    ).splitlines()
    prefixes = [
        "experiments/",
        "rubric/",
        "scripts/",
        "src/reading_core/",
        "src/attentional_v2/prompts/versions/",
    ]
    metadata = {}
    for repo_name in tracked:
        prefix = "reading-companion-backend/"
        if not repo_name.startswith(prefix):
            continue
        name = repo_name[len(prefix) :]
        if not any(name.startswith(p) for p in prefixes):
            continue
        source = BACKEND / name
        if not source.is_file() or source.is_symlink():
            continue
        target = payload / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
        metadata[name] = fingerprint(source)
        if fingerprint(target) != metadata[name]:
            raise ValueError("Metadata copy mismatch")
    # Newly added verification commands in the current uncommitted final slice are
    # explicit, scoped additions rather than a recursive copy of untracked files.
    for name in [
        "scripts/q1_experiment_index.py",
        "scripts/q1_backup.py",
        "experiments/INDEX.md",
    ]:
        target = payload / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(BACKEND / name, target)
        metadata[name] = fingerprint(BACKEND / name)
    for name, source in sources.items():
        if inventory(source) != inventories[name]:
            raise ValueError("Source changed while staging; retry into a new snapshot")
    for name, h in metadata.items():
        if fingerprint(BACKEND / name) != h:
            raise ValueError("Metadata changed while staging")
    receipt = capture(stage, output)
    # Restore solely from the saved backup payload; never resolve live source paths.
    restore = work / "restore"
    capture(output / "files", restore)
    verify(output)
    verify(restore)
    restored = restore / "files/reading-companion-backend"
    parsed = 0
    for path in restored.rglob("*.jsonl"):
        raw = path.read_bytes()
        if raw and not raw.endswith(b"\n"):
            raise ValueError(f"Incomplete JSONL: {path}")
        for line in raw.splitlines():
            json.loads(line)
        parsed += 1
    commands = [
        ["scripts/q1_scoring.py", "--evidence", "--base-ref", "7c7ea08"],
        ["scripts/q1_experiment_index.py", "--check"],
    ]
    checks = []
    for command in commands:
        result = subprocess.run(
            [sys.executable, "-B", *command],
            cwd=restored,
            capture_output=True,
            text=True,
            check=True,
        )
        checks.append({"command": command, "output": result.stdout.strip()})
    verification = dict(
        schema="q1-backup-verification/1",
        created_at=datetime.now(timezone.utc).isoformat(),
        backup_path=str(output),
        restore_path=str(restored),
        backup_manifest_sha256=fingerprint(output / "manifest.json"),
        files=len(receipt["files"]),
        bytes=sum(x["bytes"] for x in receipt["files"].values()),
        jsonl_files_parsed=parsed,
        source_roots={k: str(v) for k, v in sources.items()},
        metadata_files=len(metadata),
        checks=checks,
        restored_inventory_matches_backup=inventory(restore / "files")
        == inventory(output / "files"),
        original_source_inventories_unchanged=all(
            inventory(v) == inventories[k] for k, v in sources.items()
        ),
    )
    if not verification["restored_inventory_matches_backup"]:
        raise ValueError("Restored inventory differs from backup")
    if not verification["original_source_inventories_unchanged"]:
        raise ValueError("Source changed during backup verification")
    for path in [output / "verification.json", work / "verification.json"]:
        with path.open("x") as f:
            json.dump(verification, f, ensure_ascii=False, indent=2)
            f.write("\n")
    print(json.dumps(verification, ensure_ascii=False, indent=2))
    return verification


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--annotation-root", type=Path, required=True)
    p.add_argument("--destination", type=Path)
    args = p.parse_args()
    backup(args.annotation_root, args.destination)
