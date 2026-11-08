"""Read exact versioned text; private assets are mandatory, content-addressed inputs."""

from hashlib import sha256
from pathlib import Path
import re

BACKEND = Path(__file__).resolve().parents[2]
PRIVATE_ASSETS = BACKEND / "state/prompt_assets"
_BLOCK = re.compile(r"<!-- prompt:([^\n]+) -->\n(.*?)\n<!-- /prompt -->", re.S)
_PRIVATE = re.compile(r"\{\{private:([a-f0-9]{64})\}\}")


def read_texts(path: Path, *, private_assets: Path | None = None) -> dict[str, str]:
    blocks = _BLOCK.findall(path.read_text(encoding="utf-8"))
    if not blocks or len({key for key, _ in blocks}) != len(blocks):
        raise ValueError(f"Missing or duplicate prompt blocks: {path}")

    def resolve(match):
        digest = match[1]
        asset = (private_assets or PRIVATE_ASSETS) / f"{digest}.txt"
        if not asset.is_file():
            raise FileNotFoundError(
                f"Required private prompt asset missing: {asset}. See experiments/README.md; no example-free fallback is permitted."
            )
        raw = asset.read_bytes()
        if sha256(raw).hexdigest() != digest:
            raise ValueError(f"Private prompt asset SHA-256 mismatch: {asset}")
        return raw.decode("utf-8")

    return {key: _PRIVATE.sub(resolve, value) for key, value in blocks}


def prompt_text(family: str, version: str, key: str) -> str:
    path = BACKEND / "src/attentional_v2/prompts/versions" / family / f"{version}.md"
    return read_texts(path)[key]


def shared_text(key: str) -> str:
    return read_texts(Path(__file__).parent / "versions/shared/v1.md")[key]
