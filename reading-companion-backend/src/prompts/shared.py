"""Shared prompt fragments reused across mechanisms and capabilities."""

LANGUAGE_OUTPUT_CONTRACT = """- 解释性文本字段（如 summary/reason/note/content/reflection）必须使用 {output_language_name}
- 原文引用字段（如 anchor_quote、书中直接引文）保持原文语言，不翻译
- 搜索命中字段（title/snippet/url）保持原样，不翻译、不改写
- 专有名词、作品名、机构名、URL 可保留原文
- 如果需要引用语义段编号，只能使用输入中提供的可见锚点，不要生成内部编号"""

QUERY_LANGUAGE_POLICY = """- `queries` 只追求检索有效性，可中英混用，不受输出语言硬约束
- 不要翻译或改写命题里的专有名词"""

