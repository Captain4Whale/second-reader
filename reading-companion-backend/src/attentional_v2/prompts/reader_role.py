"""Reader role prompt fragment for attentional_v2."""

from __future__ import annotations

from .assembly import PromptFragment, PromptFragmentRegistry


READER_ROLE_FRAGMENT = PromptFragment(
    fragment_id="reader.role",
    text="""你是一个知识渊博、有深刻洞见的阅读爱好者。当前你正在深入阅读一本书，在理解这本书内容的同时，积极对其进行思考，沉淀有价值的理解，并产生有价值的输出，从而获得最大的求知乐趣与自我提升。你的阅读可能分为多个步骤，具体每一步的活动请参考具体指令。
""",
)


READER_ROLE_FRAGMENT_REGISTRY = PromptFragmentRegistry([READER_ROLE_FRAGMENT])


__all__ = [
    "READER_ROLE_FRAGMENT",
    "READER_ROLE_FRAGMENT_REGISTRY",
]
