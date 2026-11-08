"""Local-only run receipts and complete logical model inputs, without credentials."""

from contextlib import contextmanager
from contextvars import ContextVar
from datetime import datetime, timezone
import hashlib
from pathlib import Path
import subprocess
import threading
import uuid

from src.prompts.integrity import canonical

_CURRENT = ContextVar("run_provenance", default=None)
_LOCK = threading.Lock()


def current_provenance():
    state = _CURRENT.get()
    return state["receipt"] if state else None


def _sha(raw):
    return hashlib.sha256(raw).hexdigest()


def capture_workspace(directory: Path, *, repo: Path | None = None) -> dict:
    """Capture tracked staged+unstaged diff against HEAD and inventory untracked files.

    No provider settings, environment variables, credentials or ignored files are read.
    Untracked bodies are deliberately not copied: their names/hashes are evidence of
    incompleteness, not a claim that this patch reproduces them.
    """
    repo = repo or Path(__file__).resolve().parents[2]

    def git(*args):
        return subprocess.run(
            ["git", "-C", str(repo), *args], check=True, capture_output=True
        ).stdout

    try:
        status = git("status", "--porcelain=v1", "-z")
        commit = git("rev-parse", "HEAD").decode().strip()
    except (OSError, subprocess.SubprocessError):
        return {
            "code_commit": None,
            "code_dirty": None,
            "code_revision_status": "unavailable",
            "status_porcelain": [],
            "patch": None,
            "untracked_files": [],
            "reproduction_complete": False,
        }
    result = {
        "code_commit": commit,
        "code_dirty": bool(status),
        "status_porcelain": status.decode().split("\0")[:-1],
        "patch": None,
        "untracked_files": [],
    }
    if status:
        directory.mkdir(parents=True, exist_ok=True)
        # Capture from repository root even when the reader is launched in backend/.
        top = Path(git("rev-parse", "--show-toplevel").decode().strip())
        patch = subprocess.run(
            ["git", "-C", str(top), "diff", "--binary", "HEAD", "--"],
            check=True,
            capture_output=True,
        ).stdout
        path = directory / "workspace.patch"
        path.write_bytes(patch)
        result["patch"] = {
            "path": str(path),
            "sha256": _sha(patch),
            "base_commit": result["code_commit"],
        }
        for name in (
            subprocess.run(
                [
                    "git",
                    "-C",
                    str(top),
                    "ls-files",
                    "--others",
                    "--exclude-standard",
                    "-z",
                ],
                check=True,
                capture_output=True,
            )
            .stdout.decode()
            .split("\0")
        ):
            if name:
                f = top / name
                result["untracked_files"].append(
                    {
                        "path": name,
                        "sha256": _sha(f.read_bytes())
                        if f.is_file() and not f.is_symlink()
                        else None,
                    }
                )
    result["reproduction_complete"] = not result["untracked_files"]
    return result


@contextmanager
def provenance_scope(output_dir: Path, *, stage: str):
    invocation_id = uuid.uuid4().hex
    directory = output_dir / "_runtime/provenance" / invocation_id
    directory.mkdir(parents=True, exist_ok=False)
    workspace = capture_workspace(directory)
    receipt = {
        "schema_version": 1,
        "invocation_id": invocation_id,
        "stage": stage,
        "started_at": datetime.now(timezone.utc).isoformat(),
        "workspace": workspace,
        "request_index": str(directory / "requests.jsonl"),
        "samples": {},
    }
    state = {"directory": directory, "receipt": receipt}
    token = _CURRENT.set(state)
    try:
        yield receipt
    finally:
        (directory / "invocation.json").write_bytes(canonical(receipt) + b"\n")
        _CURRENT.reset(token)


def record_request(
    *,
    call_id,
    messages,
    tools,
    tool_choice,
    expect_json,
    trace_context,
    system_prompt=None,
    user_prompt=None,
):
    """Hash the actual post-assembly messages, including tool history and repair text.

    This identifies the provider-neutral request, not adapter-specific HTTP bytes.
    Only message/tool fields are serialized; never provider credentials or options.
    """
    normalized = []
    for message in messages:
        if isinstance(message, dict):
            normalized.append(
                {
                    key: message[key]
                    for key in ("role", "content", "tool_calls", "tool_call_id", "name")
                    if key in message
                }
            )
        else:
            item = {"role": getattr(message, "type", "ai"), "content": message.content}
            for key in ("tool_calls", "tool_call_id", "name"):
                value = getattr(message, key, None)
                if value:
                    item[key] = value
            additional = getattr(message, "additional_kwargs", {})
            for key in ("tool_calls", "function_call"):
                if key in additional and key not in item:
                    item[key] = additional[key]
            normalized.append(item)
    payload = {
        "schema": "logical-model-request/1",
        "messages": normalized,
        "tools": tools,
        "tool_choice": tool_choice,
        "expect_json": expect_json,
    }
    raw = canonical(payload)
    system = [m for m in normalized if m.get("role") == "system"]
    user = [m for m in normalized if m.get("role") in ("human", "user")]
    fields = {
        "request_sha256": _sha(raw),
        "system_prompt_hash": _sha(
            system_prompt.encode() if system_prompt is not None else canonical(system)
        ),
        "user_prompt_hash": _sha(
            user_prompt.encode() if user_prompt is not None else canonical(user)
        ),
    }
    state = _CURRENT.get()
    if state is None:
        return fields
    directory, receipt = state["directory"], state["receipt"]
    node = (trace_context.node if trace_context else None) or "unknown"
    extra = trace_context.extra if trace_context else {}
    fields["provenance_invocation_id"] = receipt["invocation_id"]
    record = {
        "call_id": call_id,
        "node": node,
        "prompt_version": extra.get("prompt_version"),
        **fields,
    }
    with _LOCK:
        with (directory / "requests.jsonl").open("ab") as stream:
            stream.write(canonical(record) + b"\n")
        # One sample per node is small and still gives all three prompt families evidence.
        if node not in receipt["samples"]:
            sample = directory / f"sample-{len(receipt['samples']) + 1}.json"
            sample.write_bytes(raw + b"\n")
            receipt["samples"][node] = {
                "call_id": call_id,
                "path": str(sample),
                **fields,
            }
    return fields
