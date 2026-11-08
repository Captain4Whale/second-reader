"""Public-safe, authored synthetic source. Never presented as a model experiment."""

from copy import deepcopy

from scripts.q1_comparison import digest
from src.reading_core.book_document_identity import book_document_substrate_digest


def coordinate(offset):
    return dict(chapter_id=1, paragraph_index=1, char_offset=offset)


def source_range(start, end):
    return dict(start=coordinate(start), end=coordinate(end))


def synthetic_inputs():
    text = "合成示例甲乙丙丁戊己庚辛壬癸天地玄黄宇宙洪荒🌱终"
    doc = {
        "chapters": [
            {
                "id": 1,
                "title": "合成章节",
                "paragraphs": [
                    {"paragraph_index": 1, "text": text, "href": "synthetic.xhtml"}
                ],
            }
        ]
    }
    source = dict(
        source_id="synthetic-source",
        epub_sha256=digest("no real EPUB; synthetic fixture"),
        substrate_sha256=book_document_substrate_digest(doc),
    )
    windows = [
        dict(
            source_id=source["source_id"],
            original_source_range=source_range(lo, hi),
            book="合成数据 · 非模型产出",
            author="测试夹具",
            chapter_title="合成章节",
            paragraphs=[
                dict(index=1, offset=lo, text=text[lo:hi], href="synthetic.xhtml")
            ],
            before=[text[:lo]] if lo else [],
            after=[text[hi:]] if hi < len(text) else [],
        )
        for lo, hi in [(0, 14), (14, len(text))]
    ]

    def mark(mid, lo, hi, kind="H"):
        return dict(
            marginalia_id=mid,
            source_id=source["source_id"],
            type=kind,
            body_text="这是一条用于操作验证的合成旁注。" if kind == "N" else "",
            original_source_range=source_range(lo, hi),
            source_quote=text[lo:hi],
            request_sha256=None,
        )

    outputs = []
    for i, marks in enumerate(
        [
            [mark("m1", 2, 5), mark("m2", 12, 18, "N"), mark("m3", 22, 24)],
            [mark("m1", 3, 7), mark("m2", 16, 20, "N")],
        ]
    ):
        outputs.append(
            dict(
                schema="q1-digest-comparison-output/1",
                experiment_id=f"SYNTHETIC-{i + 1}",
                run_id=f"synthetic-run-{i + 1}",
                model=f"synthetic-model-{i + 1}",
                prompt=dict(version="synthetic-prompt/1", release_sha256=None),
                reconstructed=False,
                synthetic=True,
                sources=[deepcopy(source)],
                coverage=[
                    dict(
                        source_id=source["source_id"],
                        original_source_range=source_range(0, len(text)),
                        status="complete",
                    )
                ],
                marginalia=marks,
                output_sha256=digest(marks),
            )
        )
    return (
        [source],
        windows,
        outputs,
        dict(id="synthetic-windows-v1", sha256=digest(windows)),
    )
