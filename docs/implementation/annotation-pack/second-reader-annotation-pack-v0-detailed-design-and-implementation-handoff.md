# Second Reader Annotation Pack v0：详细设计与实施交接

状态：`implementation_active_minimal_reset_slice_3_candidate`（Authority reset 与 atomic wire cutover 已验收；最终文档与分支收口中）

协议代号：`second-reader-annotation-pack/0.1`

文档日期：`2026-08-25`

实施任务：`TASK-ANNOTATION-PACK-V0-IMPLEMENTATION`

决策记录：`DEC-155`（部分被取代）、`DEC-156`（当前权威）

本文中的 `MUST`、`MUST NOT`、`SHOULD`、`MAY` 分三种来源明确表述：W3C Recommendation 的要求、固定版本 EPUB Working Draft 的要求、Second Reader Pack v0 的项目级规则。除非明确标注为 W3C 要求，其余规范性词语均指 Second Reader 项目规则。

事实标签：

- **Current fact**：已由当前代码、测试或现存 artifact 核对。
- **Accepted decision**：本任务输入已经确定，不在本设计中重新讨论。
- **Proposed v0**：本设计固定、由后续 implementation slice 实现。
- **Future-reserved**：v0 不实现，只保证不堵死演进。
- **Resolved confirmation**：owner 已于 `2026-08-23` 确认 GitHub Pages IRI、分支、逐 Slice commit/push 和第 20 节完成条件。

> **Authority reset (2026-08-25)**：`DEC-156` 与本文第 20 节是尚未公开 v0 的当前实施权威。第 1–19 节保留为首轮重型 v0 的设计与已落地历史；其中与第 20 节冲突的 Work/Edition/File、Track、`sr:*`、chapter context/fingerprint、ParagraphChar、CFI、provenance 和 public digest 要求不再是 v0 要求。

## 1. Executive Summary

Annotation Pack 是“一份具体 textual edition × 一条 Annotation Track”的可分发 sidecar。它不包含 EPUB 正文，只携带 creator、出版物身份、Highlight/Note、可复核锚点和最小安全 provenance。目标使用关系是：

```text
book.epub + <track>.annotations
```

它是 Agent、未来 Annotation Library 与 Reader Adapter 之间的 stable seam：Agent runtime 可以继续演进，Reader 不必理解 `attentional_v2` 的 memory、settlement、reaction taxonomy 或 checkpoint；相反，Agent 只需把已经 settled 的 Marginalia 投影成一个 producer-neutral contract。

本 Epic 实现：

- 一个根目录独立 contract、一个 machine-readable JSON Schema 和有效 examples；
- 一个不依赖具体 producer 的 Python reference implementation；
- 一个 `SecondReaderProducerAdapter`，把当前 native settled `highlight | note` 转换为 canonical Pack；
- publication/file/content identity、multi-anchor、deterministic IDs、严格 validator、显式 exporter/inspect CLI；
- 开发态 `annotations.json` 与正式 detached `<track>.annotations`；
- public-safe EPUB golden fixture、自动化 contract/unit/artifact tests；
- `output/<book_id>/public/annotation-packs/<track_slug>/` 下的 public product artifact。

本 Epic 明确不实现：Readest/Hypothesis/KOReader/Readwise adapter、Library API/UI、社区/评分/付费、跨版本 fuzzy alignment、跨译本迁移、Agent prompt/Digest/Memory/reading-loop 修改、自动 completion hook、新 database，以及任何 EPUB 正文再分发。

## 2. Current Repo Grounding

### 2.1 当前 source 到 Pack 的使用关系

| Current source | Current shape | Pack 使用方式 | Adapter | 分类与风险 |
|---|---|---|---|---|
| `public/book_document.json` / `BookDocument.metadata` | `book`, `author`, `book_language`, `output_language`, `source_file`；无 ISBN、edition、hash、schema version | title/author/language 只作描述；normalized content fingerprint 从 canonical chapters/paragraphs 计算 | 是 | **canonical source truth**；`source_file` 常为绝对路径，MUST NOT 导出 |
| `BookChapter` | `id`, `title`, `chapter_number`, `level`, `item_id`, `href`, `spine_index`, `paragraphs`, `sentences` | `chapter_id` 用于同一 BookDocument 内 join；title/order/fingerprint 作为 structural context | 是 | `id` 不是跨 parser/edition identity；TOC fragment 处理可能造成相同 XHTML 重复章节 |
| `ParagraphRecord` / `TextLocator` | paragraph text、1-based `paragraph_index`、`href`、element-level `start_cfi/end_cfi`、paragraph/char offsets；旧 artifacts 字段较稀疏 | 重建 exact quote、prefix/suffix、resource href 与 paragraph-char selector | 是 | **canonical source truth**；字段 optional；char end 是 end-exclusive；当前 CFI 不是 text-range proof |
| `SourceSpan` | start/end `SourceCursor`：`chapter_id`, `chapter_ref`, `paragraph_index`, `char_offset` | producer draft 的主坐标，回查 BookDocument 后才可成为公开 anchor | 是 | **mechanism-private source coordinate**；`source_span_id` 不含 publication identity，会跨书碰撞 |
| `SourceRef` | `source_span_id`, `source_span`, `quote`, `role`, `resolution` | 只用作 adapter 输入和 resolution evidence；不能原样透传 | 是，且必须严格 resolve | **mechanism-private**；当前真实 shape **没有** `href`, `locator`, `CFI`；fallback 可能是整 unit span |
| Digest `MarginaliaItem` | `kind: highlight|note`, `source_quote`, `content`, `selection_reason`；typing 仍留 compatibility fields | settled 之前只作生成来源，不直接 export | 是 | native ontology 是 `kind`；`selection_reason` 和 live Digest/audit MUST NOT 进入 Pack |
| `reaction_records.json.records[]` / `AnchoredReactionRecord` | `record_source`, `marginalia_kind`, `thought`, `source_quote`, `primary_source_ref`, compat/lineage/search fields, `created_at` | 当前唯一正式 producer 内容输入；只接受 current-native settled rows | 是 | **mechanism-private settled truth**；不是 canonical Pack schema |
| chapter compatibility result | section-shaped cards、`type/compat_family`、`marginalia/reactions` aliases、featured/count/diversity | v0 正常 exporter 禁止读取 | 不使用 | **compatibility projection**；Note 会投影为 `association`，不能反推 native kind |
| `public/book_manifest.json` | `book_id`, metadata, `source_asset`, volatile `updated_at`, absolute `source_file`, optional mechanism-private `result_file` | 只取安全 metadata hint 和相对 source-asset pointer；现场验证，绝不整包复制 | 是 | **public projection**，不是 identity authority；有 manifest 宣称 EPUB 但 asset 缺失的实物 |
| `_assets/source.epub` | provisioning 复制的源 EPUB，可能缺失、陈旧或并非真实 EPUB | 对原始 bytes 算 SHA-256；验证 ZIP/EPUB/OPF；与重建 BookDocument 做一致性 preflight | 是 | exact-file identity authority；Pack 本身不包含它 |
| older `primary_anchor`, `related_anchors`, `emitted_at_sentence_id` records | 旧 reaction shape | strict v0 skip/error；只允许未来显式 migration tool 处理 | 不在 normal path | **historical field**，不能启发式升级 |

### 2.2 实际读取的关键文件、符号与约束

| 文件 | 已核对符号/内容 | 对设计的直接约束 |
|---|---|---|
| `AGENTS.md`；`reading-companion-backend/AGENTS.md` | workspace/child rules、public/private artifact 边界、commit/check 规则 | contract、generic implementation、producer adapter 必须分层；public Pack 不落在 mechanism 目录 |
| `README.md`；`Makefile`；`scripts/contract-check.sh`；`scripts/agent-check.sh` | 当前 setup、`contract-check`、`agent-check` 路径 | 新 contract check 应接入现有根 Makefile，而非建立平行 CI 入口 |
| `docs/current-state.md`；`docs/tasks/registry.md`；`docs/tasks/registry.json` | current active/blocked/queued 路由 | 本设计登记 waiting implementation task，但不改当前 active objective/job |
| `docs/source-of-truth-map.md`；`docs/workspace-overview.md` | canonical storage map、subproject ownership | contract 落根目录，Python 参考实现落 backend，正式 artifact 落 public |
| `docs/history/README.md`；`docs/history/decision-log.md` | history retention/decision evidence rules | 本设计构成新的 stable seam，记录为 `DEC-155`；history不反向充当current behavior authority |
| `docs/product-overview.md`；`docs/product-interaction-model.md` | Second Reader 产品边界与现有用户路径 | v0 是可分发资产协议，不新增 UI/route/user journey |
| `docs/backend-state-aggregation.md`；`docs/api-contract.md` | public aggregation/compatibility API | Pack 不借用五类 reaction API shape，也不在本 Epic 增加公共 API |
| `docs/backend-reading-mechanisms/attentional_v2.md` | Digest/Marginalia、SourceRef、settlement、artifact authority | producer 从 native settled truth 适配；generic model 不依赖 mechanism ontology |
| `src/reading_core/book_document.py` | `TextLocator`, `ParagraphRecord`, `SentenceRecord`, `BookChapter`, `BookMetadata`, `BookDocument` | paragraph-char/href/CFI 的唯一 shared substrate；字段稀疏兼容必须由 adapter 处理 |
| `src/reading_core/storage.py` | `book_document_file`, `load_book_document`, `save_book_document` | `public/book_document.json` 是 canonical shared read source；当前 load 无 schema validation |
| `src/parsers/ebook_parser.py`；`src/iterator_reader/parse.py` | `_parse_epub`, `_normalize_block_text`, `_cfi_for_element`, `_paragraph_records`, `_build_book_document`, `extract_book_metadata` | normalized text、CFI 粒度、TOC fragment 与 `spine_index == 0` 风险必须进入 preflight/gap |
| `src/attentional_v2/schemas.py` | `SourceRef`, `MarginaliaItem`, `DigestResult`, `AnchoredReactionRecord` | canonical wire model不能 import 这些 private types；adapter 只在边界内理解它们 |
| `src/attentional_v2/source_spans.py` | `SourceCursor`, `SourceSpan`, `source_span_id`, `source_ref_from_span`, `source_ref_from_unit` | end-exclusive coordinate；exact/ambiguous/fallback resolution；需独立严格 resolver |
| `src/attentional_v2/llm_output_tools.py`；`llm_calls.py` | `DIGEST_RESULT_TOOL`, `validate_digest_result`, `_normalize_marginalia_item`, `digest` | live native kind 是显式 `highlight|note`；Highlight 无 content，Note 有 content |
| `src/attentional_v2/runner.py` | `_persist_marginalia`, `_run_digest_for_source_unit`, settlement/save 顺序 | audit 可领先 state save，exporter 只读持久 reaction ledger snapshot，不读 audit |
| `src/attentional_v2/slow_cycle.py` | `derive_reaction_id`, `build_reaction_record_from_surfaced_reaction`, `_target_locator_from_source_ref`, `project_chapter_result_compatibility` | reaction id/compat family 不可复用；locator helper 与 current SourceRef shape 已漂移 |
| `src/attentional_v2/storage.py` | `reaction_records_file`, chapter compatibility paths | adapter 的 private input 路径集中在 producer module；generic module不导入该 helper |
| `src/reading_runtime/artifacts.py`；`provisioning.py`；`sequential_state.py` | public/assets/runtime/mechanism helpers、`ensure_source_asset`, manifest builder | 新增中性 public path helper；manifest pointer 必须 containment/existence/format 校验 |
| `src/library/catalog.py`；`src/library/jobs.py` | output/catalog/source lookup、public status shaping | v0 不增加 Library dependency；book/output lookup 可复用中性 helper，不能把 catalog projection 当 contract |
| `tests/test_attentional_v2_source_spans.py` | exact、跨段、normalized、ordered-fragment、ambiguous、fallback cases | Pack resolver 必须支持跨段，但 strict exporter 仅接受唯一 exact match |
| `tests/test_attentional_v2_scaffold.py`；`test_attentional_v2_slow_cycle.py`；`test_attentional_v2_phase_b.py` | highlight/note persisted mapping、settlement、compat projection | `marginalia_kind` 是事实；Note 的 `compat_family=association` 是不可泄漏 sidecar |
| `tests/test_iterator_frontend_artifacts.py`；`tests/test_iterator_parse.py`；`tests/test_source_intake.py` | public artifact/source asset、可生成 EPUB 的 fixture helper | 新 golden 必须是真 EPUB；现有 36-byte `sample-upload.epub` 不能复用为协议 golden |

抽样核对还包括 current v24 `reaction_records.json`、多个 `public/book_document.json` 与 `public/book_manifest.json`。这些是 local/ignored 证据，不作为可提交 fixture。

### 2.3 代码、稳定文档与 artifact 的已确认漂移

1. **SourceRef locator drift**：任务背景与部分稳定文字容易让人理解为 current SourceRef 已携带 EPUB locator；实际 `SourceRef` 只有 span/quote/resolution。`_target_locator_from_source_ref()` 仍读取一个 current builder 不写入的 `locator`。v0 必须 join BookDocument，不能把缺失 locator 伪装成已支持。
2. **Native kind drift**：`docs/api-contract.md` 仍有由 content 空/非空推断 native kind 的兼容表述；current live tool 与 persisted ledger 已有显式 `kind` / `marginalia_kind`。Pack 只能读取显式 native discriminator。
3. **Mechanism doc field drift**：`attentional_v2.md` 的 reaction-record 摘要没有完整列出 `record_source`, `marginalia_kind`, `emitted_at_source_span_id`, `created_at` 等 current gate 字段。
4. **CFI precision gap**：`_cfi_for_element()` 产生 element-level lightweight CFI；同段 `start_cfi == end_cfi`，没有 text offset，也没有 Reader round-trip。`spine_index == 0` 还可能因 `or -1` 变成 `-1` 而丢 CFI。
5. **EPUB/BookDocument coherence gap**：source asset copy 不保存/比较 hash，已有 BookDocument 可被复用；同 slug 下可能出现新 asset + 旧 document。manifest 的 `_assets/source.epub` 声明也不保证文件存在或确为 EPUB。
6. **TOC fragment gap**：EPUB parser 丢弃 TOC href fragment，并以 resource-name substring 匹配；同 XHTML 多 fragment 可能成为多个重复 full-resource chapters。
7. **Sparse substrate drift**：旧 BookDocument 缺 `item_id`, source-normalization/HTML metadata，少量 paragraph CFI 为空；v0 只能要求 anchor 必需字段，不能要求所有最新 TypedDict optional 字段。
8. **Identity gap**：BookMetadata 无 ISBN/edition/hash；`book_id` 是 slug，manifest `updated_at` 可变，`source_span_id` 跨书碰撞，均不能作为 publication/annotation identity。
9. **Artifact write gap**：BookDocument/manifest 当前无 schema version、validation 或 atomic write；annotation exporter 自身必须做到 snapshot/recheck 与 atomic publish。
10. **Fixture gap**：tracked `sample-upload.epub` 是 36-byte placeholder；ignored local library 混有 private books。必须新建原创/CC0 微型真 EPUB。

现有 `attentional_v2.evaluation._source_ref_valid` 还把 1-based paragraph index 当作 list index/长度边界，现有 eval `_source_ref_to_slice` 又拒绝跨段 span；两者都 MUST NOT 被 Pack 复用。Pack 需要新的严格 resolver。

## 3. Architecture And Ownership

```text
attentional_v2 private artifacts                  shared source substrate
reaction_records.json -------------------+        public/book_document.json
                                         |        _assets/source.epub
                                         v               |
                              SecondReaderProducerAdapter |
                              (producer-owned parsing) <---+
                                         |
                                         v
                                list[AnnotationDraft]
                                         |
                                  AnchorBuilder
                                         |
                                         v
                           list[ResolvedAnnotationDraft]
                              + PublicationIdentityResult
                              + AnnotationTrackInput
                                         |
                                         v
                              AnnotationPackBuilder
                              (producer-neutral domain)
                                         |
                                         v
                       JSON Schema validator + semantic validator
                                         |
                              +----------+-----------+
                              |                      |
                              v                      v
                       serialize_pack()    package_detached_annotations()
                              |                      |
                              +----------+-----------+
                                         v
                   public/annotation-packs/<track_slug>/
                       current.json             (single-file atomic pointer)
                       revisions/<revision_id>/
                           annotations.json
                           <track_slug>.annotations
                           validation-report.json   (not inside package)
```

| Layer | Input | Output | Owner | 禁止依赖 | Failure boundary |
|---|---|---|---|---|---|
| `SecondReaderProducerAdapter` | output dir下 exact current reaction ledger snapshot | producer-neutral `AnnotationDraft[]`、exact ledger digest、accepted-row digests、input count、sanitized row diagnostics | `src/annotation_pack/producers/second_reader.py` | BookDocument/EPUB、export policy、compatibility chapter result、audit、prompt、Memory、public five-family ontology | ledger不可信时 pack-level fatal；private shape/legacy row在这里分类；不解析anchor、不写 public artifact |
| `PublicationIdentityBuilder` | verified EPUB bytes/OPF metadata、ephemeral + persisted BookDocument | Work/Edition/File identity | generic `annotation_pack.identity` | `attentional_v2`、book slug 作为 authority | source/EPUB/document mismatch 是 pack-level fatal |
| `AnchorBuilder` | `AnnotationDraft` + verified canonical BookDocument/resource index | `ResolvedAnnotationDraft`，内含 one canonical target with multiple selectors | generic `annotation_pack.anchors` | `SourceRef` private class；Reader-specific runtime | 不可靠 quote/span/href/CFI 被拒；不能降级成错误精确锚点 |
| `AnnotationPackBuilder` | publication/track + `ResolvedAnnotationDraft[]` | in-memory `AnnotationPackDocument` | generic `annotation_pack.builder` | producer branches、BookDocument/EPUB、artifact paths、runtime state | domain invariant violation立即失败；不进行 I/O |
| Validator | JSON document/package bytes | pre-publication `ValidationResult`；artifact bytes产生后再 finalize `ValidationReport` | generic `annotation_pack.validation` | 网络 context fetch、runtime recovery | JSON Schema errors、semantic/security errors分级；fatal 时禁止 publish |
| Serializer | validated document | canonical UTF-8 `annotations.json` bytes | generic `annotation_pack.serialization` | producer source、clock hidden global | 只接受 valid model；deterministic rules不满足则失败 |
| Packager | canonical JSON bytes | detached ZIP `.annotations` | generic `annotation_pack.packaging` | EPUB、mechanism/private assets | path/entry/size/digest错误失败；v0 只允许 root `annotations.json` |
| Export service/CLI | explicit command options | immutable public revision + atomically replaced `current.json` pointer + exit code | `annotation_pack.exporter` + scripts | normal reading completion success path | revision完整落盘后才切pointer；失败/崩溃不破坏上一个current Pack |

依赖方向固定为：

```text
contract -> generated Python bindings -> generic domain
generic domain <- producer adapters
generic domain <- CLI/service
reading runtime -> (future optional hook) exporter
```

`annotation_pack` MUST NOT import `attentional_v2`. 只有 `annotation_pack.producers.second_reader` 可以在一个边界模块内读取该 producer 的 JSON shape/path helper；它必须先输出中性 draft，再调用 generic builder。正常 Agent completion 不依赖 exporter 成功；未来自动发布需另做集成决策。

## 4. Canonical Data Model

### 4.1 Wire envelope：`AnnotationPack`

Canonical wire representation 是一个 W3C-aligned `AnnotationSet`；Python 类名为 `AnnotationPackDocument`，但 JSON `type` 保持单值 `"AnnotationSet"`，不写成多 type 数组。

表中 `Std`：`WA` = Web Annotation direct field，`EPUB-WD` = pinned EPUB profile field，`SR` = Second Reader extension。

| Field | Type | Req | Semantic / current source | Validation | Std | Status |
|---|---|---:|---|---|---|---|
| `@context` | `array[string|object]` | yes | EPUB context + one SR namespace binding | 顺序固定；禁止 remote fetch；不得重定义 WA/DC terms | EPUB-WD + SR | v0 |
| `id` | absolute IRI (`urn:uuid`) | yes | one edition × one track 的 deterministic `pack_id` | UUIDv5；与 edition/track recomputation一致 | EPUB-WD | v0 |
| `type` | `"AnnotationSet"` | yes | collection type | exact constant | EPUB-WD | v0 |
| `generator` | `Generator` object | yes (SR strengthens optional WD) | serializer application，不是 annotation author | single object，stable id/name/version | EPUB-WD + SR constraint | v0 |
| `generated` | RFC 3339 UTC datetime | yes (SR) | 本次序列化时间 | `Z`、秒精度；不参与 semantic digest/IDs | EPUB-WD | v0 |
| `about` | `PublicationIdentity` | yes | target EPUB 的 Work/Edition/File identity | file + content fingerprints required | EPUB-WD + SR | v0 |
| `items` | `array[Annotation]` | yes | 本 track 的 Highlight/Note | 按 `annotation.id` bytewise 排序；id 唯一；可为空仅显式 policy | EPUB-WD | v0 |
| `sr:specVersion` | semver string | yes | Pack protocol version | v0 initial `0.1.0` | SR | v0 |
| `sr:schemaVersion` | semver string | yes | JSON Schema version | must equal validator-supported schema | SR | v0 |
| `sr:extensionVersion` | semver-major/minor | yes | SR JSON-LD vocabulary version | v0 initial `0.1` | SR | v0 |
| `sr:profile` | `ProfileReference` | yes | pinned standards and conformance claim | exact official dated URLs/status | SR | v0 |
| `sr:track` | `AnnotationTrack` | yes | one creator/track identity | all item creators match track creator id | SR | v0 |
| `sr:provenance` | `Provenance` | yes | safe producer/adapter + input snapshot digest | no path/job/runtime/private IDs | SR | v0 |
| `sr:semanticDigest` | `Digest` | yes | stable comparison of semantic projection | SHA-256 over canonical projection excluding volatile fields/self | SR | v0 |

`ProfileReference` 固定包含：

| Field | Type | Req | Meaning / validation | Std | Status |
|---|---|---:|---|---|---|
| `type` | `"sr:ProfileReference"` | yes | custom object type | SR | v0 |
| `sr:webAnnotation` | absolute IRI | yes | `https://www.w3.org/TR/2017/REC-annotation-model-20170223/` | SR value pointing WA | v0 |
| `sr:epubAnnotations` | absolute IRI | yes | `https://www.w3.org/TR/2026/WD-epub-anno-10-20260521/` | SR value pointing pinned WD | v0 |
| `sr:conformance` | `"aligned"` | yes | 明确不是完整 EPUB-WD conformance claim | SR | v0 |

### 4.2 `PublicationIdentity`, `WorkIdentity`, `EditionIdentity`, `FileIdentity`

| Entity.Field | Type | Req | Semantic / current source | Validation | Std | Status |
|---|---|---:|---|---|---|---|
| `PublicationIdentity.dc:format` | string | yes | target file media type | exact `application/epub+zip` | EPUB-WD/DC | v0 |
| `.dc:title` | non-empty string | yes (SR) | BookMetadata/OPF title | NFC、trim；只作 metadata | EPUB-WD/DC | v0 |
| `.dc:creator` | `array[string]` | no | OPF/BookMetadata book authors | NFC、去空、保序去重 | EPUB-WD/DC | v0 |
| `.dc:identifier` | `array[string]` | yes (SR) | work/edition/file ids 的公开索引 | must contain three nested ids | EPUB-WD/DC | v0 |
| `.sr:work` | `WorkIdentity` | yes | work-level asserted/provisional identity | rules below | SR | v0 |
| `.sr:edition` | `EditionIdentity` | yes | normalized textual edition identity | content fingerprint required | SR | v0 |
| `.sr:file` | `FileIdentity` | yes | exact detached EPUB file identity | raw byte SHA-256 required | SR | v0 |
| `WorkIdentity.id` | `urn:uuid` | yes | authoritative identifier set or provisional metadata key | deterministic UUIDv5 | SR | v0 |
| `.type` | `"sr:WorkIdentity"` | yes | object type | constant | SR | v0 |
| `.sr:identityStrength` | `"asserted"|"provisional"` | yes | explicit work-level authority vs title/creator fallback | ISBN/普通 OPF identifier不是 work-level authority；title/author MUST be provisional | SR | v0 |
| `.sr:identifiers` | `array[Identifier]` | no | 仅明确指向 abstract work 的 URI/ID | scheme/value normalized；不接受 ISBN/local path | SR | v0 |
| `EditionIdentity.id` | `urn:uuid` | yes | textual edition id | UUIDv5 over algorithm+content digest | SR | v0 |
| `.type` | `"sr:EditionIdentity"` | yes | object type | constant | SR | v0 |
| `.sr:contentFingerprint` | `Fingerprint` | yes | normalized BookDocument content | algorithm/version/digest exact | SR | v0 |
| `.sr:publicationIdentifiers` | `array[Identifier]` | no | ISBN/OPF unique identifier 等 edition/manifestation-level声明 | syntax/source normalized；不提升 Work strength | SR | v0 |
| `.sr:language` | BCP 47 string | no | textual edition language | valid tag when known；不使用 output UI language | SR | v0 |
| `.sr:chapterFingerprints` | `array[ChapterFingerprint]` | yes | ordered chapter structural hints | chapter id/order unique；digest valid | SR | v0 |
| `FileIdentity.id` | `urn:uuid` | yes | exact file id | UUIDv5 over media type + SHA-256 | SR | v0 |
| `.type` | `"sr:FileIdentity"` | yes | object type | constant | SR | v0 |
| `.dc:format` | string | yes | source file media type | exact `application/epub+zip` | DC | v0 |
| `.sr:sha256` | lowercase hex string | yes | raw `_assets/source.epub` bytes | exactly 64 hex chars；现场计算 | SR | v0 |
| `.sr:byteLength` | non-negative integer | yes | raw byte size | must match opened regular file | SR | v0 |

`Identifier = {"type":"sr:Identifier", "sr:scheme": string, "sr:value": string}`。v0 识别 `isbn-10`, `isbn-13`, `uri`, `opf-identifier`, `work-uri`。ISBN与普通 OPF unique identifier放在 `EditionIdentity.sr:publicationIdentifiers`：它们是 publication/manifestation evidence，不是 abstract Work authority。只有来源明确、语义明确指向 work（例如项目显式提供的 work-level URI/ID）的 identifier 才进入 `WorkIdentity.sr:identifiers` 并把 strength设为 `asserted`。

`Fingerprint = {"type":"sr:Fingerprint", "sr:algorithm":"sha256", "sr:algorithmVersion": string, "sr:value": lowercase-hex}`。Chapter fingerprint 增加 `sr:chapterId`, `sr:order`, optional `sr:title`, `sr:resourceHrefs[]`；它是同一 BookDocument 内 structural aid，不宣称跨译本对齐。

### 4.3 `AnnotationTrack`, `Creator`, `Generator`, `Provenance`

| Entity.Field | Type | Req | Semantic / source | Validation | Std | Status |
|---|---|---:|---|---|---|---|
| `AnnotationTrack.id` | `urn:uuid` | yes | creator + stable track key + edition | deterministic UUIDv5 | SR | v0 |
| `.type` | `"sr:AnnotationTrack"` | yes | object type | constant | SR | v0 |
| `.sr:key` | safe string | yes | producer-neutral stable logical key | `^[a-z0-9][a-z0-9._-]{0,63}$`；不得含 job/path | SR | v0 |
| `.name` | string | no | display label | NFC，1..128 code points | WA common | v0 |
| `.creator` | `Creator` | yes | track唯一 creator | all annotations use same creator id | WA + SR constraint | v0 |
| `Creator.id` | absolute IRI | yes (SR) | Person/Organization/Software identity | stable；不得由 display name alone随机生成 | WA | v0 |
| `.type` | enum | yes | `Person|Organization|Software` | exact enum | WA | v0 |
| `.name` | string | yes (SR) | display name | NFC、非空、<=256 | WA | v0 |
| `Generator.id` | absolute IRI | yes | serializer application | distinct semantics from creator | EPUB-WD/WA | v0 |
| `.type` | `"Software"` | yes | generator class | constant | WA | v0 |
| `.name` | string | yes | `Second Reader Annotation Pack Exporter` | non-empty | WA | v0 |
| `.sr:version` | semver/build string | yes | reference implementation version | no local path/secret | SR | v0 |
| `Provenance.type` | `"sr:Provenance"` | yes | safe provenance object | constant | SR | v0 |
| `.sr:producer` | absolute IRI | yes | producer adapter identity | current adapter stable IRI/URN | SR | v0 |
| `.sr:adapterVersion` | semver string | yes | adapter contract version | supported version | SR | v0 |
| `.sr:inputSnapshotDigest` | `Digest` | yes | canonicalized accepted draft inputs | excludes paths/private fields | SR | v0 |
| `.sr:inputSnapshotAlgorithmVersion` | string | yes | producer-safe snapshot framing | current adapter exact `sr-second-reader-input-snapshot-v1` | SR | v0 |

`reaction_id`, `run_id`, `job_id`, source artifact path、mechanism key、audit pointer 不属于 Pack provenance。必要的 source-row 对照仅进入不随 `.annotations` 分发的 sanitized `validation-report.json`。

`Digest` wire object定义为：required `type="sr:Digest"`, `sr:algorithm="sha256"`, `sr:value`（64位 lowercase hex）；`sr:canonicalization` 只在 digest确实基于一个已命名 canonicalization时出现。`sr:semanticDigest` 必须写 `sr:canonicalization="sr-canonical-json-v1"`；raw input snapshot digest若仅对明确 framing后的 bytes计算，则由 provenance contract固定 framing version，不伪写 JSON canonicalization。

### 4.4 `Annotation`, `AnnotationTarget`, selectors 与 `TextualBody`

| Entity.Field | Type | Req | Semantic / current source | Validation | Std | Status |
|---|---|---:|---|---|---|---|
| `Annotation.id` | `urn:uuid` | yes | canonical `annotation_id` | deterministic；全 Pack 唯一 | WA/EPUB-WD | v0 |
| `.type` | `"Annotation"` | yes | annotation class | constant | WA/EPUB-WD | v0 |
| `.motivation` | enum | yes | highlight→`highlighting`; note→`commenting` | one value only | WA/EPUB-WD | v0 |
| `.creator` | `Creator` | yes | track creator | id/type/name must match track | WA/EPUB-WD | v0 |
| `.created` | RFC 3339 UTC | yes (SR) | persisted `created_at` | required current-native row；valid UTC | WA/EPUB-WD | v0 |
| `.body` | `TextualBody` | conditional | Note visible content | highlight MUST omit；note MUST have exactly one | WA/EPUB-WD | v0 |
| `.target` | `AnnotationTarget` | yes | one anchored source segment | exactly one target | WA/EPUB-WD | v0 |
| `.sr:kind` | `"highlight"|"note"` | yes | native product primitive | consistent with motivation/body | SR | v0 |
| `TextualBody.type` | `"TextualBody"` | yes | plain-text note | constant | WA | v0 |
| `.value` | string | yes | current `thought` / Digest content | NFC、non-empty、<=16384 code points | WA | v0 |
| `.format` | `"text/plain"` | yes | no HTML/Markdown contract in v0 | constant | WA | v0 |
| `.language` | BCP 47 | no | note language if defensible | valid tag；不从 output language盲推 | WA | v0 |
| `AnnotationTarget.type` | `"SpecificResource"` | yes | segment target | constant | WA | v0 |
| `.source` | relative EPUB manifest href | yes | start/end ParagraphRecord href | no scheme/query/fragment/`..`；must exist in OPF manifest；range不能跨 href | WA/EPUB-WD | v0 |
| `.selector` | selector array | yes (SR strengthens optional WD) | quote + paragraph-char + optional CFI | exactly one quote and one paragraph-char；optional max one CFI | WA + SR | v0 |
| `.sr:anchorId` | `urn:uuid` | yes | edition-bound anchor identity | deterministic recomputation | SR | v0 |
| `.sr:chapter` | `ChapterContext` | yes | chapter id/order/title/fingerprint | must match Edition chapter list | SR | v0 |

Required `TextQuoteSelector`：

| Field | Type | Req | Rule | Std | Status |
|---|---|---:|---|---|---|
| `type` | `"TextQuoteSelector"` | yes | constant | WA | v0 |
| `exact` | string | yes | 从 BookDocument span 重建；1..1024 Unicode code points；不得截断 | WA | v0 |
| `prefix` | string | yes (SR) | 同 resource canonical text 中 exact 前最多 64 code points，schema max 128 | WA | v0 |
| `suffix` | string | yes (SR) | exact 后最多 64 code points，schema max 128 | WA | v0 |
| `sr:normalization` | `"sr-epub-resource-text-v1"` | yes | 声明 WA quote所用 XHTML→logical text项目算法 | SR | v0 |

Required `sr:ParagraphCharSelector`：

```json
{
  "type": "sr:ParagraphCharSelector",
  "sr:coordinateSystem": "sr-book-document-paragraph-char-v1",
  "sr:offsetUnit": "unicode-code-point",
  "sr:start": {"sr:chapterId": 1, "sr:paragraphIndex": 4, "sr:charOffset": 12},
  "sr:end": {"sr:chapterId": 1, "sr:paragraphIndex": 5, "sr:charOffset": 9}
}
```

`paragraphIndex` 沿用当前 persisted 1-based index；`charOffset` 是 Python normalized string 的 Unicode code-point offset，start inclusive/end exclusive。跨段重建时段之间使用当前 `source_unit_from_span()` 的 `"\n\n"` separator。start/end chapter 必须相同；覆盖的所有 paragraph 必须属于同一 target href。

Optional `sr:EpubCfiSelector`：

```json
{
  "type": "sr:EpubCfiSelector",
  "value": "epubcfi(/6/4!/4/2/6,/1:12,/1:28)",
  "sr:verification": "quote-round-trip"
}
```

只有 exporter 使用独立 CFI resolver 在 exact source EPUB 上 round-trip，再按 `sr-epub-resource-text-v1`得到与 `exact`完全相同的 code-point slice时才能发出。current element-level paragraph CFI 不满足此 gate，因此 current adapter v0 默认省略该 selector。它不伪装成 pinned EPUB WD 的 `FragmentSelector`。

`ChapterContext` 字段为 `type="sr:ChapterContext"`, `sr:chapterId` (integer), `sr:order` (positive integer), optional `name`, required `sr:fingerprint` (`Fingerprint` object，algorithm version必须为 `sr-book-document-chapter-v1`)。`chapterId` 只用于同一 edition 的结构关联；fingerprint提供 future re-anchoring hint并必须等于 `EditionIdentity.sr:chapterFingerprints` 中同章的 digest。

### 4.5 Extension metadata 与 future-reserved 边界

v0 确实需要的 SR extension 只有：version/profile、publication三层身份与 fingerprint、track、native kind、安全 provenance/semantic digest、quote normalization声明、paragraph-char selector、chapter context、optional verified CFI。v0 schema 不预留空的 compatibility map、migration candidates、social metadata、rating、reading progress、Memory 或 agent reasoning 字段。

Future consumers 可用已声明 JSON-LD prefix 添加 optional extension。未知 **unprefixed** field 必须拒绝；未知且 context 已声明的 prefixed field 可保留并 warning/ignore。未知 `sr:` field 只在相同 spec major 下按 optional extension 处理；任何新 required semantics 必须提升 schema/spec major。

## 5. Highlight And Note Mapping

### 5.1 Mapping rules

| Native settled value | W3C-aligned output | v0 invariant |
|---|---|---|
| `marginalia_kind="highlight"`, empty `thought` | `motivation="highlighting"`, `sr:kind="highlight"`, no `body` | `thought` 非空即 invalid；不把 private selection reason补成 body |
| `marginalia_kind="note"`, non-empty `thought` | `motivation="commenting"`, `sr:kind="note"`, one plain `TextualBody` | empty body invalid；不采用 compatibility `association` |
| `primary_source_ref` exact unique span | one `SpecificResource` target with quote + paragraph-char selectors | exporter 从 BookDocument 重建 quote/context/href；不信任原 row 直接透传 |
| `created_at` | annotation `created` | RFC 3339 UTC required；不以 export time代替 |
| Track creator config | annotation `creator` | Pack 内每条必须同一 creator |
| producer record id | validation report correlation only | 不作为 canonical annotation id/provenance |

### 5.2 Minimal Highlight item

以下 UUID 为结构示例；正式值由第 9 节算法计算。

```json
{
  "id": "urn:uuid:2e95ed39-c078-5c63-93fe-48ae17f13b18",
  "type": "Annotation",
  "motivation": "highlighting",
  "creator": {
    "id": "urn:uuid:95a909f2-658f-50c5-9c2b-8ef0e6dc7512",
    "type": "Software",
    "name": "Second Reader"
  },
  "created": "2026-07-03T08:30:00Z",
  "target": {
    "type": "SpecificResource",
    "source": "Text/chapter-01.xhtml",
    "selector": [
      {
        "type": "TextQuoteSelector",
        "exact": "A durable idea is worth returning to.",
        "prefix": "The reader paused. ",
        "suffix": " Then the argument moved on.",
        "sr:normalization": "sr-epub-resource-text-v1"
      },
      {
        "type": "sr:ParagraphCharSelector",
        "sr:coordinateSystem": "sr-book-document-paragraph-char-v1",
        "sr:offsetUnit": "unicode-code-point",
        "sr:start": {"sr:chapterId": 1, "sr:paragraphIndex": 2, "sr:charOffset": 19},
        "sr:end": {"sr:chapterId": 1, "sr:paragraphIndex": 2, "sr:charOffset": 56}
      }
    ],
    "sr:anchorId": "urn:uuid:c9718883-d248-59ab-8fa2-44886bd0afd0",
    "sr:chapter": {
      "type": "sr:ChapterContext",
      "sr:chapterId": 1,
      "sr:order": 1,
      "name": "A Small Beginning",
      "sr:fingerprint": {"type": "sr:Fingerprint", "sr:algorithm": "sha256", "sr:algorithmVersion": "sr-book-document-chapter-v1", "sr:value": "3cfdb8b1ff4a08b274836fded5205374d485351c4c5863c2bf066690391b4cbb"}
    }
  },
  "sr:kind": "highlight"
}
```

### 5.3 Minimal Note item

```json
{
  "id": "urn:uuid:6cc4f771-cc56-5a0c-a05c-7c75f9743758",
  "type": "Annotation",
  "motivation": "commenting",
  "creator": {
    "id": "urn:uuid:95a909f2-658f-50c5-9c2b-8ef0e6dc7512",
    "type": "Software",
    "name": "Second Reader"
  },
  "created": "2026-07-03T08:31:00Z",
  "body": {
    "type": "TextualBody",
    "value": "This turns rereading into a deliberate test, not repetition.",
    "format": "text/plain",
    "language": "en"
  },
  "target": {
    "type": "SpecificResource",
    "source": "Text/chapter-01.xhtml",
    "selector": [
      {
        "type": "TextQuoteSelector",
        "exact": "Return with a better question.",
        "prefix": "Do not merely repeat. ",
        "suffix": " The page may answer differently.",
        "sr:normalization": "sr-epub-resource-text-v1"
      },
      {
        "type": "sr:ParagraphCharSelector",
        "sr:coordinateSystem": "sr-book-document-paragraph-char-v1",
        "sr:offsetUnit": "unicode-code-point",
        "sr:start": {"sr:chapterId": 1, "sr:paragraphIndex": 3, "sr:charOffset": 22},
        "sr:end": {"sr:chapterId": 1, "sr:paragraphIndex": 3, "sr:charOffset": 52}
      }
    ],
    "sr:anchorId": "urn:uuid:006bb1e4-7e83-5d97-98aa-c606207f93f8",
    "sr:chapter": {
      "type": "sr:ChapterContext",
      "sr:chapterId": 1,
      "sr:order": 1,
      "name": "A Small Beginning",
      "sr:fingerprint": {"type": "sr:Fingerprint", "sr:algorithm": "sha256", "sr:algorithmVersion": "sr-book-document-chapter-v1", "sr:value": "3cfdb8b1ff4a08b274836fded5205374d485351c4c5863c2bf066690391b4cbb"}
    }
  },
  "sr:kind": "note"
}
```

### 5.4 Complete minimal Pack with both items

为避免正文重复，下面用较短的 fixture text，但仍展示所有 required top-level identity/version/provenance fields。这里的 UUID、digest、byte length 与 offset 是 schema-valid 协议示例值，不是已经由 fixture重算的 semantic test vector，也不得被引用为 golden。Slice 1 只由 schema/contract tests锁定其 wire shape；Slice 2 提交 identity/fingerprint fixed vectors，Slice 8 再从最终 tiny EPUB fixture重建并由 semantic validator锁定正式 golden，不能复制这些示意 digest冒充已验证事实。

```json
{
  "@context": [
    "https://www.w3.org/ns/epub-anno.jsonld",
    {"@protected": true, "sr": "https://captain4whale.github.io/second-reader/ns/annotation-pack#"}
  ],
  "id": "urn:uuid:31f414c4-32f3-50d6-85e1-9382e47c6390",
  "type": "AnnotationSet",
  "generator": {
    "id": "urn:uuid:8aef6a01-c757-51b3-8245-5fcdff08f737",
    "type": "Software",
    "name": "Second Reader Annotation Pack Exporter",
    "sr:version": "0.1.0"
  },
  "generated": "2026-08-23T00:00:00Z",
  "about": {
    "dc:format": "application/epub+zip",
    "dc:title": "The Tiny Reader Fixture",
    "dc:creator": ["Second Reader Test Authors"],
    "dc:identifier": [
      "urn:uuid:eb86ac5d-92e7-5306-b891-0ab1d7b2c713",
      "urn:uuid:c0493acf-8277-574b-968d-801d8fe77768",
      "urn:uuid:1cbdcba1-1388-5a11-abf0-852ddca6d1c9"
    ],
    "sr:work": {
      "id": "urn:uuid:eb86ac5d-92e7-5306-b891-0ab1d7b2c713",
      "type": "sr:WorkIdentity",
      "sr:identityStrength": "provisional"
    },
    "sr:edition": {
      "id": "urn:uuid:c0493acf-8277-574b-968d-801d8fe77768",
      "type": "sr:EditionIdentity",
      "sr:contentFingerprint": {
        "type": "sr:Fingerprint",
        "sr:algorithm": "sha256",
        "sr:algorithmVersion": "sr-book-document-text-v1",
        "sr:value": "36c9a5c98a7a9a2bf3425d96e9c993839acd63ae676b77ba2efffd635d5f774d"
      },
      "sr:publicationIdentifiers": [
        {"type": "sr:Identifier", "sr:scheme": "opf-identifier", "sr:value": "urn:uuid:fixture-edition"}
      ],
      "sr:language": "en",
      "sr:chapterFingerprints": [
        {
          "type": "sr:ChapterFingerprint",
          "sr:chapterId": 1,
          "sr:order": 1,
          "sr:title": "A Small Beginning",
          "sr:resourceHrefs": ["Text/chapter-01.xhtml"],
          "sr:algorithm": "sha256",
          "sr:algorithmVersion": "sr-book-document-chapter-v1",
          "sr:value": "3cfdb8b1ff4a08b274836fded5205374d485351c4c5863c2bf066690391b4cbb"
        }
      ]
    },
    "sr:file": {
      "id": "urn:uuid:1cbdcba1-1388-5a11-abf0-852ddca6d1c9",
      "type": "sr:FileIdentity",
      "dc:format": "application/epub+zip",
      "sr:sha256": "c6b708b231994f2c768e0462011e764782512f0f749b83743122d243b8e74247",
      "sr:byteLength": 4096
    }
  },
  "items": [
    {
      "id": "urn:uuid:2e95ed39-c078-5c63-93fe-48ae17f13b18",
      "type": "Annotation",
      "motivation": "highlighting",
      "creator": {"id": "urn:uuid:95a909f2-658f-50c5-9c2b-8ef0e6dc7512", "type": "Software", "name": "Second Reader"},
      "created": "2026-07-03T08:30:00Z",
      "target": {
        "type": "SpecificResource",
        "source": "Text/chapter-01.xhtml",
        "selector": [
          {"type": "TextQuoteSelector", "exact": "A durable idea is worth returning to.", "prefix": "The reader paused. ", "suffix": " Then the argument moved on.", "sr:normalization": "sr-epub-resource-text-v1"},
          {"type": "sr:ParagraphCharSelector", "sr:coordinateSystem": "sr-book-document-paragraph-char-v1", "sr:offsetUnit": "unicode-code-point", "sr:start": {"sr:chapterId": 1, "sr:paragraphIndex": 2, "sr:charOffset": 19}, "sr:end": {"sr:chapterId": 1, "sr:paragraphIndex": 2, "sr:charOffset": 56}}
        ],
        "sr:anchorId": "urn:uuid:c9718883-d248-59ab-8fa2-44886bd0afd0",
        "sr:chapter": {"type": "sr:ChapterContext", "sr:chapterId": 1, "sr:order": 1, "name": "A Small Beginning", "sr:fingerprint": {"type": "sr:Fingerprint", "sr:algorithm": "sha256", "sr:algorithmVersion": "sr-book-document-chapter-v1", "sr:value": "3cfdb8b1ff4a08b274836fded5205374d485351c4c5863c2bf066690391b4cbb"}}
      },
      "sr:kind": "highlight"
    },
    {
      "id": "urn:uuid:6cc4f771-cc56-5a0c-a05c-7c75f9743758",
      "type": "Annotation",
      "motivation": "commenting",
      "creator": {"id": "urn:uuid:95a909f2-658f-50c5-9c2b-8ef0e6dc7512", "type": "Software", "name": "Second Reader"},
      "created": "2026-07-03T08:31:00Z",
      "body": {"type": "TextualBody", "value": "This turns rereading into a deliberate test, not repetition.", "format": "text/plain", "language": "en"},
      "target": {
        "type": "SpecificResource",
        "source": "Text/chapter-01.xhtml",
        "selector": [
          {"type": "TextQuoteSelector", "exact": "Return with a better question.", "prefix": "Do not merely repeat. ", "suffix": " The page may answer differently.", "sr:normalization": "sr-epub-resource-text-v1"},
          {"type": "sr:ParagraphCharSelector", "sr:coordinateSystem": "sr-book-document-paragraph-char-v1", "sr:offsetUnit": "unicode-code-point", "sr:start": {"sr:chapterId": 1, "sr:paragraphIndex": 3, "sr:charOffset": 22}, "sr:end": {"sr:chapterId": 1, "sr:paragraphIndex": 3, "sr:charOffset": 52}}
        ],
        "sr:anchorId": "urn:uuid:006bb1e4-7e83-5d97-98aa-c606207f93f8",
        "sr:chapter": {"type": "sr:ChapterContext", "sr:chapterId": 1, "sr:order": 1, "name": "A Small Beginning", "sr:fingerprint": {"type": "sr:Fingerprint", "sr:algorithm": "sha256", "sr:algorithmVersion": "sr-book-document-chapter-v1", "sr:value": "3cfdb8b1ff4a08b274836fded5205374d485351c4c5863c2bf066690391b4cbb"}}
      },
      "sr:kind": "note"
    }
  ],
  "sr:specVersion": "0.1.0",
  "sr:schemaVersion": "0.1.0",
  "sr:extensionVersion": "0.1",
  "sr:profile": {
    "type": "sr:ProfileReference",
    "sr:webAnnotation": "https://www.w3.org/TR/2017/REC-annotation-model-20170223/",
    "sr:epubAnnotations": "https://www.w3.org/TR/2026/WD-epub-anno-10-20260521/",
    "sr:conformance": "aligned"
  },
  "sr:track": {
    "id": "urn:uuid:04ace963-40ef-5247-90d2-1cc55d925afa",
    "type": "sr:AnnotationTrack",
    "sr:key": "second-reader-agent",
    "name": "Second Reader",
    "creator": {"id": "urn:uuid:95a909f2-658f-50c5-9c2b-8ef0e6dc7512", "type": "Software", "name": "Second Reader"}
  },
  "sr:provenance": {
    "type": "sr:Provenance",
    "sr:producer": "urn:uuid:da94868b-ce7f-56d6-9c77-c5b959f15f5a",
    "sr:adapterVersion": "0.1.0",
    "sr:inputSnapshotDigest": {"type": "sr:Digest", "sr:algorithm": "sha256", "sr:value": "82f72cf3651f3c1c6b96e7a170da1302a7cf0e86bf8d57db37e5ed66005a40d8"},
    "sr:inputSnapshotAlgorithmVersion": "sr-second-reader-input-snapshot-v1"
  },
  "sr:semanticDigest": {
    "type": "sr:Digest",
    "sr:algorithm": "sha256",
    "sr:canonicalization": "sr-canonical-json-v1",
    "sr:value": "6a48c77d9e08a46b3340727932cd35fef7a72486ce4f7b5c521931389f834ce8"
  }
}
```

## 6. W3C Mapping And Second Reader Extensions

### 6.1 固定的官方规范基线

- 稳定语义底座：[W3C Web Annotation Data Model Recommendation, 23 February 2017](https://www.w3.org/TR/2017/REC-annotation-model-20170223/)。
- EPUB profile 固定参考：[EPUB Annotations 1.0 Working Draft, 21 May 2026](https://www.w3.org/TR/2026/WD-epub-anno-10-20260521/)。截至本文日期，这是 W3C history 中最新正式发布的 WD；它仍是 work in progress，不是 Recommendation。Pack v0 不宣称完整 conformant。
- 发布历史与未来复核入口：[EPUB Annotations 1.0 history](https://www.w3.org/standards/history/epub-anno-10/)。`/TR/epub-anno-10/` 和 editor's draft 可漂移，不能替代 dated pin。

Pinned WD 当前规定 detached `.annotations` 为 ISO/IEC 21320-1 ZIP、根文件名 `annotations.json`、外层 media type `application/zip;profile="https://www.w3.org/TR/epub-anno-10/"`。它没有规定自定义 `manifest.json`，所以本设计不发明一个并声称为标准 manifest。

### 6.2 四层字段边界

**A. Direct W3C Web Annotation fields**：`id`, `type`, `creator`, `created`, `motivation`, `body`, `target`, `source`, `selector`, `TextualBody`, `TextQuoteSelector`, `exact`, `prefix`, `suffix`。

**B. Pinned EPUB-profile fields/shape**：顶层 `AnnotationSet`, `about`, `items`, `generator`, `generated`；每条 one creator/one target/one motivation；target source 是 EPUB package manifest item 的 relative href；detached ZIP/root file/media type。

**C. Second Reader extensions**：所有 `sr:*` fields/types，包括三层 publication fingerprint、track identity、native `sr:kind`、quote normalization、paragraph-char selector、chapter context、verified CFI selector、protocol/profile versions、安全 provenance 和 semantic digest。

**D. Implementation-only metadata**：source reaction id/index、input/output paths、run/job status、skip stack、validation timings、package byte digest、private artifact revision。它们只在内存或 sanitized validation report，MUST NOT 出现在 Pack。

### 6.3 为什么不是“严格 EPUB WD conformance”

Pinned WD 的 JSON Schema 章节仍为 `T.B.D.`，privacy/security 章节也为 `T.B.D.`；其 selector 列表比基础 Web Annotation 更窄。尤其：

- `TextQuoteSelector` 是稳定 WA selector，也作为 inherited term被 pinned EPUB WD reference引入，且 TextPosition说明会引用它；但该 WD没有像 Fragment/CSS/TextPosition那样给它独立 normative subsection/完整 field table，profile细节仍不完整。本设计按 WA Recommendation直接采用，并用 `sr:normalization`补足项目 text-stream约定。
- EPUB WD `FragmentSelector.conformsTo` 允许列表不包含 EPUB CFI。基础 WA Recommendation 虽把 EPUB CFI 列为 FragmentSelector 例子，本设计不把 current CFI 伪装成该 EPUB profile FragmentSelector，而用隔离的 `sr:EpubCfiSelector`。
- WD 对 TextPosition counting basis 仍有未决问题；current `SourceSpan` 又是 paragraph-local normalized offsets，不能无损冒充 resource-wide `TextPositionSelector`，因此使用 `sr:ParagraphCharSelector`。
- WD introduction/body table、non-normative generator example 与 normative table 存在 draft 内部张力。本项目固定 Highlight 无 body、Note 一个 TextualBody；generator 按 normative object table实现。

因此 conformance 字段是 `aligned`，而不是 `conformant`。

Note body选择 WA `TextualBody` representation：`value`为普通 string，`language`作为 sibling BCP 47 field。Pinned EPUB WD的 localizable-text示例还展示过把 language/text放入 value object的草案形态；v0不采用那一形态，也不声称这是 EPUB WD localizable-text conformance。未来若 WD收敛，按第 16 节做 dated delta review，不能在 v0中同时接受两种 wire shape。

### 6.4 `sr:` namespace 策略

设计候选 namespace：

```text
https://captain4whale.github.io/second-reader/ns/annotation-pack#
```

规则：

1. namespace 由项目控制，term IRI 不随 schema patch 改路径；协议版本放 `sr:specVersion` / `sr:extensionVersion`。
2. 只扩展标准无法准确表达且当前有消费者需求的语义；能用 WA/DC 的字段不复制成 `sr:`。
3. term 使用 lower camel case；class/selector type 使用 UpperCamelCase。
4. contract 提交 context 文档并固定 SHA-256；validator 不联网拉取 context，只接受 committed allowlist，避免 SSRF/供应链漂移。
5. Adapter-specific data先归一化到 draft，不能新增 `sr:attentionalV2*` wire fields。
6. owner 已确认使用该 namespace 和 GitHub Pages托管。Slice 1提交 allowlisted Pages workflow与可重复 staging check；只有 workflow进入 `main`、Pages部署成功并完成HTTP byte comparison后，才可对外宣称该 IRI 已上线可解析。

本设计不引入 RDF store、JSON-LD expansion/compaction framework。v0 serializer 生成固定 compact JSON-LD；validator 做 JSON Schema + 项目语义检查即可。

## 7. Publication Identity And Fingerprints

### 7.1 Work → Edition → File

```text
WorkIdentity
  └── conceptual work；可能只有 provisional metadata key
      EditionIdentity
        └── 一份 normalized textual/structural content
            FileIdentity
              └── 一组完全相同的 EPUB bytes
```

两个 files SHA-256 相同，才是 exact same file。两个 files 不同但 `sr-book-document-text-v1` 相同，可判断为 same normalized textual edition；不能据此断言出版 metadata、样式、图片等全部相同。两个 editions 只有共享明确 work-level identifier，或经未来显式 mapping，才可判断为 same work；相同可信 ISBN只支持 same publication/manifestation。title/author 相同只能生成 `provisional` candidate，不能作为合并 authority。

### 7.2 `file_sha256`

`FileIdentity.sr:sha256 = lowercase_hex(SHA256(raw_epub_bytes))`：

1. 只解析 manifest 中相对 `source_asset.file`；默认 `_assets/source.epub`。
2. resolved path 必须 containment 在 book output dir 内，且是非 symlink regular file；拒绝绝对路径、`..`、device/FIFO。
3. 验证 ZIP magic、无 unsafe entry、root `mimetype` 内容为 `application/epub+zip`、`META-INF/container.xml` 可解析、rootfile OPF 存在且 target href 在其 manifest。
4. 以 binary streaming 每块 1 MiB 计算 SHA-256 和 byte length；不读 manifest 的声称值。
5. hash 前后比较 file stat，再在 publish 前复核 digest；变化即 `input_changed_during_export` fatal。Exact-source BookDocument reparse必须消费与 digest复核相同的 already-open handle或不可变 bytes snapshot，不能按 pathname重新打开；否则短暂 directory swap再还原会产生 File(A)+Edition(B)的混合 identity。

Pack 不写入本机 source path、mtime、inode 或 upload id。

Identity boundary必须覆盖 verified-handle parse、neutral BookDocument build与 deterministic source normalization整个 exact rebuild阶段。任何来自 verifier-accepted但 parser/builder不可规范处理的 navigation metadata或内容结构异常，除既有 structured `EpubSourceError` / `PublicationIdentityError` 外，都映射为不回显输入的稳定 `source_asset_missing_or_not_epub`；不得把 `ValueError`, Unicode error或第三方 parser exception裸露给调用方。Normal parser路径本身不因该 identity wrapper改变行为。

### 7.3 v0 normalized content fingerprint

v0 **实现** normalized content fingerprint；算法名 `sr-book-document-text-v1`。Edition fingerprint的权威输入是 exact source EPUB 在 export preflight 中重新构建的 in-memory BookDocument；另以第 7.4 节更严格的 substrate projection 对 persisted `public/book_document.json` 做 field-level equivalence。不能只比较本 content digest，也不能使用 `--allow-skips` 绕过 substrate mismatch。实施时应把 current private `_build_book_document()` 提炼为一个无写入、无 LLM、shared deterministic build API，或提供语义等价的 neutral helper；禁止直接调用带“存在即复用”行为的 `_load_or_build_book_document()`。

算法精确定义：

```text
N(s):
  1. convert input to Unicode string
  2. Unicode NFC
  3. normalize CRLF/CR to LF
  4. replace each maximal Unicode White_Space run with U+0020
  5. strip leading/trailing U+0020

FRAME(tag, s):
  b = UTF-8(N(s))
  ASCII(tag) || ":" || ASCII(decimal(len(b))) || ":" || b || LF

STREAM:
  ASCII("SECOND-READER-BOOK-DOCUMENT-TEXT-V1") || LF
  for chapter in BookDocument.chapters list order:
      FRAME("C", chapter.title)
      for paragraph in chapter.paragraphs list order, including normalized-empty records:
          FRAME("P", paragraph.text)
      ASCII("E") || LF

digest = SHA256(STREAM)
```

v0 的 `Unicode White_Space` 不跟随 runtime 的 `re \s` / `str.isspace()` 漂移，而固定为 Unicode White_Space code points：`U+0009..U+000D`, `U+0020`, `U+0085`, `U+00A0`, `U+1680`, `U+2000..U+200A`, `U+2028`, `U+2029`, `U+202F`, `U+205F`, `U+3000`。因此 `U+200B` 与 `U+001C` 不折叠。Chapter stream使用相同的 `C/P/E` framing，包括末尾 `E LF`。

该算法：

- 包含 canonical chapter boundaries 和所有 paragraphs（包括 auxiliary/front/back matter），不以当前 reading eligibility 决定 edition identity；
- 不包含 `chapter_id`, href, CFI, HTML metadata, source path, output language, parser timestamps；
- 对 repackaging/空白差异有一定稳定性，但受 parser 的 chapter/paragraph segmentation 与 TOC-fragment 行为影响；
- 算法改变必须换 `algorithmVersion`，不得在同名 v1 下偷偷修订。

Edition UUID name 是 `edition\0sr-book-document-text-v1\0<digest>`。如果未来新算法认为两个历史 edition 等价，必须通过显式 migration/crosswalk 建立关系，不能重写旧 ID。

### 7.4 Implementation-only substrate equivalence

`sr-book-document-text-v1` 故意排除 chapter id/href/offset-bearing structure，所以它只能定义 Edition identity，**不能**证明 persisted reaction span仍可安全套到 exact EPUB。Export preflight另实现 `sr-book-document-substrate-v1`；该 digest只进入 input snapshot/validation report，不进入可分发 Pack。

其 canonical projection对 source-rebuilt 与 persisted BookDocument分别生成并做 field-by-field equality（digest只用于快速比较）：

```text
header = "SECOND-READER-BOOK-DOCUMENT-SUBSTRATE-V1"
chapters[] in list order:
  list_order
  id
  chapter_number
  title (exact code points)
  normalized chapter href
  item_id / spine_index with explicit null/default normalization
  paragraphs[] in list order:
    list_order
    paragraph_index
    text (exact code points; no NFC/whitespace rewrite)
    normalized href
    text_role (missing -> "body")
    readable = bool(non-empty text and text_role != "auxiliary")
```

Canonical encoding使用以下 frozen typed length frame，null与empty严格区分：

```text
TFRAME(tag, value):
  null   -> ASCII(tag) ":n:0:" LF
  bool   -> ASCII(tag) ":b:1:" ("1" | "0") LF
  int    -> payload = canonical base-10 ASCII with optional leading "-" and no leading zero
            ASCII(tag) ":i:" ASCII(decimal(len(payload))) ":" payload LF
  string -> payload = exact UTF-8 bytes without Unicode/whitespace normalization
            ASCII(tag) ":s:" ASCII(decimal(len(payload))) ":" payload LF

STREAM:
  "SECOND-READER-BOOK-DOCUMENT-SUBSTRATE-V1" LF
  TFRAME("chapterCount", len(chapters))
  for each projected chapter:
    TFRAME("chapter.listOrder", ...)
    TFRAME("chapter.id", ...)
    TFRAME("chapter.chapterNumber", ...)
    TFRAME("chapter.title", ...)
    TFRAME("chapter.href", ...)
    TFRAME("chapter.itemId", ...)
    TFRAME("chapter.spineIndex", ...)
    TFRAME("chapter.paragraphCount", len(paragraphs))
    for each projected paragraph:
      TFRAME("paragraph.listOrder", ...)
      TFRAME("paragraph.paragraphIndex", ...)
      TFRAME("paragraph.text", ...)
      TFRAME("paragraph.href", ...)
      TFRAME("paragraph.textRole", ...)
      TFRAME("paragraph.readable", ...)
```

Missing optional `chapter_number`, `href`, `item_id`, `spine_index` 归一为 null；显式 empty string仍是 empty string。Missing `text_role`归一为 `"body"`；`readable` 中的 non-empty 指 exact code-point length非零，不做 trim。Normalized href 的 exact rule由同 Slice的 strict EPUB path normalizer固定并由 vectors锁定。`start_cfi/end_cfi`、HTML classes、sentences、source-normalization diagnostics不参与 equality，因为 required anchor不依赖它们，且旧 artifacts可合法缺失；optional CFI永远从 exact source现场验证，不信 persisted值。

`normalize_epub_href` 的 v0 exact rule：输入必须是 package-local/OPF-relative href；fragment先移除，最前面的 `./`允许并折叠；各 segment必须是严格 UTF-8 percent decoding，随后 NFC并以 canonical UTF-8 percent encoding输出（raw space变 `%20`，unreserved escape例如 `%7E`变 `~`）。拒绝 scheme/authority、query、absolute或drive path、backslash/NUL、空 segment、内部 `.`、任何 `..`，以及 encoded slash/backslash/NUL。用于 strict OPF manifest的 `normalize_opf_relative_href` 额外拒绝 fragment，并把 canonical href解析为不得逃出 OPF directory的 archive member path。

ebooklib可能把 manifest href中的 `%23` / `%3F` filename字符解码成 literal `#` / `?`。Slice 2 因此用 verified manifest建立有优先级的 resolver：canonical OPF href与 decoded OPF-relative archive name是 primary aliases；full archive member只能是不覆盖 primary的低优先级 fallback。Source-rebuilt与 persisted BookDocument必须先经同一 resolver canonicalize再做 substrate comparison，且合法 nested OPF中一个 item的 canonical href与另一个 item的 full archive path重名时不得误报 ambiguous。

Equality至少保证 reaction所依赖的 `chapter_id + paragraph_index + exact text + readable filtering` 与 target所依赖的 href没有漂移。任一 chapter/paragraph reorder、id/index、exact code point、href或readability变化都产生 `publication_substrate_mismatch` fatal，并在 report中给 first differing JSON pointer与两侧 field digests，不复制正文。老 artifact若失败必须重建/rerun source substrate；不能用 title/content digest相同或 `allow_skips`绕过。

### 7.5 Work 与 publication metadata identity

优先从 verified OPF 读取并规范化 publication identifiers，但严格区分层级：

1. 合法 ISBN-13/ISBN-10（含 check digit）、OPF unique identifier和publication URI进入 `EditionIdentity.sr:publicationIdentifiers`。相同可信 ISBN可强支持“同一 publication/manifestation”；不同 ISBN **不能** 推出不同 Work，因为同一作品的精装、平装、电子版、修订版常有不同 ISBN。
2. 只有显式标注且语义确实指向 abstract work 的 URI/ID进入 `WorkIdentity.sr:identifiers`，并可令 `identityStrength="asserted"`。当前 repo没有这样的 work-level authority，正常 current adapter应输出 provisional Work。
3. 当前 `BookMetadata.book/author` 仅作 display/provisional fallback；OPF 与 BookDocument不一致产生 warning，Pack display优先 verified OPF，validation report记录 sanitized difference。
4. 没有 work-level authority时，work name用 `provisional\0<N(title)>\0<ordered N(creators)>` 生成 deterministic UUID，并标 `identityStrength="provisional"`。Importer MUST NOT 仅因 provisional ID相同而自动合并 Work。

Work identity不纳入 edition/file digest；edition identity不纳入 filename/slug。Publication identifier的新增/纠正可能改变 Edition metadata，但 normalized content相同仍保持同一 `edition_id`；若业务未来需要区分相同正文的不同出版 manifestation，应在 v1增加独立 Manifestation层，而不是滥用 Work。

显式 v0 `work-uri` 只接受 public-safe absolute `http`, `https`, `urn` URI；拒绝 credentials、query secrets/任何 query、`file:`/script schemes、localhost/private/link-local/reserved addresses、local path和 whitespace/control characters。URI与 public display scanner必须在最多四轮 percent decode后达到稳定 NFC text，并在该稳定视图再次执行结构、query、whitespace、path与secret检查；未在界限内稳定或任何轮次产生非法 UTF-8均拒绝，不能让双编码隐藏 query/space/path/secret。OPF/persisted display metadata在进入 wire或 safe rebuilt result前也必须是 string并通过该 scanner；不能把 mapping/list用 Python `repr`字符串化，unsafe optional creator应 sanitized warning + omit，unsafe/missing required title应 fail closed或使用另一个已验证 safe fallback。Verified OPF与 persisted BookDocument中同时存在的合法 title/creator/language不一致时使用 verified值并产生 generic sanitized `publication_metadata_mismatch`；`output_language`不参与 publication metadata比较。

### 7.6 Chapter fingerprints

v0 **实现** `sr-book-document-chapter-v1`。它使用上一算法相同的 `N/FRAME`，stream header 改为 `SECOND-READER-BOOK-DOCUMENT-CHAPTER-V1`，只包含目标 chapter 的 title 与 ordered paragraphs。每章还保存 current BookDocument `chapterId`, list `order`, title 和去重后的 manifest-relative `resourceHrefs`。

用途：检测同一 edition 内 structural drift、帮助 future re-anchoring、在重复 quote 时缩小范围。它不是跨译本/跨 parser 的 universal chapter id。

### 7.7 Preflight identity gates

Pack-level fatal：

- source asset missing/not regular/not EPUB/unsafe ZIP；
- OPF target resource缺失或 path 非法；
- exact-source rebuilt 与 persisted BookDocument 的 `sr-book-document-substrate-v1` projection不同（content digest相同也不能放行）；
- edition/file digest计算期间 input变化；
- title 缺失且没有可用 OPF metadata；
- canonical chapter title不满足 public display metadata gate；该 title参与 content/chapter/substrate fingerprints，不能先用原值计算 identity再在 result中改写或清空，否则 `PublicationIdentityResult`会内部脱节；
- fingerprint algorithm/version 不受当前 validator支持。

现存 v24 eval segment 可能 manifest 宣称 `_assets/source.epub`，实际文件不存在或 source 是 `.txt` segment；这些输出必须得到 `source_asset_missing_or_not_epub`，不能生成一个声称可导入原 EPUB 的 Pack。

## 8. Anchor Model

### 8.1 Multi-anchor responsibilities

| Anchor component | Req | 作用 | Exact-file / re-anchor | 验证 |
|---|---:|---|---|---|
| `target.source` EPUB href | yes | 指向 OPF manifest resource | exact-file primary resource；future edition candidate resource | normalized relative href；必须存在；span 不跨 href |
| `TextQuoteSelector.exact` | yes | 人可读、可搜索的源证据 | exact + future re-anchor | 从 span重建并映射到 verified `sr-epub-resource-text-v1` continuous slice；与 row/source ref三方一致；<=1024 code points |
| `prefix` / `suffix` | yes (可为空) | 同 quote 多次出现时消歧；承受 offset漂移 | future re-anchor | 从同一 verified resource stream现场提取；各默认<=64、schema<=128 |
| `sr:ParagraphCharSelector` | yes | current BookDocument 的精确 end-exclusive坐标 | exact current substrate | 坐标范围、1-based paragraph map、跨段 separator、quote round-trip |
| `sr:EpubCfiSelector` | no | 支持未来 Reader 快速定位 | exact-file optimization only | 必须对 exact EPUB 做 CFI→text round-trip；current lightweight CFI不够 |
| `sr:chapter` | yes | structural narrowing/context | same edition + future hint | chapter id/order/fingerprint必须与 edition list一致 |
| file/content/chapter fingerprints | pack/target层 required | 防止“能解析但绑错书/版/章” | identity gate | importer先匹配 file，再 content，再 structural/quote |

### 8.2 Strict resolution algorithm

`SecondReaderProducerAdapter` 对每条 current-native row 依次执行：

1. 检查 `record_source == "read_surface"` 且 `marginalia_kind in {"highlight","note"}`；不从 `type`, `compat_family`, `thought` 猜 kind。
2. `primary_source_ref.resolution` 必须是 `status="matched"`, `method="exact_text"`, `match_count=1`。`ambiguous_first_match`, normalized/ordered-fragment、missing/fallback 默认全部是 annotation-level invalid。后两种只留给未来显式 repair/migration mode。
3. 用 `SourceSpan.start.chapter_id` 通过 `{chapter.id: chapter}` join；`chapter_ref` 只作诊断，不作 key。start/end chapter 必须相同。
4. 用 `{paragraph.paragraph_index: paragraph}` 映射（不是 list index）解析 1-based index；验证 `0 <= charOffset <= len(paragraph.text)`、start < end、跨段顺序合法。
5. 按 current `source_unit_from_span()` 规则重建：首尾 Python slice、中间整段，以 `\n\n` 拼接。重建结果必须同时等于 `record.source_quote` 和 `primary_source_ref.quote`。
6. 覆盖 paragraphs 的 normalized href 必须同一；该 href 必须精确对应 verified OPF manifest item。
7. 将 span映射到 verified `sr-epub-resource-text-v1` continuous slice并提取 prefix/suffix；不得跨过被 reader过滤掉但存在于 XHTML的 block。若 quote在 resource stream中多次出现，paragraph-char + chapter context仍确定 current anchor，但 report给 `quote_not_unique_in_resource` warning。
8. 生成 anchor/annotation IDs，必要时尝试 verified CFI；CFI失败只 warning并省略，不能让已经可靠的 quote/span失败。

Source-derived `exact/prefix/suffix` 必须保留 persisted BookDocument 中实际 Unicode code-point序列，serializer不得事后做 NFC并让 paragraph-char offsets失配。metadata、creator和Note body在进入 builder时规范化为 NFC；source quote只在 content fingerprint算法的独立 `N(s)` 步骤中做 NFC。实现还应检测 start/end 是否切开 Unicode extended grapheme cluster；strict模式将其记为 `grapheme_boundary_split` annotation error，而不是发布一个视觉上残缺的 selector。

当前 live `_normalize_marginalia_item()` 已要求 quote 是 current unit source text 的 exact substring；v24 抽样绝大多数 records 都是 unique exact match。这使 strict gate 可落地，不需要把通用 fallback 当 normal case。

### 8.3 Verified XHTML resource text stream

仅在 BookDocument里把 paragraphs以 `\n\n`拼接，最多证明“自己的 parser可回查”，不能告诉 detached Reader怎样从 target XHTML得到相同 logical text。v0因此定义并在每个 TextQuoteSelector写入 `sr:normalization="sr-epub-resource-text-v1"`：

1. 从 verified OPF manifest定位 exact `target.source` bytes；必须可作为 XML/XHTML安全解析，失败即 `resource_text_unverifiable`，不走正则/plain-text fallback。
2. document-order遍历 local-name属于 `p, li, blockquote, caption, div, figcaption, h1..h6` 的 elements。
3. element text为 `"".join(element.itertext())`；按 Python Unicode `\s+`语义折叠为一个 U+0020并trim，**不做 NFC**。
4. 对非 heading container：若它有含文本的上述 child block、且自身 direct text（element.text + direct children tails）归一化后为空，则跳过 container，避免与 child重复；这与 current `_extract_epub_paragraph_records()` 的 duplicate-container rule一致。
5. 每个其余非空 block成为一个 resource block；包括以后可能分类成 auxiliary 的 block。logical resource stream以 `\n\n`连接 blocks，并保留 block→code-point range映射。
6. source-rebuilt BookDocument每个 paragraph必须与对应 resource block的 exact text/href/order匹配；span start/end映射到 resource stream后，`exact`必须是一个连续 slice。
7. Current `readable_paragraphs()` 会排除 `text_role="auxiliary"`。如果一个 SourceSpan跨过任何未进入 source unit的非空 resource block，v0拒绝 `non_contiguous_resource_quote`，不把跳跃拼接伪装成 W3C continuous quote。

v0 SourceSpan仍不允许跨 href/chapter。`prefix/suffix` 从 verified resource stream的 exact slice边界截取 code points；这样第三方 Reader只需实现已版本化算法，不需要访问 Second Reader BookDocument。若未来采用浏览器 `innerText` 或标准化 DOM text算法，必须新建 normalization version并评估 offsets/IDs，不能改 v1。

若 parser 的同一 href 被 TOC fragment复制到多个 chapters，adapter 使用 exact `chapter_id + span` 解析，同时报告 `duplicate_resource_chapter_projection` warning。若由此生成完全相同 anchor/annotation ID，strict export 以 duplicate ID fatal，不任意丢一条；这是 parser gap 的可见证据。

### 8.4 CFI 与错误绑定防护

Importer 建议顺序：

1. file SHA-256 exact match：可优先 paragraph-char/verified CFI；
2. file不同但 content fingerprint相同：忽略 CFI，使用 href + quote/context + chapter fingerprint；
3. content fingerprint不同：v0 不自动迁移，只返回 `edition_mismatch`；
4. 即使 CFI 可解析，CFI 解析结果的 normalized quote不等于 `exact` 时，MUST reject该 CFI，不得以“可跳转”视为成功。

Exporter 无法生成可靠 required anchor 时：strict 默认整次 export失败；显式 `allow_skips` 模式可 skip单条并产出 degraded-but-valid Pack。永不截断 quote后继续发布，永不把 whole-unit fallback包装成精确 Highlight/Note。

## 9. IDs And Determinism

### 9.1 UUID strategy

所有 canonical ids 使用 RFC 4122 UUIDv5，并以 `urn:uuid:<lowercase>` 序列化。Slice 2 生成并提交以下独立 namespace UUID constants；一旦 contract 发布不可改变：`WORK_NAMESPACE`, `EDITION_NAMESPACE`, `FILE_NAMESPACE`, `TRACK_NAMESPACE`, `PACK_NAMESPACE`, `ANCHOR_NAMESPACE`, `ANNOTATION_NAMESPACE`, `CREATOR_NAMESPACE`, `GENERATOR_NAMESPACE`。每个 constant 固定为 `UUIDv5(NAMESPACE_URL, "https://captain4whale.github.io/second-reader/ns/annotation-pack/uuid/<kind>/v0")` 的结果，代码硬编码实值、tests复核 derivation与 fixed vectors；不能在 runtime临时换 root/name。

| Namespace constant | Immutable UUID literal |
|---|---|
| `WORK_NAMESPACE` | `e818f38e-2894-5910-a94f-afec1212f840` |
| `EDITION_NAMESPACE` | `82f700a5-7f2d-5c1d-902c-7ff9fe327044` |
| `FILE_NAMESPACE` | `9755ee25-0dad-51a9-a36d-63589e35707c` |
| `TRACK_NAMESPACE` | `011c6a5f-2255-5b98-b86a-8f1a55548652` |
| `PACK_NAMESPACE` | `15a1b369-656b-55cb-bfa1-55a529a1f39e` |
| `ANCHOR_NAMESPACE` | `3a26c857-f475-506c-a16a-219763fd1ce9` |
| `ANNOTATION_NAMESPACE` | `ab5c7848-4a52-5b43-a01b-f76dbce62959` |
| `CREATOR_NAMESPACE` | `e0d4d5df-e315-5db3-9667-3f89a814f602` |
| `GENERATOR_NAMESPACE` | `dc17bd39-4e7c-574f-9aa0-87d4fe7e927b` |

Canonical name 使用 UTF-8、NUL (`\0`) field separator；metadata/track/body等由 builder定义为 NFC，source quote/hash则使用 wire中与 BookDocument坐标一致的原始 code-point序列。禁止依赖 Python repr、dict insertion order、本地 path 或当前时间。

| ID | Canonical name | Stability/change rule |
|---|---|---|
| `work_id` asserted | `work\0asserted\0<sorted scheme:value id 1>\0<sorted scheme:value id 2>...` | 每个 deduplicated identifier是独立 NUL field；相同权威 identifier set稳定；identifier修正会变化 |
| `work_id` provisional | `work\0provisional\0<N(title)>\0<ordered N(creators)>` | metadata相同稳定，但不可当自动 merge authority |
| `edition_id` | `edition\0sr-book-document-text-v1\0<content_sha256>` | normalized textual structure变化即变化；file repack可不变 |
| `file_id` | `file\0application/epub+zip\0sha256\0<file_sha256>` | media type或任一 byte变化即变化；与第 4 节规则一致 |
| `creator_id` current default | `creator\0software\0second-reader-agent\0<creator-contract-major>` | stable config；不从可变 display name生成 |
| `generator_id` current reference | `generator\0software\0second-reader-annotation-pack-exporter\0<generator-contract-major>` | 软件产品 identity稳定；build version另写 `sr:version` |
| `track_id` | `track\0<edition_id>\0<creator_id>\0<track_key>` | edition/creator/logical track变化才变化 |
| `pack_id` | `pack\0<spec-major>\0<edition_id>\0<track_id>` | 同 edition×track在 v0 内稳定；partial/新增 items不换 pack id |
| `anchor_id` | `anchor\0<edition_id>\0<href>\0<chapter_fp>\0<start chapter id>\0<start paragraph index>\0<start char offset>\0<end chapter id>\0<end paragraph index>\0<end char offset>\0<quote_sha256>` | 六个坐标整数各自是独立 NUL field；target/content变化即变化；CFI不参与，避免 optional locator改变 identity |
| `annotation_id` | `annotation\0<track_id>\0<kind>\0<anchor_id>\0<body_sha256-or-empty>` | 同 creator/track语义重复稳定；Note正文变化、kind/anchor变化即新 ID |

v0 不额外序列化 `source_id`：`target.source` 已在 `edition_id` scope内唯一，新增一个无人消费的 wire id只会增加漂移。内部可按 `UUIDv5(EDITION_NAMESPACE, "resource\0" + edition_id + "\0" + href)` 派生，但不是 v0 contract field。current `source_span_id` 和 `reaction_id` 都不是 canonical id。

### 9.2 Repeated export behavior

- 同一 settled input snapshot、schema、creator/track options产生相同 publication/track/pack/anchor/annotation IDs与 `sr:semanticDigest`。
- `generated` 表示真正 serialization time，不参与 IDs或 semantic digest。只有 current revision同时满足相同 semantic digest、相同 input snapshot digest、相同请求 deliverables、pointer/JSON/report现场完整复验，以及 report status/counts/findings与 fresh validation一致，才默认返回 `unchanged`并保留现有 bytes/timestamp。semantic digest单独相同不足以证明幂等；JSON-only current也不能阻止后续 packaged revision生成。
- `--force-regenerate` 可重写 `generated`，但 semantic digest仍相同；golden tests通过 injected clock固定它。
- items按 annotation id排序；AnnotationSet语义上无序，排序只是 SR canonicalization rule。
- 同一 track、anchor、kind、body产生同一 annotation id，应视为 semantic duplicate并 fatal，而不是靠 ordinal造新 ID。
- Pack contents变化时 pack id不变、semantic digest变化；这符合“edition×track”容器身份。未来 snapshot/version history属于 Library层，不塞进 v0。

JSON-only→detached upgrade写死为 byte-preserving path：当 fresh candidate与 current semantic digest相同、fresh/current `sr:inputSnapshotDigest`也相同、current JSON/pointer/report全部复验通过、仅缺 package且 `force_regenerate=False` 时，packager直接包装 current revision的 exact `annotations.json` bytes，不重新注入 clock或 serialize candidate。Current validator必须对该 exact JSON与新 package重新执行完整校验，并从本次 `ValidationResult` finalize一份全新的 deterministic report，`validator_version`一律是 current version；不得把旧 findings/version与新 package结果拼接。若 input snapshot不同或current validator不再接受旧 JSON，则从 fresh candidate重新序列化，或在 invalid时失败。`force_regenerate=True` 也始终从 fresh candidate重新序列化并允许新 `generated`/revision。

### 9.3 `sr:semanticDigest`

semantic projection 从完整 Pack 删除：`generated`, `generator`, `sr:provenance`, `sr:semanticDigest`；将 `items` 按 id排序，再按 `sr-canonical-json-v1`编码，计算 SHA-256。这样 exporter build升级但语义不变时可比较；creator/publication/annotation任何改变都会改变 digest。

`sr:inputSnapshotDigest` 对 producer input使用独立 `sr-second-reader-input-snapshot-v1` framing：

```text
SECOND-READER-INPUT-SNAPSHOT-V1
E:64:<exact source EPUB SHA-256>
B:64:<exact persisted BookDocument bytes SHA-256>
S:64:<sr-book-document-substrate-v1 digest>
L:64:<exact reaction-ledger bytes SHA-256>
R:64:<successful resolved/published source-record digest>
...
```

每一 frame都是 exact ASCII `tag:length:value`加 LF；`R` frames按 `source_record_index`排序，且只覆盖最终成功 anchor-resolved并实际进入 Pack的 rows。Adapter的 `accepted_record_digests`仍包含所有 adapter-accepted drafts，exporter必须在 anchor resolution/skip policy之后缩减为最终 published subset，不能直接照搬。

每个 source-record digest是 strict-parsed单条 row的稳定 JSON bytes SHA-256：object keys按 Unicode code point排序，array保留输入顺序，UTF-8不 escape非 ASCII，无额外空白，保留有限 JSON numbers，末尾一个 LF；source strings不做 NFC。这个 producer-private row编码允许 ignored compatibility payload中的有限 float，因此不是 public `sr-canonical-json-v1`。整个 input snapshot不包含 path、run/job status、clock或creator display。Digest object不写 `sr:canonicalization`；framing名称由 sibling `sr:inputSnapshotAlgorithmVersion`声明。任何 framing字段或row编码变化必须换 v2。

## 10. File And Packaging Format

### 10.1 Development JSON

```text
output/<book_id>/public/annotation-packs/<track_slug>/revisions/<revision_id>/annotations.json
```

它是完整 canonical JSON-LD `AnnotationSet`，不是非标准 manifest。media type：

```text
application/ld+json;profile="http://www.w3.org/ns/anno.jsonld"
```

`track_slug` 只用于安全路径，格式 `<track-key>-<first12(track_uuid_hex)>`；wire identity仍是 `sr:track.id`。`revision_id` 是第 10.3 节 `sr-annotation-publication-revision-v1` 对本 revision完整 deliverable set计算的 lowercase SHA-256；current revision由同级 `current.json`选择。它不能只等于 `annotations.json` SHA-256：否则 Slice 6 的 JSON-only revision 与 Slice 7 对同一 JSON 增加 detached package 时会碰撞，并迫使实现修改一个已经声明 immutable 的目录。

### 10.2 Detached artifact

```text
output/<book_id>/public/annotation-packs/<track_slug>/revisions/<revision_id>/<track_slug>.annotations
```

外层 media type按 pinned WD：

```text
application/zip;profile="https://www.w3.org/TR/epub-anno-10/"
```

v0 ZIP 内容严格为：

```text
/
└── annotations.json
```

Pinned WD允许 note assets，但 v0 不实现 asset body，因此额外 entry 是 validation error。EPUB 本体绝不入包。正式 package 不需要/不允许 EPUB 风格 `mimetype` entry，也不增加自定义 `manifest.json`。

Track root的 `current.json` 是 Second Reader本地发布 pointer，不在 `.annotations` 内，也不是 W3C root manifest。最小 shape：

```json
{
  "schema_version": "annotation-pack-publication-pointer/0.1",
  "track_id": "urn:uuid:04ace963-40ef-5247-90d2-1cc55d925afa",
  "revision_id": "7a7a7a7a7a7a7a7a7a7a7a7a7a7a7a7a7a7a7a7a7a7a7a7a7a7a7a7a7a7a7a",
  "semantic_digest": "8b8b8b8b8b8b8b8b8b8b8b8b8b8b8b8b8b8b8b8b8b8b8b8b8b8b8b8b8b8b8b",
  "annotations_json": "revisions/<revision_id>/annotations.json",
  "annotations_json_sha256": "9c9c9c9c9c9c9c9c9c9c9c9c9c9c9c9c9c9c9c9c9c9c9c9c9c9c9c9c9c9c9c",
  "detached_package": "revisions/<revision_id>/<track_slug>.annotations",
  "detached_package_sha256": "adadadadadadadadadadadadadadadadadadadadadadadadadadadadadadadad",
  "validation_report": "revisions/<revision_id>/validation-report.json",
  "validation_report_sha256": "bebebebebebebebebebebebebebebebebebebebebebebebebebebebebebebe"
}
```

所有 pointer paths必须是track-root-relative、containment-safe，且每个 digest与目标 bytes现场一致。Slice 6在 detached packaging尚未实现时成对省略 `detached_package` / `detached_package_sha256`；不得写不存在的目标。这里的重复 hex只是 shape示意，不是 golden vector；正式 contract example由测试生成真实 digest。

### 10.3 Canonical serialization

`sr-canonical-json-v1`：

- entity-specific builder先完成 normalization：metadata/creator/Note body用 NFC，source-derived exact/prefix/suffix保持与 BookDocument坐标一致；serializer本身绝不改 string；JSON UTF-8，无 BOM；
- object keys按 Unicode code-point lexicographic order；arrays保持协议规定顺序（items预排序、context/selector固定顺序）；
- v0 number domain只接受 `[-(2^53-1), 2^53-1]` 内的 JSON integer；拒绝所有 float（包括 finite、NaN和Infinity），避免把任一 runtime的浮点格式暗中变成协议；
- string原始 code points不做 normalization；`"`、`\\`和 U+0008/U+0009/U+000A/U+000C/U+000D使用 JSON short escapes，其余 U+0000–U+001F使用 lowercase `\\u00xx`，`/`不转义，其余合法 Unicode直接写 UTF-8；lone surrogate拒绝；
- separators为 `,` / `:`，无额外空白，文件末尾一个 LF；
- datetime统一 UTC `YYYY-MM-DDTHH:MM:SSZ`；SHA/UUID lowercase；
- serializer只接受已经 schema + semantic valid 的 document。

Immutable publication revision使用独立 `sr-annotation-publication-revision-v1`：先生成 canonical JSON、optional deterministic package和 canonical validation report；Validation report不得包含 `revision_id`，避免自引用。然后计算：

```text
REV_FRAME(tag, hex_digest_or_empty):
  b = ASCII(lowercase hex digest or empty string)
  ASCII(tag) || ":" || ASCII(decimal(len(b))) || ":" || b || LF

REVISION_STREAM:
  ASCII("SECOND-READER-ANNOTATION-PUBLICATION-REVISION-V1") || LF
  REV_FRAME("J", annotations_json_sha256)
  REV_FRAME("P", detached_package_sha256 or empty)
  REV_FRAME("R", validation_report_sha256)

revision_id = lowercase_hex(SHA256(REVISION_STREAM))
```

这样同一完整 deliverable set有同一 revision；Slice 7为同一 JSON补上 package时会得到新 revision，而不会改写 Slice 6目录。该 digest只定义本地 immutable publication revision，不进入 Pack wire identity或 semantic digest。

ZIP reproducibility 是 **SR project rule**，不是 WD要求：entries排序；root path固定；Unix mode `0644`；不写 extra/comment；ZipInfo timestamp固定 `1980-01-01T00:00:00`；compression `DEFLATED`、level固定。给定相同 `annotations.json` bytes，`.annotations` bytes必须相同。

`validation-report.json`（不在 ZIP 内）记录 `annotations_json_sha256` 和 `package_sha256`。package digest不能自包含，否则形成递归。

### 10.4 Package validation

Validator 分两层：

1. JSON document：size/UTF-8/JSON duplicate keys、JSON Schema、semantic invariants、fingerprint/ID recomputation、private-field scan。
2. ZIP envelope：regular ZIP、exact one safe entry、无 absolute/`..`/symlink/encryption/data descriptor anomaly、entry uncompressed size上限 16 MiB、package size上限 8 MiB、compression ratio上限 100、entry bytes等于 independently validated canonical JSON。

Slice 1–6 可先生成 `annotations.json`，因为 contract/identity/anchor/exporter可独立验证；只有 Slice 7 同时满足 ZIP/extension/root/media/security checks 后，才称“正式 detached `.annotations` artifact”。此前不得仅把 JSON 改扩展名。

## 11. Export Pipeline

### 11.1 Explicit entrypoint

首版提供 callable API 和显式 CLI，不接入 normal reading completion：

```bash
cd reading-companion-backend
.venv/bin/python scripts/export_annotation_pack.py \
  --book-id <book_id> \
  --track-key second-reader-agent \
  --creator-type Software \
  --creator-id urn:uuid:<stable-creator-uuid> \
  --creator-name "Second Reader" \
  --deliverables detached
```

`--deliverables` 只接受 `json | detached`；最终 v0默认 `detached`，其中 detached必然同时保留 development JSON。Slice 6开发阶段必须显式传 `json`。`--book-output-dir` 可供测试/运维显式替代 `--book-id` lookup，但必须 resolved containment 在 configured output root 内，除非 library API由测试注入 isolated root。CLI不接受任意 reaction-record path作为 public normal mode。

### 11.2 Completed / partial / active 定位

1. 通过 existing output-root/book helper定位 `output/<book_id>`，不以 title slug重新推导。
2. 读取 `_runtime/run_state.json.stage`；current `RunStage`的真实 enum是 `ready | parsing_structure | deep_reading | completed | paused | error`：
   - `completed`：strict默认允许；
   - `paused|error`：只有 `--allow-partial` 才允许导出已 settled ledger snapshot；
   - `parsing_structure|deep_reading`：拒绝，避免与 writer竞争；
   - `ready`：默认 `run_not_started`拒绝；只有显式 `--allow-empty`且ledger确为空时才允许空 Track；
   - missing/unknown：normal CLI拒绝，fixture/migration只能调用显式低层 API并记录 policy。
3. stage可能陈旧，不能单独证明没有 writer。Exporter还必须通过 neutral `reading_runtime` job-registry/lease truth确认该 book/output没有有效 active writer/lease；若当前组合逻辑只存在于 `library.runtime_truth`，先提炼 neutral read-only helper，`annotation_pack`不得依赖 Library module。active lease无论stage为何都返回 `active_writer_present` fatal。
4. run state/lease只作 export gate/report，不写入 Pack，也不改变 pack/track id。
5. partial Pack是同一 logical track 的当前 snapshot；后续完成后重复 export保持 pack id、增加 items/改变 semantic digest。它不在 wire里标 `partial`，因为 job status被明确排除。

### 11.3 End-to-end steps

1. **Resolve**：解析 output dir与 deterministic track slug；检查上一个 public Pack但不覆盖。
2. **Snapshot**：读取 persisted BookDocument bytes、reaction ledger bytes、run-state gate；记录 SHA-256。只读 `_mechanisms/attentional_v2/runtime/reaction_records.json`，不读 read/settlement audit。
3. **Verify source**：从 manifest安全相对 pointer定位 `_assets/source.epub`；做第 7 节 EPUB/OPF/file hash检查。
4. **Verify substrate**：从 exact EPUB无写入重建 BookDocument；比较 `sr-book-document-substrate-v1` field projection，另计算 content fingerprint；验证 every target href。
5. **Load producer rows**：要求 ledger envelope/version受支持；只选 `record_source="read_surface"` 且显式 native `marginalia_kind`。legacy rows成为 `unsupported_legacy_record` invalid；不从 compatibility aliases升级。
6. **Normalize current compatibility sidecars**：`type`, `compat_family`, `compatibility_section_ref`, `prior_link`, search/lineage fields全部 drop；可检查 native kind与expected compat projection是否自洽并 warning，但它们永不决定 output。
7. **Map drafts**：Highlight要求 empty `thought`；Note要求 non-empty `thought`；`created_at`有效；提取 primary ref。Understanding/response/selection reason/memory/traces均无输入通道。
8. **Resolve anchors**：按第 8 节 join BookDocument，三方 quote核对，生成 context/href/chapter/optional verified CFI。
9. **Build identity/track/items**：现场 fingerprints、UUIDv5、creator equality；排序/deduplicate。
10. **Validate**：schema、semantic、identity、privacy；先生成不含 artifact digests 的 `ValidationResult`。strict有任一 invalid row即失败；`--allow-skips` 才能跳过 annotation-level invalid。
11. **Recheck snapshot**：重新 hash BookDocument/reaction ledger/source EPUB；任一变化 fatal。
12. **Idempotency/upgrade check**：安全读取 `current.json`及其 revision，复算 pointer声明的所有 digest；只有 semantic digest相同且 current具备 `ExportPolicy.deliverables`要求的完整 deliverable set时才返回 `unchanged`。要求 `detached`而 current仍是 JSON-only时，若非 force且所有复验通过，选定 current exact JSON bytes走第 9.2 节 byte-preserving package upgrade；否则使用 fresh candidate bytes。
13. **Serialize/package/report finalize**：在 `revisions/` 同 filesystem写 unique temp revision，生成所要求的 JSON/optional ZIP并完成 package validation；把最终 JSON/package digests注入 `finalize_validation_report()`，生成 schema-valid deterministic report；再按 `sr-annotation-publication-revision-v1` 计算 `revision_id`，fsync每个file和directory。
14. **Publish immutable revision**：将 temp rename到尚不存在的 `revisions/<revision_id>/`；若已存在，只能在逐byte/digest完全相同时复用，否则 fatal。此步骤不覆盖非空目录。
15. **Atomic pointer switch**：写/validate/fsync `current.json.tmp-<nonce>`，再以单文件 `os.replace()`替换 `current.json`并fsync track root。crash发生在切换前仍指旧完整revision，切换后只指新完整revision；不存在混合版本窗口。失败报告单独以同样方式替换 `last-failed-validation-report.json`，绝不移动旧pointer。

### 11.4 Invalid rows, partial and empty policy

- 默认 `strict=True`：一条 invalid annotation导致整次 export失败；warnings不阻塞。
- `--allow-skips`：仅 annotation-level errors可 skip，至少剩一条 valid item时发布 `degraded-but-valid` Pack；report含 counts/codes与 source row index/hash，不含 private内容/path。
- pack-level identity/schema/security/private-leak错误永远不能降级。
- partial 与 skip是两种独立许可：`--allow-partial` 不等于 `--allow-skips`。
- empty current track默认 `empty_track` failure；显式 `--allow-empty` 才把同一 `empty_track` finding降为 warning并发布合法 `items: []`。它适合 contract/integration，不应被误作“Agent无观点”的质量结论。

### 11.5 Public artifact layout

```text
output/<book_id>/public/annotation-packs/<track_slug>/
├── current.json
├── last-failed-validation-report.json          # only after a failed attempt
└── revisions/
    └── <revision_id>/
        ├── annotations.json
        ├── <track_slug>.annotations
        └── validation-report.json
```

Revision directories immutable；自动GC/retention不在v0，避免误删仍被pointer/外部流程引用的artifact。`validation-report.json` 是 local product-operational companion，不在 detached package，默认 Library/Reader分发跟随 `current.json`后只选择 `.annotations`。正式 Library/API discovery不在本 Epic。

## 12. Proposed Python API

以下签名是 implementation contract，不是本轮代码。Wire bindings由 canonical JSON Schema生成；domain draft/input types是手写 producer-neutral dataclasses，不承载重复的 wire validation规则。

```python
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Literal

JSONValue = None | bool | int | str | list["JSONValue"] | dict[str, "JSONValue"]

@dataclass(frozen=True)
class CreatorInput:
    id: str
    type: Literal["Software", "Person", "Organization"]
    name: str

@dataclass(frozen=True)
class SourceCoordinate:
    chapter_id: int
    paragraph_index: int
    char_offset: int

@dataclass(frozen=True)
class SourceRange:
    start: SourceCoordinate
    end: SourceCoordinate

@dataclass(frozen=True)
class AnnotationDraft:
    kind: Literal["highlight", "note"]
    source_range: SourceRange
    source_quote: str
    body_text: str | None
    created_at: datetime
    source_record_index: int       # diagnostics only; never serialized
    source_record_digest: str      # diagnostics only; never serialized

@dataclass(frozen=True)
class ResolvedAnnotationDraft:
    kind: Literal["highlight", "note"]
    body_text: str | None
    created_at: datetime
    target: "ResolvedAnchor"
    source_record_index: int       # diagnostics only; never serialized
    source_record_digest: str      # diagnostics only; never serialized

@dataclass(frozen=True)
class ResolvedAnchor:
    anchor_id: str
    href: str
    exact: str
    target: Mapping[str, JSONValue]  # complete canonical AnnotationTarget
    findings: tuple["ValidationFinding", ...]

@dataclass(frozen=True)
class IdentityFinding:
    code: str
    message: str
    json_pointer: str | None = None
    severity: Literal["warning"] = "warning"

@dataclass(frozen=True)
class EpubManifestIndex:
    opf_path: str                   # safe EPUB-internal path, never local path
    manifest_hrefs: frozenset[str]
    text_resource_hrefs: frozenset[str]  # XHTML/HTML subset eligible for chapters

@dataclass(frozen=True)
class EpubResourceIndex:
    manifest: EpubManifestIndex
    resource_texts: Mapping[str, str]  # sr-epub-resource-text-v1
    paragraph_ranges: Mapping[tuple[int, int], tuple[str, int, int]]
    unverifiable_hrefs: frozenset[str]  # parsed/mapping-incoherent resources; anchors fail closed

@dataclass(frozen=True)
class PublicationIdentityResult:
    wire: Mapping[str, JSONValue]   # complete canonical `about` object
    rebuilt_book_document: Mapping[str, Any]  # in-memory only; source_file is fixed safe relative ref
    epub_index: EpubResourceIndex
    file_sha256: str
    content_sha256: str
    substrate_sha256: str
    chapter_fingerprints: Mapping[int, str]
    findings: tuple["IdentityFinding", ...]  # sanitized warnings only

@dataclass(frozen=True)
class ProducerDraftResult:
    drafts: tuple[AnnotationDraft, ...]
    reaction_ledger_sha256: str
    accepted_record_digests: tuple[str, ...]
    findings: tuple["ValidationFinding", ...]
    input_count: int

@dataclass(frozen=True)
class GeneratorInput:
    id: str
    name: str
    version: str

@dataclass(frozen=True)
class ProvenanceInput:
    producer: str
    adapter_version: str
    input_snapshot_digest: str
    input_snapshot_algorithm_version: Literal["sr-second-reader-input-snapshot-v1"]

@dataclass(frozen=True)
class ExportPolicy:
    deliverables: Literal["json", "detached"] = "detached"  # detached implies JSON + package
    allow_partial: bool = False
    allow_skips: bool = False
    allow_empty: bool = False
    force_regenerate: bool = False

@dataclass(frozen=True)
class ValidationFinding:
    code: str
    severity: Literal["fatal", "error", "warning", "skipped"]
    source_record_index: int | None
    json_pointer: str | None
    annotation_id: str | None
    source_record_digest: str | None
    message: str

@dataclass(frozen=True)
class ValidationResult:
    schema_version: str
    validator_version: str
    status: Literal["valid", "degraded", "failed"]
    pack_id: str | None
    semantic_digest: str | None
    input_snapshot_digest: str | None
    input_count: int
    exported_count: int
    skipped_count: int
    warning_count: int
    error_count: int
    findings: tuple[ValidationFinding, ...]

@dataclass(frozen=True)
class ValidationContext:
    input_count: int | None = None
    findings: tuple[ValidationFinding, ...] = ()
    allow_empty: bool = False

@dataclass(frozen=True)
class ValidationReport:
    schema_version: str
    validator_version: str
    status: Literal["valid", "degraded", "failed"]
    pack_id: str | None
    semantic_digest: str | None
    input_snapshot_digest: str | None
    annotations_json_sha256: str | None
    package_sha256: str | None
    input_count: int
    exported_count: int
    skipped_count: int
    warning_count: int
    error_count: int
    findings: tuple[ValidationFinding, ...]

@dataclass(frozen=True)
class ExportResult:
    status: Literal["published", "degraded", "unchanged", "failed"]
    pack: "AnnotationPackDocument | None"
    annotations_json: Path | None
    detached_package: Path | None
    validation: ValidationResult
    validation_report: Path | None
    current_pointer: Path | None
    revision_id: str | None

@dataclass(frozen=True)
class PackageResult:
    path: Path
    sha256: str
    byte_length: int
    annotations_json_sha256: str

@dataclass(frozen=True)
class InspectionResult:
    valid: bool
    pack_id: str | None
    track_id: str | None
    semantic_digest: str | None
    item_counts: Mapping[str, int]
    anchor_capabilities: tuple[str, ...]
    findings: tuple[ValidationFinding, ...]
```

Slice 2 的 `EpubManifestIndex` 只证明 safe OPF/manifest membership与 chapter资源属于 XHTML/HTML subset；Slice 3 才从它构建 `sr-epub-resource-text-v1` 与 paragraph ranges，不能用 empty mapping伪装已实现。Strict verifier持有的 local `Path`/stat snapshot是 builder-scope private handle，不进入 `PublicationIdentityResult`；result内用于后续 anchor resolution 的 rebuilt BookDocument把 `metadata.source_file` 固定成 verified manifest-relative source reference（canonical current layout为 `_assets/source.epub`）。Unsafe canonical chapter title必须在构建 result前 fail closed；不能在计算 substrate/content/chapter fingerprints后改写返回文档。成功 result的 rebuilt BookDocument必须仍能重算出 result中的全部三类 digest，并从 repr隐藏整份 BookDocument以避免日志复制正文。递归 privacy tests必须证明 local-path-shaped navigation metadata不进入 wire或成功 result。`wire`与 rebuilt BookDocument在 result内递归只读，避免 gate通过后被调用方修改而令 identity/anchors脱节；只读容器仍必须被 JSON encoder、JSON Schema与 generated bindings直接接受。

### 12.1 Core classes

```python
class PublicationIdentityBuilder:
    def build(
        self,
        *,
        output_dir: Path,
        persisted_book_document: Mapping[str, Any],
        manifest: Mapping[str, Any] | None = None,
        source_asset_file: str | None = None,
        work_identifiers: Sequence[tuple[str, str]] = (),
    ) -> "PublicationIdentityResult": ...

class AnchorBuilder:
    def resolve(
        self,
        *,
        draft: AnnotationDraft,
        publication: "PublicationIdentityResult",
    ) -> ResolvedAnnotationDraft: ...

class AnnotationPackBuilder:
    def __init__(self, *, id_factory: "DeterministicIdFactory", clock: "Clock") -> None: ...

    def build(
        self,
        *,
        publication: "PublicationIdentityResult",
        track_key: str,
        track_name: str | None,
        creator: CreatorInput,
        annotations: Sequence[ResolvedAnnotationDraft],
        generator: "GeneratorInput",
        provenance: "ProvenanceInput",
    ) -> "AnnotationPackDocument": ...

class SecondReaderProducerAdapter:
    def load_drafts(
        self,
        *,
        output_dir: Path,
    ) -> "ProducerDraftResult": ...
```

`SecondReaderProducerAdapter` 只可 import `attentional_v2.storage.reaction_records_file` 这个 path helper，并在 producer module内读取 exact支持版本的 JSON envelope；它不接收 BookDocument或export policy，public return type只能是上面的中性 dataclasses。`ProducerAdapterError`只从 catalog code重建固定 fatal finding，不能接受 caller-supplied message/finding。`AnchorBuilder` 只使用同一个已经通过 substrate-equivalence gate 的 `PublicationIdentityResult.rebuilt_book_document` 与 `epub_index`，不再接受调用方传入另一份可漂移的 BookDocument/index。`AnnotationPackBuilder`, `AnchorBuilder`, identity/validation/serialization modules绝不能 import mechanism package。

### 12.2 Functional API

```python
def validate_pack(
    document: Mapping[str, JSONValue],
    *,
    mode: Literal["strict", "compatible"] = "strict",
    verify_ids: bool = True,
    context: ValidationContext | None = None,
) -> ValidationResult: ...

def finalize_validation_report(
    result: ValidationResult,
    *,
    annotations_json_sha256: str | None,
    package_sha256: str | None,
) -> ValidationReport: ...

def serialize_pack(
    pack: "AnnotationPackDocument | Mapping[str, JSONValue]",
    *,
    canonicalization: Literal["sr-canonical-json-v1"] = "sr-canonical-json-v1",
) -> bytes: ...

def package_detached_annotations(
    annotations_json: bytes,
    destination: Path,
    *,
    reproducible: bool = True,
) -> "PackageResult": ...

def inspect_annotation_pack(
    source: Path,
    *,
    verify_package: bool = True,
) -> "InspectionResult": ...

def export_annotation_pack(
    *,
    output_dir: Path,
    track_key: str,
    creator: CreatorInput,
    policy: ExportPolicy = ExportPolicy(),
    generated_at: datetime | None = None,
) -> ExportResult: ...
```

`deliverables="json"` 表示只要求 revision内有 `annotations.json`；`deliverables="detached"` 表示 JSON和正式 `.annotations` 都必须存在，不能表达 package-only。完成 v0后 CLI/API默认 `detached`；Slice 6尚未实现 packaging 时，CLI必须显式使用 `--deliverables json`，请求 `detached`返回稳定的 `deliverable_not_implemented`，不得静默降级。`validate_pack()` 返回尚不声称 artifact digest的 frozen `ValidationResult`；只有 serialize/package及其校验完成后，`finalize_validation_report()` 才创建 final frozen report，禁止先造半成品 report再 mutation。`serialize_pack()` 不自行修复 invalid object；`package_detached_annotations()` 不重新解释 producer data；`export_annotation_pack()` 是唯一 orchestrator。Clock/ID factory可注入，使 tests deterministic。所有 disk writes集中在 exporter/package层，builder/validator保持 pure。

## 13. Schema Authority And Drift Prevention

### 13.1 选择：JSON Schema canonical，Python bindings generated

Source of truth 选择：

```text
contract/annotation-pack/v0/schema/annotation-pack.schema.json
```

理由：

- contract 已被接受为独立于 backend implementation 的根目录 bounded module；JSON Schema适合 Python以外的 Reader/Library消费者。
- pinned EPUB WD 当前 JSON Schema 仍为 `T.B.D.`，所以本文件明确是 **Second Reader profile schema**，不是 W3C official schema。
- 当前 backend使用 Pydantic 2，但若把 backend model当 authority，会让外部 contract依赖实现包；反向生成更符合现有 OpenAPI snapshot/contract-check思路。
- schema处理 wire fields、required/enums/limits；额外跨字段、ID/fingerprint/package安全规则由 semantic validator实现并在 contract README列出。README不得重新定义字段表。

Schema draft固定为 JSON Schema 2020-12，带稳定 `$id`：

```text
https://captain4whale.github.io/second-reader/schema/annotation-pack/v0/annotation-pack.schema.json
```

owner 已确认它与 namespace URL 使用 GitHub Pages托管；在 workflow进入 `main`、Pages部署和HTTP byte comparison完成前仍不得对外宣称已上线可解析。

### 13.2 Committed and generated artifacts

Canonical/hand-authored：

- `contract/annotation-pack/v0/schema/annotation-pack.schema.json`
- `contract/annotation-pack/v0/schema/publication-pointer.schema.json`（local publication auxiliary；不参与 Pack wire bindings）
- `contract/annotation-pack/v0/schema/validation-report.schema.json`（local validation auxiliary；不参与 Pack wire bindings）
- `contract/annotation-pack/v0/context/second-reader-annotation-context.jsonld`
- `contract/annotation-pack/v0/README.md`（只写语义/invariants/版本流程并链接 schema）
- contract examples。

Generated/committed但不可手改：

- `reading-companion-backend/src/annotation_pack/_generated_models.py`：从 schema 生成的 Pydantic 2 wire bindings；文件头写 source digest/tool version。
- `reading-companion-backend/src/annotation_pack/resources/annotation-pack.schema.json`：canonical schema 的 byte-for-byte runtime copy，便于 wheel/offline validator；不是第二 authority。
- `reading-companion-backend/src/annotation_pack/resources/publication-pointer.schema.json`：pointer auxiliary schema 的 byte-for-byte runtime copy；不生成 Pydantic wire model。
- `reading-companion-backend/src/annotation_pack/resources/validation-report.schema.json`：report auxiliary schema 的 byte-for-byte runtime copy；不生成 Pydantic wire model。

Hand-authored Python domain types（`drafts.py`）仅表达 adapter→builder 的中性 input，不镜像 JSON wire contract；它们可以独立演进但最终必须过 canonical schema。

Codegen技术决策现已固定，不是 open confirmation：Slice 1使用 [`datamodel-code-generator==0.74.0`](https://pypi.org/project/datamodel-code-generator/0.74.0/) 作为 dev-only generator，目标 `pydantic_v2.BaseModel` / Python 3.11。该版本在本文日期的官方 PyPI metadata声明支持 Python 3.11和JSON Schema→Pydantic v2；版本升级必须作为显式 generated-diff review，不能使用 floating latest。

### 13.3 Generation and checks

`reading-companion-backend/scripts/generate_annotation_pack_bindings.py`：

1. 读取 canonical Pack schema与pointer/report auxiliary schemas；
2. 以固定参数调用 local-only `datamodel-codegen`：`--input-file-type jsonschema --output-model-type pydantic_v2.BaseModel --target-python-version 3.11 --snake-case-field --use-standard-collections --use-union-operator --formatters builtin`；禁止 remote refs；
3. 规范 header/format并复制三个 exact runtime schemas；只有 Pack schema生成 bindings，且生成结果必须为 `@context` / `sr:*`保留 serialization aliases；
4. 默认写入，`--check` 只生成到 temp并 byte diff；
5. 任何 drift返回非零，不悄悄改文件。

新增：

```make
annotation-pack-contract-check:
	cd reading-companion-backend && .venv/bin/python scripts/generate_annotation_pack_bindings.py --check
	cd reading-companion-backend && .venv/bin/python scripts/validate_annotation_pack.py ../contract/annotation-pack/v0/examples/*.json
	cd reading-companion-backend && .venv/bin/pytest tests/annotation_pack/test_contract.py -q
```

根 `make contract-check` 调用该 target；CI不依赖网络 context fetch。`pyproject.toml` 显式声明 runtime `jsonschema>=4.23,<5` 和 dev-only `datamodel-code-generator==0.74.0`，不能依赖传递安装。Pydantic binding是construction/IDE convenience；runtime validity始终由 canonical `jsonschema` + semantic validator决定。

Drift prevention tests：

- canonical Pack/pointer/report schema SHA分别等于各自 runtime copy，Pack schema SHA另等于 generated file header；
- regenerate-to-temp diff clean；
- every committed example经 JSON Schema + semantic validator；
- generated model可 load/dump examples，alias保持 `@context` / `sr:*`；dump结果再过 canonical validator；declared unknown prefixed extension不能被悄悄丢弃或改名；
- README只引用 schema pointers/version，不维护第三份字段清单；
- schema `$id`, `sr:schemaVersion`, directory version, generated package version一致。

### 13.4 Version update process

1. 先分类 additive optional / breaking / fingerprint algorithm change。
2. 修改 canonical schema/context与 `CHANGELOG.md`；若是 breaking，建 `v1/`，不原地覆盖 `v0/`。
3. regenerate bindings/runtime schema。
4. 更新 examples + positive/negative fixtures + migration note。
5. 运行 annotation-pack contract check、完整 root contract/agent checks。
6. 若 standards pin变化，另做 conformance delta review并更新 `DEC-*`；不能自动追随 latest URL。

## 14. Validation And Error Semantics

### 14.1 Severity and outcome

| Severity | Meaning | Default outcome | `allow_skips` outcome |
|---|---|---|---|
| `fatal` | Pack/source/package级不可信或安全失败 | no Pack | 仍 no Pack |
| `error` | 一条 annotation无法形成 valid canonical item | strict整次失败 | skip该 row；若仍有 item则 degraded Pack |
| `warning` | Pack仍正确，但存在可解释限制 | valid Pack + report | 同左 |
| `skipped` | explicit degraded mode 已排除一条 row | 不适用 | degraded Pack + report |

`degraded-but-valid` 意味着发布的 JSON本身完全满足 schema/semantic invariants，只是 input不是全量；绝不意味着把 malformed anchor留在 Pack。

### 14.2 Required error catalog

| Code / case | Scope | Severity | Rule |
|---|---|---:|---|
| `schema_version_unsupported` / schema mismatch | pack | fatal | validator不支持 exact major/version，不猜测 |
| `source_asset_missing_or_not_epub` | pack | fatal | 不存在、非 regular、安全/EPUB结构失败 |
| `publication_substrate_mismatch` | pack | fatal | source-rebuilt与persisted BookDocument的anchor-bearing substrate projection不同；content digest相同也不豁免 |
| `publication_identity_missing` | pack | fatal | file/content identity/title minimum不足 |
| `input_changed_during_export` | pack | fatal | snapshot recheck失败 |
| `reaction_ledger_unavailable` | producer input | fatal | ledger missing、symlink/non-regular、全路径no-follow或安全打开失败 |
| `reaction_ledger_invalid_json` | producer input | fatal | BOM、UTF-8、duplicate key、NaN/Infinity或strict JSON解析失败 |
| `reaction_ledger_schema_unsupported` | producer input | fatal | envelope keys/schema/mechanism version不等于exact支持版本 |
| `reaction_ledger_limit_exceeded` | producer input | fatal | byte/record/depth/node/string/single-row任一安全上限超出；不得row-skip |
| `active_writer_present` | pack | fatal | neutral job/lease truth显示当前仍有有效 writer |
| `run_state_not_exportable` | pack | fatal | current RunStage不满足 completed/explicit partial/explicit empty policy |
| `deliverable_not_implemented` | export | fatal | 当前 slice/runtime不支持请求的 explicit deliverables；不得静默降级 |
| `publication_pointer_invalid` | publication | fatal | pointer schema/path/declared digest/revision framing任一不一致 |
| `validation_report_invalid` | publication | fatal | report schema/status/count/canonical bytes与revision场景不一致 |
| `duplicate_pack_or_track_id_semantics` | pack | fatal | id重算或track invariant失败 |
| `duplicate_annotation_id` / `duplicate_anchor_semantics` | pack | fatal | 不用 ordinal隐藏重复/冲突 |
| `private_field_leakage` | pack | fatal | forbidden key/value/path/mechanism marker出现 |
| `invalid_generated_timestamp` | pack | fatal | 顶层 timestamp非 UTC RFC3339 |
| `unsupported_kind` | row | error | 不是 explicit highlight/note |
| `unsupported_legacy_record` | row | error | 缺 current native discriminator/source shape |
| `invalid_annotation_timestamp` | row | error | missing/invalid `created_at` |
| `highlight_body_present` | row | error | highlight thought/content非空 |
| `note_body_missing` | row | error | note正文空或超限 |
| `malformed_source_span` | row | error | chapter/paragraph/char非法或跨chapter |
| `grapheme_boundary_split` | row | error | start/end切开 Unicode extended grapheme cluster |
| `cross_resource_span` | row | error | covered paragraphs href不同 |
| `resource_text_unverifiable` | row | error | target XHTML无法按 `sr-epub-resource-text-v1`安全解析/映射 |
| `non_contiguous_resource_quote` | row | error | SourceSpan跳过了XHTML中存在的block，不能表示为continuous TextQuote |
| `unresolved_source_quote` | row | error | fallback/missing/三方quote不一致 |
| `ambiguous_source_quote` | row | error | `ambiguous_first_match` / match_count≠1 |
| `source_quote_too_long` | row | error | exact超过1024，不截断 |
| `target_href_not_in_manifest` | row | error | source不在verified OPF |
| `cfi_unverified` | selector | warning | 省略 CFI，不使可靠主anchor失败 |
| `quote_not_unique_in_resource` | selector | warning | paragraph-char仍唯一，提示未来重锚风险 |
| `unknown_declared_extension` | field | warning | compatible模式保留/忽略，不改变core语义 |
| `empty_track` | pack | fatal/default | 只有显式 `allow_empty` 降为 warning并发布空 items |
| `package_entry_invalid` / ZIP bomb/path traversal | package | fatal | 不读取/发布不安全 package |

### 14.3 Private-field leakage scanner

JSON Schema的 `additionalProperties/patternProperties` 不能单独防止已声明 extension value泄密。semantic validator深度扫描：

- forbidden keys/normalized terms：`understanding`, `selection_reason`, `prompt`, `chain_of_thought`, `reasoning`, `reading_memory`, `recent_reading_memory`, `unit_memory`, `settlement_audit`, `job_status`, `reading_progress`, `reaction_id`, `compat_family`, `search_results` 等；
- forbidden path fragments：`/_mechanisms/`, `/_runtime/`, `state/library_sources`, `state/uploads`；
- POSIX absolute path、Windows drive/UNC path、`file://` URL、home expansion、secret-like query/token；
- package仅允许 expected keys/declared prefixes，任何 extension object也受size/depth/string限制。

Scan不把普通 quote中偶然出现一个单词判为泄漏；它检查 field names和 path/token形态。测试必须覆盖 false positive/negative。

### 14.4 Machine-readable `validation-report.json`

```json
{
  "schema_version": "annotation-pack-validation-report/0.1",
  "validator_version": "0.1.0",
  "status": "degraded",
  "pack_id": "urn:uuid:30ce5020-b141-5900-8be1-641b61ab8a71",
  "semantic_digest": "8b8b8b8b8b8b8b8b8b8b8b8b8b8b8b8b8b8b8b8b8b8b8b8b8b8b8b8b8b8b8b",
  "input_snapshot_digest": "82f72cf3651f3c1c6b96e7a170da1302a7cf0e86bf8d57db37e5ed66005a40d8",
  "annotations_json_sha256": "9c9c9c9c9c9c9c9c9c9c9c9c9c9c9c9c9c9c9c9c9c9c9c9c9c9c9c9c9c9c9c",
  "package_sha256": "adadadadadadadadadadadadadadadadadadadadadadadadadadadadadadadad",
  "counts": {"input": 10, "exported": 9, "skipped": 1, "warnings": 0, "errors": 0},
  "findings": [
    {
      "code": "ambiguous_source_quote",
      "severity": "skipped",
      "source_record_index": 7,
      "source_record_digest": "cdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcd",
      "json_pointer": null,
      "annotation_id": null,
      "message": "Source quote did not resolve uniquely."
    }
  ]
}
```

Canonical auxiliary schema是 `contract/annotation-pack/v0/schema/validation-report.schema.json`；它与 pointer schema一样不定义 Pack wire，也不生成 Pydantic Pack binding。`ValidationResult` 不是可落盘报告；`finalize_validation_report()` 在 JSON/package bytes及其校验结果都已确定后一次性构造 frozen `ValidationReport`。`package_sha256` 只要非 null，`annotations_json_sha256` 就必须同时是有效 digest，不能产生只声称 package 而不绑定其中 JSON 的报告。`status` 只允许 `valid | degraded | failed`：immutable revision里的 `validation-report.json` 只能是 `valid | degraded`；`failed` 只能写 track root的 `last-failed-validation-report.json`。Repeated export的 `unchanged` 只属于 `ExportResult.status`，返回既有 revision report path，绝不修改 report或创建“unchanged revision”。

Report bytes使用 `sr-annotation-validation-report-json-v1`：所有 entity strings先按各自 domain rule normalization；object keys按 Unicode code point排序；无额外空白；末尾一个 LF。`findings` 在 serialize前按 `(severity_rank, code, source_record_index_or_-1, json_pointer_or_empty, annotation_id_or_empty, source_record_digest_or_empty, message)` 排序，其中 rank固定 `fatal=0,error=1,skipped=2,warning=3`；`counts` 由排序前集合重算，不能由 caller声称。Schema用 conditionals要求 published report有 pack/semantic/JSON digest，JSON-only report的 `package_sha256=null`，packaged report必须是64-hex package digest；failed preflight允许这些 fields为null。

Revision report禁止 wall-clock、duration、host、PID、path、stack或 unordered diagnostics；message使用按 error code固定的英文模板，动态 detail只能是安全 enum/index/digest。这样同一 validator version + inputs + deliverables产生 byte-identical report。Report不含 source quote/body、绝对路径、reaction id或stack trace。成功时写 immutable revision内的 `validation-report.json`；失败时保留上一个 valid Pack并原子替换 `last-failed-validation-report.json`，便于诊断而不伪装成新发布。

建议 CLI exit codes：`0` valid/unchanged，`10` explicit degraded publish，`20` validation rejected，`30` source/environment preflight，`40` package/security，`70` unexpected internal error。stdout可输出一行 summary JSON；详细报告写文件。

## 15. Copyright And Data-Minimization Boundary

这不是法律结论，而是工程最小化规则：

- `.annotations` MUST NOT 包含 EPUB file、XHTML、完整 paragraph/chapter、cover或其他 source assets。
- `TextQuoteSelector.exact`最多 1024 Unicode code points；超限 annotation失败，不截断后假装同一 anchor。
- exporter默认 prefix/suffix各最多 64 code points，schema硬上限各128；从 source现场生成，不信任 producer附带上下文。
- quote + prefix + suffix总 source excerpt硬上限1280 code points；即使 paragraph更长也不复制其余内容。
- Note body是 creator留下的批注，最大16384 code points；不得把整章通过 note body绕过 source excerpt限制。明显等于/覆盖大段 source text时给 `body_looks_like_source_copy` warning/error policy测试。
- Pack metadata只保留 title/creator/language/public identifiers/fingerprints；`source_file`, local slug/upload id, username, home path, runtime artifact path全部剔除。
- Person creator只输出用户显式同意的 public id/name；email、account id、credential不作为默认字段。
- validator不通过网络dereference creator/context/target，避免隐私泄漏和 SSRF。
- fixture必须是项目原创短文或明确 CC0/public-domain 微型内容，附 provenance/license README；不能复制 ignored `state/library_sources`、private eval books或现有输出中的长 quote。
- validation report默认也不重复 quote/body，避免 sidecar二次扩散。

## 16. Versioning And Compatibility

### 16.1 Independent version axes

| Axis | v0 initial | Meaning | Change rule |
|---|---|---|---|
| `sr:specVersion` | `0.1.0` | protocol semantics | additive optional→minor；breaking→new major/directory |
| `sr:schemaVersion` | `0.1.0` | exact JSON Schema contract | any schema change bumps；must map to spec |
| `sr:extensionVersion` | `0.1` | SR vocabulary terms | additive term→minor；changed meaning/remove→major/new namespace plan |
| content fingerprint | `sr-book-document-text-v1` | edition digest algorithm | any byte/normalization input change→v2 |
| substrate equivalence | `sr-book-document-substrate-v1` | implementation-only anchor-bearing BookDocument equality | any projected field/framing change→v2 |
| chapter fingerprint | `sr-book-document-chapter-v1` | chapter digest algorithm | same rule |
| resource text | `sr-epub-resource-text-v1` | verified XHTML→logical quote/context stream | same rule |
| canonical JSON | `sr-canonical-json-v1` | semantic/package bytes | any encoding change→v2 |
| validation report JSON | `sr-annotation-validation-report-json-v1` | deterministic revision/failure report bytes | any field/order/encoding change→v2 |
| publication revision | `sr-annotation-publication-revision-v1` | immutable JSON/package/report deliverable-set digest | any frame/member change→v2 |
| generator version | reference implementation `0.1.0` | software build | normal release semver；不影响 semantic id |
| adapter version | `0.1.0` | current producer mapping | private input/mapping change bumps；不成为 schema dependency |

### 16.2 Compatibility policy

- v0.x reader必须验证 supported `specVersion` major、required core fields、fingerprint algorithm和 `sr:kind` invariants。
- 未知 unprefixed field拒绝；已声明 context的未知 prefixed optional field保留或忽略并 warning。Reader不得因未知 optional extension改变 core interpretation。
- `additionalProperties`策略：core objects拒绝未知 unprefixed；允许 syntactically valid CURIE pattern，但 semantic validator要求 prefix已在 fixed top context声明、限制深度/size，并禁止重定义 core prefixes。
- Minor release只能增加 optional field/enum capability且旧文档仍 valid。新增 required field、改变 ID input、改变 highlight/note body规则、改变 target语义都必须新 major。
- Migration是显式 `v0 -> v1` tool：读旧 schema、输出新 artifact、保留旧 file、不原地改 bytes，并生成 migration report。不能让 generic validator“顺手修复”。
- current historical reaction rows的升级不属于 Pack schema migration；它是 producer-private offline migration，normal adapter仍strict。

### 16.3 Working Draft updates

EPUB Annotations Working Draft 发布新 dated version时：

1. 不自动更新 `sr:profile`；现有 v0继续 pin 2026-05-21。
2. 建 standards delta report：AnnotationSet/selector/context/packaging/media/security变化。
3. 若仅解释性且不改变 Pack，patch doc即可；若改变 wire/packaging/conformance claim，bump schema/spec并保留旧 validator。
4. 只有 W3C最终 Recommendation发布并完成 fixture/import验证后，才可改变 `conformance`措辞。

### 16.4 Reader Adapter stable dependency surface

Future Reader只应依赖：

- top-level `type/id/items`, profile/schema versions；
- publication file/content identity；
- one track/creator；
- annotation `id`, `sr:kind`, motivation/body；
- target source href、TextQuoteSelector、ParagraphCharSelector、chapter fingerprint；
- CFI仅作为 optional acceleration。

Reader不得依赖 generator version、provenance、item order、validation report、Second Reader runtime paths或 compatibility taxonomy。

## 17. Repository Landing Plan

### 17.1 New contract files

| File | Purpose / owned contract | Dependencies | Coverage |
|---|---|---|---|
| `contract/annotation-pack/v0/README.md` | 对外入口、scope、normative invariants、version/process；不重复字段表 | schema/context/standards | link/version lint |
| `contract/annotation-pack/v0/schema/annotation-pack.schema.json` | **canonical wire schema authority** | JSON Schema 2020-12 | positive/negative contract tests |
| `contract/annotation-pack/v0/schema/publication-pointer.schema.json` | local `current.json` auxiliary schema；不定义 Pack wire | publication revision algorithm | pointer/path/digest/optional-package tests |
| `contract/annotation-pack/v0/schema/validation-report.schema.json` | local machine report auxiliary schema；不定义 Pack wire | validation error catalog/canonicalization | status/conditional/determinism tests |
| `contract/annotation-pack/v0/context/second-reader-annotation-context.jsonld` | `sr:` term/type mapping | confirmed namespace | offline context hash/test |
| `contract/annotation-pack/v0/standards.md` | pinned W3C URLs、aligned/not-conformant说明、known WD gaps | official dated specs | URL/pin snapshot review |
| `contract/annotation-pack/v0/CHANGELOG.md` | protocol/schema change log | version policy | version check |
| `contract/annotation-pack/v0/examples/highlight.annotation.json` | minimal item example | schema `$defs/Annotation` | item validation |
| `contract/annotation-pack/v0/examples/note.annotation.json` | minimal item example | same | item validation |
| `contract/annotation-pack/v0/examples/minimal-pack.json` | full two-item example | canonical schema/context | schema + semantic validation |

### 17.2 New Python implementation files

| File | Purpose / owned contract | Allowed dependencies | Coverage |
|---|---|---|---|
| `src/annotation_pack/__init__.py` | stable public Python API/version | generic modules only | import smoke |
| `src/annotation_pack/drafts.py` | producer-neutral input/result dataclasses | stdlib | type/construction tests |
| `src/annotation_pack/_generated_models.py` | generated wire bindings；不可手改 | Pydantic | drift/round-trip |
| `src/annotation_pack/resources/annotation-pack.schema.json` | byte-identical runtime schema | canonical root schema | SHA drift check |
| `src/annotation_pack/resources/publication-pointer.schema.json` | byte-identical auxiliary pointer schema | canonical root auxiliary schema | SHA drift check |
| `src/annotation_pack/resources/validation-report.schema.json` | byte-identical auxiliary report schema | canonical root auxiliary schema | SHA drift check |
| `src/annotation_pack/schema.py` | offline schema/context loader | `importlib.resources`, `jsonschema` | no-network/invalid schema |
| `src/annotation_pack/identity.py` | EPUB/OPF validation、fingerprints、PublicationIdentityBuilder | ebooklib/stdlib/reading_core neutral parse | file/content/chapter goldens |
| `src/annotation_pack/ids.py` | immutable UUID namespaces/canonical name functions | stdlib | fixed vectors/property tests |
| `src/annotation_pack/anchors.py` | strict BookDocument resolver、AnchorBuilder、context/optional CFI interface | reading_core TypedDict only | exact/cross段/failure tests |
| `src/annotation_pack/builder.py` | generic highlight/note/pack construction | drafts/generated/ids/anchors | mapping/invariants |
| `src/annotation_pack/validation.py` | schema + semantic/privacy validation/report | schema/ids | error catalog tests |
| `src/annotation_pack/serialization.py` | `sr-canonical-json-v1` + semantic digest | stdlib | canonical byte vectors |
| `src/annotation_pack/packaging.py` | safe reproducible detached ZIP | stdlib zipfile | package/security tests |
| `src/annotation_pack/exporter.py` | snapshot/idempotency、immutable revision + atomic pointer orchestration | generic modules + runtime neutral paths | artifact/integration/crash-window tests |
| `src/annotation_pack/producers/__init__.py` | producer plugin boundary | drafts only | import boundary test |
| `src/annotation_pack/producers/second_reader.py` | current reaction ledger→draft adapter | `attentional_v2.storage`/JSON shape、BookDocument | real-shaped adapter tests |

若 exact EPUB→BookDocument reparse仍只有 private `_build_book_document()`，Slice 2 应提炼一个 neutral、no-write public helper（优先 `src/reading_core/epub_document.py`）并在 `iterator_reader/parse.py` 复用它，配 equivalence test。不得复制两套 whitespace/paragraph/CFI parser，也不得改变 normal parse output。

### 17.3 New scripts/tests/fixtures

| File | Purpose | Coverage / note |
|---|---|---|
| `scripts/generate_annotation_pack_bindings.py` | schema→bindings/runtime copy，`--check` | generation drift |
| `scripts/export_annotation_pack.py` | explicit exporter CLI | CLI exit/status/idempotency |
| `scripts/validate_annotation_pack.py` | JSON/package validator | good/bad package |
| `scripts/inspect_annotation_pack.py` | safe summary，不显示private/全文 | independent inspect test |
| `tests/annotation_pack/test_contract.py` | schema/context/examples/generated drift | contract |
| `tests/annotation_pack/test_identity.py` | file/content/chapter/work IDs | fixed vectors |
| `tests/annotation_pack/test_anchors.py` | quote/span/context/CFI | unit/property |
| `tests/annotation_pack/test_builder.py` | highlight/note/creator/IDs | unit |
| `tests/annotation_pack/test_validation.py` | every error/private leak/extension | unit |
| `tests/annotation_pack/test_serialization.py` | canonical bytes/digests | golden |
| `tests/annotation_pack/test_packaging.py` | ZIP/reproducibility/security | artifact |
| `tests/annotation_pack/test_second_reader_adapter.py` | current vs compatibility/historical rows | producer contract |
| `tests/annotation_pack/test_exporter.py` | full public output/atomic/idempotent/partial | integration |
| `tests/annotation_pack/fixtures/tiny-reader/README.md` | original/CC0 provenance/license/generation | privacy gate |
| `tests/annotation_pack/fixtures/tiny-reader/source.epub` | deterministic valid micro EPUB | one Highlight + one Note |
| `tests/annotation_pack/fixtures/tiny-reader/build_fixture.py` | reproducibly rebuild binary | byte SHA fixture |
| `tests/annotation_pack/fixtures/tiny-reader/producer/` | minimal current-shaped BookDocument/reaction ledger/run state | no private book text |
| `tests/annotation_pack/fixtures/tiny-reader/golden/` | expected JSON/package/report digests | full golden |

另建 fragment-TOC negative fixture或test factory，暴露 current duplicate-resource风险；不把它混入 happy-path golden。

### 17.4 Modified files and governance timing

| Existing file | Planned change | When / why |
|---|---|---|
| `reading-companion-backend/pyproject.toml` | direct `jsonschema[format-nongpl]>=4.23,<5` runtime + dev-only `datamodel-code-generator==0.74.0` / `ruff==0.15.5` deterministic generation toolchain；Slice 3若stdlib不足则显式pin经过测试的 Unicode grapheme segmenter | Slice 1/3 |
| `reading-companion-backend/src/reading_runtime/artifacts.py` | neutral `annotation_packs_dir`, track dir/file helpers | Slice 6；public artifact ownership |
| `reading-companion-backend/src/iterator_reader/parse.py` / new reading_core helper | only if needed，提炼 no-write canonical rebuild path | Slice 2；must preserve parse behavior |
| `Makefile`, `scripts/contract-check.sh` | `annotation-pack-contract-check` | Slice 1/8 |
| `README.md` | explicit export/validate/inspect commands | Slice 6/8 when runnable |
| `docs/source-of-truth-map.md` | 将 root contract登记为 canonical + check | Slice 1 when schema exists |
| `docs/workspace-overview.md` | annotation contract/backend module/public artifact ownership | Slice 1/7 when real |
| `docs/backend-state-aggregation.md` | new public artifact source/normalization boundary | Slice 6/7 when emitted |
| `docs/current-state.md` | only when implementation becomes active/blocked/done | first authorized implementation slice；本设计不伪造 active work |
| `docs/tasks/registry.md/.json` | active Epic；每 slice更新 status/evidence | first authorized implementation slice + future slices |
| `docs/history/decision-log.md` | `DEC-155` stable seam decision | 本设计 |
| `.gitignore` | only if implementation creates new generated scratch under tracked territory | same slice；normal output已ignored |

本 Epic 不修改 `docs/api-contract.md` / `docs/api-integration.md`，因为没有新 public HTTP route；未来 Library/Reader API另立任务。也不修改 mechanism doc、Digest contract或 prompt，因为 adapter只读现有 settled truth。若实现过程中发现必须改变 native mechanism，停止并重新拆决策，不能把改动藏进 Pack slice。

### 17.5 Resolved confirmations before Slice 1

owner 已于 `2026-08-23` 确认正式采用并通过 GitHub Pages托管：

```text
https://captain4whale.github.io/second-reader/ns/annotation-pack#
https://captain4whale.github.io/second-reader/schema/annotation-pack/v0/annotation-pack.schema.json
```

Slice 1建立 GitHub Actions Pages发布约定和本地 byte-identical staging check；feature branch只证明构建映射，正式托管仍以进入 `main`后的成功部署和HTTP复验为准。不得使用 GitHub blob/raw易漂移 URL替代长期 namespace。其余 v0 产品/架构决策已固定，不需要重新讨论。

## 18. Implementation Slices

每个 slice 独立 review、运行 focused + governance checks、更新 `TASK-ANNOTATION-PACK-V0-IMPLEMENTATION` evidence，并按 workspace rule单独 commit。owner 已明确授权本 Epic 每个 Slice验收后 push `codex/annotation-pack-v0`；下一 Slice只能建立在前一 Slice acceptance通过且已 commit/push的提交上。

### Slice 1 — Contract skeleton + canonical schema authority

**Objective**：建立独立 root contract、固定 namespace/版本/pinned standards、提交 canonical JSON Schema/examples，并让 generated binding drift可检查。

**Files changed**：

- 新建 `contract/annotation-pack/v0/{README.md,standards.md,CHANGELOG.md}`；
- 新建 `schema/{annotation-pack.schema.json,publication-pointer.schema.json,validation-report.schema.json}`, `context/*.jsonld`, `examples/*.json`；
- 新建 `src/annotation_pack/{__init__.py,_generated_models.py,schema.py,resources/...}`；
- 新建 `scripts/generate_annotation_pack_bindings.py`, `tests/annotation_pack/test_contract.py`；
- 修改 `pyproject.toml`, `Makefile`, `scripts/contract-check.sh`, `docs/source-of-truth-map.md`, `docs/workspace-overview.md`, current-state/registry evidence。

**Dependencies**：本设计；namespace/schema hosting URL确认；现有 Pydantic 2/pytest。无 Slice 2+ code依赖。

**Implementation steps**：

1. owner确认 namespace/schema IRI；固定 protected `sr` prefix binding。Wire已使用完整 `sr:*` compact IRI key，因此 committed context不创建会重定义 WA/DC bare terms的别名，也不联网扩展。
2. 将第 4–6 节转成 canonical Pack JSON Schema 2020-12 `$defs`；另建不参与 wire/codegen 的 publication-pointer与validation-report auxiliary schemas；core unprefixed fields strict，declared extensions受控。
3. 写 three examples与最小 negative fixtures；验证 UUID/URL/date/conditional highlight/note规则能被 schema表达的部分。
4. 按第 13 节固定 `jsonschema`范围、`datamodel-code-generator==0.74.0`和CLI参数；实现 deterministic generate/`--check`，用extension probe验证aliases/extra不会丢失。
5. generated model alias round-trip回到原 JSON keys；runtime schema copy byte-identical。
6. 接入 root `contract-check`，更新 source-of-truth routing。

**Tests/checks**：`generate... --check`、examples schema pass、删 required field/错 kind/Highlight body等 negative pass、publication pointer path/digest/optional-package条件、validation report status/conditional/canonical sort、generated alias round-trip、`make contract-check`, `make agent-check`。

**Acceptance criteria**：一个且只有一个 Pack wire schema authority，pointer/report auxiliary schemas不重定义 Pack；examples valid；生成物无 drift；offline/no-network check可在 clean clone运行；contract不 import backend producer。

**Must not do**：不实现 exporter/fingerprint/adapter；不把 README字段表当第二 authority；不声称 W3C official schema或WD Recommendation；不使用 placeholder namespace发布。

**Rollback/failure notes**：如果固定 codegen不能稳定保留 JSON-LD aliases/declared extensions，Slice 1不得部分落地或换 floating tool；保留设计/JSON Schema authority，回滚未发布生成物并提交一份generator替代决策再重做 Slice。不得反转 authority到临时 Python model。

### Slice 2 — Publication identity and fingerprinting

**Objective**：实现 verified source EPUB、Work/Edition/File identities、content/chapter fingerprints与固定 UUID vectors；解决 source asset↔BookDocument coherence gate。

**Files changed**：

- 新建 `src/annotation_pack/{identity.py,ids.py,epub_source.py}` 或等价 neutral modules；
- 必要时新建 `src/reading_core/epub_document.py` 并最小重构 `iterator_reader/parse.py`复用；
- 新建 `tests/annotation_pack/test_identity.py` 与 tiny EPUB factory seed；
- 若新增依赖，修改 `pyproject.toml`；更新 task evidence/current-state。

**Dependencies**：Slice 1 schema/versions；current ebooklib/parser；可用真实微型 EPUB test factory。

**Implementation steps**：

1. 实现 safe path/regular file/ZIP/mimetype/container/OPF manifest validation。
2. 实现 streaming file SHA-256/length和 pre/post snapshot guard。
3. 实现 exact `N/FRAME` content/chapter algorithms与固定 digest vectors。
4. 从 exact EPUB无写入重建 BookDocument；比较 persisted `sr-book-document-substrate-v1` projection并计算独立 content digest；确保 normal parse结果完全不变。
5. 实现 OPF identifier/title/creator/language normalization及 provisional work fallback。
6. 提交 immutable namespace UUID constants与所有 publication/creator/generator ID functions。

**Tests/checks**：same bytes、repack same text、text/structure change、metadata-only change、missing/corrupt/path traversal EPUB、stale BookDocument、ISBN valid/invalid、Unicode/whitespace vectors、chapter order、spine-0/fragment regression observation、parser equivalence。

**Acceptance criteria**：identity仅由已定义输入决定；raw file与normalized edition区分正确；source/document mismatch fatal；无 absolute path进入 result；同 vectors跨重复运行一致。

**Must not do**：不做跨译本/work fuzzy matching；不把 slug/title-author当 authority；不改变 normal parse/reading behavior；不把 source EPUB复制到 Pack。

**Rollback/failure notes**：如果 neutral reparse提炼会改变 parser输出，先只暴露现有 deterministic builder的 no-write wrapper并记录 tech debt；任何 digest不一致都 fail closed，不能增加 `--trust` 默认绕过。

### Slice 3 — Anchor model and serialization primitives

**Objective**：实现 strict paragraph-char→href/quote/context/chapter anchor、canonical JSON bytes与 semantic digest；CFI保持verified optional接口。

**Files changed**：

- 新建 `src/annotation_pack/{drafts.py,anchors.py,serialization.py}`；
- 新建 `tests/annotation_pack/{test_anchors.py,test_serialization.py}`；
- 增加 anchor/resource text fixed vectors与negative fixtures。

**Dependencies**：Slice 2 `PublicationIdentityResult`, verified EPUB index, UUID IDs；BookDocument types；实现时选择并pin可按 Unicode extended grapheme cluster工作的轻量 helper，不能手写只覆盖 combining mark 的伪完整算法。

**Implementation steps**：

1. 实现 `{chapter.id}`, `{paragraph_index}` maps和end-exclusive range validator。
2. 支持单段/跨段、`\n\n` reconstruction、三方 quote equality、same href/OPF membership。
3. 实现 resource text mapping、bounded prefix/suffix、quote uniqueness warning、chapter context。
4. 实现 `AnchorBuilder`与anchor id；定义 `CfiResolver` protocol，current default resolver只在真正 round-trip时返回selector，否则None/warning。
5. 实现 `sr-canonical-json-v1`、semantic projection/digest fixed vectors。

**Tests/checks**：exact单段/跨段、1-based paragraph、char boundaries、Unicode NFC/combining boundary cases、wrong chapter/ref、fallback/ambiguous/cross-href、empty/long quote、CFI absent/present/mismatch、key order/UTF-8/repeat bytes。

**Acceptance criteria**：每个成功 anchor可从 BookDocument完全重建 exact；current unverified CFI从输出省略；serialization fixed vectors稳定；module不 import attentional_v2。

**Must not do**：不实现 fuzzy re-anchor；不把 paragraph-local offset称 WA TextPosition；不以可解析 CFI覆盖 quote mismatch；不截断 exact。

**Rollback/failure notes**：若 current CFI没有可靠 resolver，整个 v0保持无 CFI并以 tests锁定；这是合法成功，不建立脆弱 parser。Anchor required parts失败必须 fail/skip，不降低语义。

### Slice 4 — Generic Pack Builder and validator

**Objective**：实现 producer-neutral `AnnotationPackBuilder`、Highlight/Note mapping、schema + semantic/privacy validator和 machine report。

**Files changed**：

- 新建 `src/annotation_pack/{builder.py,validation.py}`；
- 新建 `tests/annotation_pack/{test_builder.py,test_validation.py}`；
- 若发现 schema表达缺口，以规范 version流程同步修改 root schema/generated binding/examples。

**Dependencies**：Slices 1–3；不依赖 current producer artifacts。

**Implementation steps**：

1. build publication/track/generator/provenance envelope；按 ID排序 items。
2. 映射 Highlight无 body/`highlighting`，Note单一 plain TextualBody/`commenting`。
3. 重算并校验 pack/track/anchor/annotation IDs与 semantic digest。
4. 实现 cross-field invariants、creator一致性、duplicate/empty规则。
5. 实现 private leak scanner、unknown extension policy、完整 error catalog、pre-publication `ValidationResult`与 artifact-digest-aware `finalize_validation_report()`。
6. 让 serializer只接受 validator成功的 document。

**Tests/checks**：所有 mapping、creator三类型、invalid motivation/body/kind、duplicate IDs、invalid times、missing identity、schema mismatch、unknown prefix、private keys/paths、large strings/depth、strict vs degraded/empty policy。

**Acceptance criteria**：不接触任何 producer也能从 drafts构建/验证完整 example；每个设计 error code有测试；degraded output本身仍 fully valid；report无 quote/path/private ID。

**Must not do**：不加 producer-specific if/field；不做 auto-repair；不引入 database/RDF/remote JSON-LD；不把 report塞进 Pack。

**Rollback/failure notes**：若 semantic validator与schema责任重叠，schema保留结构 authority，semantic code只保留跨字段/外部 bytes invariants；禁止在 README复制规则作为补丁。

### Slice 5 — `SecondReaderProducerAdapter`

**Objective**：只把 current native settled `reaction_records.json`转换成中性 drafts，显式隔离 compatibility/historical/private data。

**Files changed**：

- 新建 `src/annotation_pack/producers/{__init__.py,second_reader.py}`；
- 新建 `tests/annotation_pack/test_second_reader_adapter.py` 与 current-shaped sanitized fixtures；
- 不修改 `attentional_v2` prompt/schema/runner/settlement。

**Dependencies**：Slices 2–4；current reaction ledger/storage path；existing SourceRef/settlement tests作为事实依据。

**Implementation steps**：

1. snapshot/load supported ledger envelope；拒绝 audit/chapter compatibility作为输入。
2. gate `record_source=read_surface`, explicit `marginalia_kind`, timestamp，Highlight/Note body invariants。
3. strict gate unique `matched/exact_text` primary source ref；把 private source span复制进 `SourceRange` value，不透传类型。
4. drop compat/search/lineage/selection/memory fields；source record仅生成 local index+hash。
5. 返回 exact ledger SHA、真实 `input_count`与adapter成功 rows的ordered digests；不在 adapter读取 BookDocument、解析anchor、应用export policy或调用builder。
6. 将 historical/mixed ledger分类为可预测 row error codes；ledger unavailable/invalid/schema/limit/mutation一律 pack-level fail closed，不 heuristic migrate。

防御上限固定为：`MAX_REACTION_LEDGER_BYTES=16 MiB`、`MAX_REACTION_RECORDS=2000`、`MAX_REACTION_LEDGER_JSON_DEPTH=64`、`MAX_REACTION_LEDGER_JSON_NODES=100000`、single/total string code points=`65536/16777216`、`MAX_REACTION_RECORD_CANONICAL_BYTES=128 KiB`、hash chunk=`1 MiB`。读取必须逐路径组件 `O_NOFOLLOW`、只接 regular UTF-8无 BOM file，拒绝 duplicate keys和non-finite numbers，并在read前后以及全路径重开时核对fd/path identity；任何 limit或snapshot mutation都不能降级为row skip。

**Tests/checks**：current highlight/note、Note compat=`association`仍映射note、legacy缺kind、non-string discriminator、`primary_anchor` old shape、fallback/ambiguous、wrong quote、mixed rows、timestamp floor、NFC-before-limit、strict JSON/limits、leaf/parent symlink、pathname/in-place mutation、forged error privacy、no private leakage、跨段 source ref、adapter import boundary、multiple hash seeds。

**Acceptance criteria**：一个真实 current-shaped ledger至少导出一 Highlight/一 Note；compat fields改变不影响 canonical item；old rows不会伪装成current；generic builder无 attentional import。

**Must not do**：不读 read/settlement audit、Digest result或chapter compatibility；不改 Agent；不从 `type/compat_family`猜 kind；不输出 reaction id。

**Rollback/failure notes**：若 current ledger版本无法可靠区分 native/historical，支持范围缩窄并fail closed；另开 migration任务，不污染 normal adapter。

### Slice 6 — CLI export / inspect / validate tools

**Objective**：提供 callable orchestration与显式 JSON exporter/validator/inspector，落 public path并实现 snapshot/idempotency/atomicity；此 slice只承诺 `annotations.json`。

**Files changed**：

- 新建 `src/annotation_pack/exporter.py`；
- 新建 `scripts/{export_annotation_pack.py,validate_annotation_pack.py,inspect_annotation_pack.py}`；
- 修改 `reading_runtime/artifacts.py`, `README.md`, `docs/backend-state-aggregation.md`；
- 新建 `tests/annotation_pack/test_exporter.py` 与 CLI tests。

**Dependencies**：Slices 1–5；existing output/run-state/artifact helpers。

**Implementation steps**：

1. safe book/output/track path resolution与 run-state policy。
2. input byte snapshot/recheck；调用 adapter/builder/validator/serializer。
3. existing semantic digest no-op；实现 temp/fsync→`sr-annotation-publication-revision-v1` immutable revision→schema-valid single-file atomic `current.json` pointer与failed report。
4. 实现 `deliverables=json|detached` 与 strict/allow-partial/allow-skips/allow-empty独立 flags和exit codes；Slice 6只接受显式 `json`，请求 `detached`稳定失败。
5. validator接受裸 JSON；inspector只显示safe metadata/count/digests/anchor capability，不打印全文。
6. docs给出可复制命令和“未完成正式 packaging”警告。

**Tests/checks**：`ready/parsing_structure/deep_reading/completed/paused/error/missing/unknown`、active lease、empty、degraded、input concurrent mutation、existing pack unchanged、path traversal、repeat no-op、JSON-only pointer、pointer digest/path mismatch、publish crash windows、public location、stdout/exit codes、no automatic runner dependency。

**Acceptance criteria**：独立 CLI以 `--deliverables json` 从 safe fixture生成 valid public `annotations.json`；重复命令幂等；失败保留上版；请求未实现的 detached不降级；normal reading tests无变化。

**Must not do**：不把 JSON改名伪称 `.annotations`；不添加 API/UI/catalog discovery；不在 Agent completion hook调用；不允许 arbitrary private input path normal mode。

**Rollback/failure notes**：不得尝试原子覆盖非空目录，也不得file-by-file覆盖current revision。若 pointer切换前失败，删除/保留未引用 temp供诊断并保持旧pointer；切换后失败只影响后续清理，current仍指完整immutable revision。未完全成功不能返回published。

### Slice 7 — Detached package generation

**Objective**：实现 pinned WD形态的 safe/reproducible `<track>.annotations`，并让 validator/inspector可独立处理 package。

**Files changed**：

- 新建 `src/annotation_pack/packaging.py`；
- 扩展 exporter/validate/inspect scripts；
- 新建 `tests/annotation_pack/test_packaging.py`；
- 更新 contract packaging说明、README/backend state aggregation。

**Dependencies**：Slice 6 canonical JSON bytes；stdlib ZIP；pinned WD 2026-05-21。

**Implementation steps**：

1. 只写 root `annotations.json`；固定 entry attrs/time/compression/order。
2. 写完后 reopen，执行 path/symlink/encryption/entry-count/size/ratio checks。
3. 对 entry JSON做 canonical/schema/semantic复验；计算 exact package digest。
4. exporter把 JSON/ZIP/report写成一个新的完整 immutable revision，再原子切换 pointer；同一 JSON从 Slice 6 JSON-only升级到 packaged deliverable时，publication revision digest必须变化，旧 JSON-only revision仍不修改。
5. inspector识别 `.json`/`.annotations`，默认不extract到disk。

**Tests/checks**：byte reproducibility、exact one entry、wrong root、extra EPUB/asset、zip slip、symlink、bomb-like sizes、encrypted/corrupt ZIP、entry noncanonical、independent open/inspect、MIME string constant。

**Acceptance criteria**：同 JSON生成 byte-identical package；普通 ZIP tool可打开；独立 validator成功；包中无 EPUB/private/report；正式 artifact命名/media/docs准确。

**Must not do**：不加入 `mimetype`、custom manifest或optional assets；不把WD未规定的reproducibility说成W3C要求；不自动上传/分发。

**Rollback/failure notes**：若 package validation失败，保留 Slice 6 valid JSON但不发布/宣称 detached artifact；修复 package层，不改 canonical data model迁就 ZIP bug。

### Slice 8 — Golden fixtures, full tests, docs and contract checks

**Objective**：用可公开真 EPUB + current-shaped Marginalia完成 end-to-end proof，补齐 contract/governance docs/checks并关闭 Epic。

**Files changed**：

- 完成 `tests/annotation_pack/fixtures/tiny-reader/{README.md,source.epub,build_fixture.py,producer/,golden/}`；
- 完善所有 `tests/annotation_pack/*`、root/backend docs、Makefile/check scripts；
- 更新 source-of-truth/current-state/task registry/decision evidence；必要时 `.gitignore`。

**Dependencies**：Slices 1–7全部通过；无 network/provider/LLM/Readest/Library依赖。

**Implementation steps**：

1. 写原创短文、固定 OPF identifier/title/creator/language与两个 XHTML resources；附版权/provenance声明。
2. 固定 ZIP entry order/time/mode/compression；generator重建后 SHA一致。
3. 从真实 EPUB parse生成/核对 BookDocument，再用 current-shaped ledger导出一 Highlight/一 Note。
4. golden校验 href/span/quote在 exact EPUB重建；覆盖 CFI absent而成功。
5. 加 fragment-TOC/sparse-CFI negative/regression probe。
6. 运行 focused/full checks，文档列明 capability/limits；将 waiting/active task转 done，记录 commit/evidence。

**Tests/checks**：第 19 节全部；至少 `make annotation-pack-contract-check`, backend annotation tests, relevant parser/runtime tests, `make contract-check`, `make agent-check`，风险允许时完整 backend suite。

**Acceptance criteria**：DoD全部机器可验证；fresh clone离线生成/validate/inspect package；golden含一 Highlight/一 Note且anchors resolve；no private text/path/state；文档与代码/schema无 drift。

**Must not do**：不以 ignored/public-domain local大书替代tracked micro fixture；不跑/依赖LLM eval；不顺便修 Readest/Library/Agent；不把 focused success表述成外部 Reader interoperability proof。

**Rollback/failure notes**：fixture provenance/byte reproducibility/anchor任一不稳定即不关闭 Epic；回滚 golden而不是更新 expected digest掩盖未解释变化。对 parser gap做明确 negative test/后续任务，不在本 slice大范围重构。

## 19. Test Plan

### 19.1 Unit tests

| Area | Required cases | Pass evidence |
|---|---|---|
| Highlight mapping | explicit kind、empty thought、highlighting、no body | exact canonical item |
| Note mapping | explicit kind、non-empty content、commenting、one text/plain body/language optional | exact canonical item |
| Deterministic IDs | fixed UUID vectors、same input repeat、body/quote/edition/track change | expected same/different IDs |
| Content normalization | NFC、CRLF、Unicode whitespace、empty paragraph、chapter boundary、order | fixed SHA-256 vectors |
| File fingerprint | streaming bytes/length、one-byte change | exact hashes |
| Work identity | valid ISBN, invalid check digit, OPF URI, missing id provisional | strength/id rules |
| SourceRef mapping | current exact、single/cross paragraph、1-based map、end-exclusive | reconstructed exact equality |
| Quote/context | resource stream、prefix/suffix at boundaries、duplicate quote、max lengths | selectors/warnings/errors |
| CFI optionality | missing/lightweight/failed round-trip omitted；verified exact included | output remains valid without CFI |
| Invalid input | missing chapter/paragraph、bad offsets、fallback/ambiguous、cross href、bad time/kind | stable error codes |
| Private exclusion | every forbidden field/path plus benign text false positives | fatal/no leak |
| Repeat determinism | canonical JSON bytes、semantic digest、ZIP bytes with fixed generated time | byte equality |
| Publication revision | JSON-only/full-package frame vectors、report digest、same deliverables、package added | expected revision IDs / immutability |
| Report finalization | ValidationResult has no artifact claims；JSON/package digests injected once after validation | no mutable/half-valid report |
| Export policy | strict/skips/partial/empty/active/mutation/idempotent | expected outcome/report/exit |

现有 regression事实测试必须继续跑：`test_attentional_v2_source_spans.py`、Marginalia settlement/scaffold/slow-cycle tests、relevant iterator parse/public artifact tests。Pack tests不替代它们。

### 19.2 Contract tests

- root schema本身通过 Draft 2020-12 meta-schema check；`$id`/directory/version一致。
- highlight item、note item、minimal Pack examples保持 valid。
- 每个 required field删除都会被拒；unknown unprefixed field拒绝。
- conditional body/motivation/kind、one creator/target/motivation、relative source href、limits/enums被锁定。
- declared non-`sr` optional extension在 compatible mode preserve/warn；undeclared prefix拒绝；extension不得覆盖 core/context。
- generated models/runtime schema与canonical schema byte/source digest不漂移。
- Python generated alias round-trip后仍过 canonical schema；Python model不反向生成新authority。
- `publication-pointer.schema.json` 锁定 safe relative paths、64-hex digests、package path/digest成对出现；`validation-report.schema.json` 锁定 status/conditional/counts/findings，并证明 pre-artifact `ValidationResult`不能被误落盘；二者不得重定义或内嵌 Pack wire fields。
- pinned standards date/status/URLs有简单 constant snapshot，避免误改成 latest/Recommendation。

### 19.3 Artifact and security tests

- output只落 `public/annotation-packs/<track_slug>/`，不落 `_mechanisms`。
- JSON/package/report先组成 immutable revision并fsync，最后只原子替换 `current.json`；任一 crash point都保留一个完整 current revision，failed export不改pointer。
- pointer及三个 artifact digests可现场重算；JSON-only→packaged upgrade生成新 revision，旧 revision目录逐 byte不变。
- `.annotations` exact one root JSON；不含 EPUB、report、source assets或extra files。
- JSON/ZIP无 absolute/local path、mechanism/private state、job status、reaction/compat fields。
- package可由 stdlib ZIP独立打开，可由 validator/inspector在没有 producer artifacts时理解。
- corrupted ZIP、zip-slip、absolute/Windows path、symlink、encrypted entry、oversize、high ratio、duplicate root、duplicate JSON keys均拒绝。
- semantic/package/input digests都可独立重算。
- inspector不会打印完整 source quotes/note bodies，除非未来另有显式安全 flag（v0不需要）。

### 19.4 Golden / real-data test

Tracked `tiny-reader/source.epub` 必须：

- 是有效 EPUB 3 ZIP，不是 current 36-byte placeholder；
- 内容为项目原创或明确 CC0/public-domain短文，README记录作者、license、生成命令与 SHA-256；
- 至少两个 XHTML/多个 paragraphs，固定 href与OPF identifier；
- producer fixture使用 current `reaction_records` envelope/fields，至少一 unique exact Highlight、一 unique exact Note；
- 从真实 parse产生 BookDocument，不手写一个与 parser无关的“理想”substrate；
- exporter output的每个 href存在于 OPF；paragraph-char重建等于 TextQuote exact；Note body/Highlight no-body正确；
- CFI present/absent都覆盖，但 happy path成功不得依赖 CFI；
- repeated export semantic/bytes（injected time）与 committed golden一致；
- fixture/golden全文很短且无 private eval书籍内容。

另用 synthetic/negative builders测试 TOC fragment duplication、spine-0 CFI null、old sparse BookDocument；这些可以只在 temp生成，不提交受保护内容。

### 19.5 Suggested verification commands per completed Epic

```bash
make annotation-pack-contract-check
cd reading-companion-backend && .venv/bin/pytest tests/annotation_pack -q
cd reading-companion-backend && .venv/bin/pytest \
  tests/test_attentional_v2_source_spans.py \
  tests/test_attentional_v2_slow_cycle.py \
  tests/test_attentional_v2_scaffold.py \
  tests/test_iterator_parse.py \
  tests/test_iterator_frontend_artifacts.py -q
make contract-check
make agent-check
```

若 full backend suite因无关 baseline失败，必须将 focused pass与baseline failure分开报告；不能把未运行写成通过。

## 20. Definition Of Done

`DEC-156` 允许在尚未公开、尚无可能兼容承诺的情况下，直接替换 `contract/annotation-pack/v0/` 与原 schema IRI 对应的 v0。旧 wire 与 phase8 不保留 compatibility layer；本节是新的唯一 Epic 完成边界。

### 20.1 Canonical public wire

最终 `annotations.json` 必须是一个严格 `AnnotationSet`：

```text
AnnotationSet
├── @context = https://www.w3.org/ns/epub-anno.jsonld
├── id / type=AnnotationSet
├── generator
│   └── id / type=Software / name
├── generated
├── about
│   ├── dc:identifier = ["nih:sha-256;<64位小写hex>"]
│   ├── dc:format = application/epub+zip
│   ├── dc:title
│   └── dc:creator[]（源书有作者时）
└── items[]
    ├── id / type=Annotation / created / motivation
    ├── body（仅 Note）
    └── target
        ├── source = EPUB manifest 中的相对 XHTML href
        └── selector
            ├── TextQuoteSelector: exact + 可选 prefix/suffix
            └── TextPositionSelector: start/end
```

- [x] `@context` 必须是上述 W3C EPUB Annotations context 字符串；Pack 中零 `sr:*`，各层均使用严格属性白名单。
- [x] `generator` 使用固定的 Second Reader 软件身份，`generated` 为每个 Pack 必备时间。
- [x] `about.dc:identifier` 必须是恰好一项的数组，唯一值是 RFC 6920 `nih:sha-256;` 加 exact EPUB bytes 的 64 位小写十六进制 SHA-256；不接受分隔符、缩写或校验位。
- [x] `about` 必须有 `dc:format=application/epub+zip` 和非空 `dc:title`；源 EPUB 有作者时必须输出非空 `dc:creator[]`。
- [x] Highlight 必须为 `motivation=highlighting` 且禁止 `body`；Note 必须为 `motivation=commenting` 且只有一个 `type=TextualBody`、非空 `value` 的 body。
- [x] `target` 只有 `source` 与 `selector`；selector 恰好两项且顺序固定为 TextQuote 后 TextPosition。`TextQuoteSelector.exact` 必备，`prefix`/`suffix` 可省略。
- [x] TextPosition 使用 Unicode code point，`start` 包含、`end` 不包含，坐标针对当前 EPUB resource 的固定规范化文本流；规范化算法在 v0 README 中唯一定义，不逐条重复。
- [x] `items` 按 Annotation `id` 确定性排序；Pack ID 是 exact EPUB hash 与固定 generator identity 的 UUIDv5，Annotation ID 是 EPUB hash、href、start/end、motivation 及 Note body 的 UUIDv5；语义重复项拒绝。
- [x] 不输出逐条 creator、`sr:kind`、target type、body format、Work/Edition/File、Track、chapter context/fingerprint、anchor ID、CFI、provenance 或 public digest。

### 20.2 Standards and producer boundary

- [x] 文档仅宣称与 W3C Web Annotation Data Model Recommendation 及 `2026-05-21` EPUB Annotations 1.0 Working Draft aligned；不宣称 EPUB Working Draft conformant。
- [x] Set/Annotation 基础身份字段来自 W3C/EPUB WD；`generator/generated`、书籍必备元数据、motivation、双 selector、exact-file hash、顺序与严格白名单是 Second Reader v0 profile 约束，但公开 wire 仍只使用标准词汇。
- [x] 默认 `ReadingProductProducerAdapter` 只读取 complete Reading Product v1 的公开 pointer、不可变 revision 与 validation report，并把已提交 Unit 中的 native Highlight/Note、exact range/quote 和 settlement time 展平为 producer-neutral drafts；默认路径不读取 run state、reaction ledger、audit、Memory 或机制版本。
- [x] `attentional-v2-phase9-legacy` 只保留为显式选择的旧输入 adapter，无自动 fallback；phase8 继续直接拒绝。无旧 wire migration/compatibility path，无 phase8 自动升级，无从 compatibility taxonomy 反推 Highlight/Note。

### 20.3 Internal correctness and publication invariants

- [x] exact verified source handle/no-follow、EPUB/BookDocument coherence、quote round-trip、privacy scan、canonical JSON bytes、ZIP hostile-case rejection、immutable revisions、atomic `current.json`、idempotent unchanged、input mutation detection、crash recovery与 concurrency protection 全部保留。
- [x] snapshot/content digest、adapter identity/details 与 findings 仅可存在 sanitized validation report/current pointer，不得进入 `annotations.json` 或 `.annotations`。
- [x] `.annotations` 是单根 `annotations.json` ZIP；可在无 EPUB、BookDocument 或 producer ledger 时独立 validate/inspect。
- [x] public Pack/package 不含 local path、private Agent/book/job/id、compat taxonomy、prompt/reasoning、Memory、trace/audit、provenance 或其他 producer-private 内容。

### 20.4 Implementation slices and acceptance

**Slice 1 — Authority reset**

- [x] 新决策明确 v0 未公开，允许原路径直接替换，并部分 supersede `DEC-155` 的重型身份与锚点公开设计。
- [x] 本节、current state 与 task registry 指向新完成边界；登记 Annotation Hub consumer 后续迁移任务，但不修改 Hub 工作树。
- [x] 轻量文档/注册表校验通过；Slice 1 已由 `012788d` 独立 commit 并 push 到 `origin/codex/annotation-pack-v0`。

**Slice 2 — Atomic wire cutover**

- [x] 同一 Slice 同步替换 canonical schema、examples、标准说明、generated bindings/runtime copies 和 Pages projection；删除自定义 JSON-LD context/namespace 发布面，保留原 schema IRI。
- [x] 同步重构 identity、IDs、anchor、builder、validator、exporter、inspector 和 adapter；ParagraphChar 被 TextPosition 完全替代，phase8 失败。
- [x] 重建 Tiny Reader `annotations.json`、package、report、pointer 和 digest golden；每个 target 均满足 `resource_text[start:end] == exact`。
- [x] focused Annotation Pack checks、影响的 Agent/source regressions 与必要的 contract checks 完成；Slice 2 已由 `b44ba7d` 独立 commit 并 push 到 `origin/codex/annotation-pack-v0`。两条相关回归失败是可在 replacement 前基线复现的 `slow_cycle` 测试/接口漂移，单列于 baseline observations，不计为 Annotation Pack 回归。

**Slice 3 — Acceptance and close-out**

- [x] 同步 README、source-of-truth、state aggregation、current-state、task registry、baseline observations 与本节的最终验收证据。
- [x] 最终命令组完成：`annotation-pack-contract-check: 55 passed`、完整 Annotation Pack suite `794 passed`、相关 Agent/source regressions `134 passed, 2 failed`，完整 backend suite `1794 passed, 9 failed`，`make contract-check` 与 `make agent-check` 均 exit `0`。两条相关回归失败、完整 backend 的九条失败及治理命令的历史 warning 均按既有 baseline 单列，未冒充全绿。
- [x] Slice 3 由包含本验收记录的独立 closing commit 交付并 push 到 `origin/codex/annotation-pack-v0`；交付端在 push 后核对本地与远端 HEAD 一致，不 force-push。正文不写入无法自指的 closing commit hash，精确 hash 由最终交付记录报告。
- [x] 未运行真实整书 Agent，未新增 live-model、Library、HTTP API、frontend 或 Reader 集成。

### 20.5 Required negative and determinism evidence

- [x] 缺少任一 profile-required 字段、任意 `sr:*`、旧重型 v0 字段、phase8 ledger、Highlight+body 或 Note-body 缺失均失败。
- [x] EPUB 任意一 byte 改变都会改变 `nih` 标识与相关确定性 IDs。
- [x] 错 href、越界/空 TextPosition 或错 exact 失败；prefix/suffix 可合法省略。
- [x] 重复导出 unchanged，崩溃恢复、输入突变、并发和 hostile ZIP 用例继续通过。

### 20.6 Completion claim boundary

Epic 完成后只能声明：

> **当前默认阅读机制已经在代码层接入 Reading Product Output v1；使用真实 EPUB 和确定性模型替身，可以完成逐 Unit 提交、整书封版、兼容投影以及 Annotation Pack 的生成与独立验证。**

不得声明旧《悉达多》《纳瓦尔宝典》已转换，不得声明真实 LLM Agent 已完成整书阅读或真实整书 current Agent→Pack Gate 已验证。GitHub Pages schema IRI 目前仍为未上线；只有进入 `main`、启用/完成 Pages 部署并通过 served-byte 对比后，才能声明公开可用。原生 Unit API、frontend Understanding/Response 展示、Library、HTTP API 与 Reader 集成也不在本轮完成范围。

在 Slice 5 repo-local 收口时，只作出上述限定离线声明；当时真实 LLM 整书 Agent→Pack 尚未运行。后续 bounded live Gate 见第 20.9 节，它不改变这里的离线证据边界。旧《悉达多》《纳瓦尔宝典》仍未转换。Pages 只完成本地 projection/byte check，不是 live 部署或 served-byte 复验；原生 Unit API、frontend Understanding/Response、Library、HTTP API 与 Reader 集成均未实现、未测试、未声明。

### 20.7 Current minimal-reset acceptance evidence

- Authority reset 已由 `012788d` commit/push：写入 `DEC-156`、新 DoD 和 Annotation Hub consumer migration 后续任务，未修改 Hub 工作树。
- Atomic wire cutover 已由 `b44ba7d` commit/push：canonical contract、runtime、producer/export/package 链路和 Tiny Reader golden 已原子替换为极简 v0，无旧 wire 或 phase8 compatibility layer。
- Slice 3 验收证据：`make annotation-pack-contract-check` 为 `55 passed`；完整 `tests/annotation_pack` 为 `794 passed`；相关 Agent/source regression set 为 `134 passed, 2 failed`；`make contract-check` 与 `make agent-check` 均 exit `0`。
- 两条失败都位于 `tests/test_attentional_v2_slow_cycle.py`，仍是测试 monkeypatch 已移除的 `slow_cycle.invoke_structured_output_tool` module attribute；该漂移在 replacement 前基线已存在，Slice 1/2 均未修改 `slow_cycle.py` 或这两个测试。它们不是 Annotation Pack 回归，也没有被冒充为通过。
- 完整 backend suite 为 `1794 passed, 9 failed`。九条失败与既有 baseline 清单一致：`attentional_v2.bridge` 三条、`survey` 两条、`slow_cycle` 两条均为已移除 `invoke_structured_output_tool` attribute 的 monkeypatch/interface drift；另有 minimal-eval inventory active pointer 一条和 F4A 默认 target-count 一条。极简替换未触碰这些实现/测试，结果未冒充全绿。
- `make agent-check` 仍输出历史 task traceability、retired evidence path、active/done appendix drift、duplicate decision ID 与 LangChain deprecation warning；`make contract-check` 还输出 high-signal-doc decision reminder。前者均已在 baseline observations 中登记；后者不新增 decision-log entry，因为本 Slice 只同步 `DEC-156` 已决方向和 landed 能力，没有建立新方向。
- Slice 3 通过包含本记录的 closing commit/push 与交付端远端 HEAD 对齐完成；精确 closing commit hash 在最终交付记录中报告。

### 20.8 Reading Product v1 default-producer follow-through

`DEC-158` 在不改变极简 W3C/DC wire 的前提下，把默认生产者输入从机制私有 phase9 ledger 迁移到 mechanism-neutral Reading Product Output v1。Annotation Pack 的 schema、identity、anchor、canonical bytes 和 detached package 语义保持不变；phase9 只作为显式 legacy adapter 保留。

- [x] Slice 1（`d83707a`，已 push）建立 `contract/reading-product/v1`、共享 canonical JSON/BookDocument substrate/source-range 能力和严格 Product domain，且保持既有 Annotation Pack bytes 不变。
- [x] Slice 2（`7dcd160`，已 push）让默认 `attentional_v2` 在 accepted cursor 前原子提交 Product Unit；Understanding、Response、Highlight/Note 与 exact source anchors 成为产品事实，audit/Memory/reaction/selection reason 保持私有派生。
- [x] Slice 3（`e7adccc`，已 push）完成 Product Store 权威恢复、无重复模型调用的 committed-Unit replay、whole-book-only finalizer、source mutation/partial/chapter-only/audit-cap fail-closed 和不可变 publication。
- [x] Slice 4（`6239147`，已 push）把 Annotation Pack 默认 adapter 与章节兼容投影迁移到 complete Reading Product；删除私有 reaction/audit/memory 后仍可生成 Pack 和旧 UI 兼容投影，phase9 无自动 fallback。
- [x] Slice 5 repo-local implementation/acceptance 使用 tracked Tiny Reader 真实 EPUB 通过普通 parse、默认 Reading Runner、真实 Unit settlement/coordinates、Product Store、恢复、finalizer、compatibility projection 和默认 Pack exporter；只在模型调用边界注入确定性替身，没有执行 provider preflight 或真实 LLM 请求。最终隔离验收显式设置 `PYTHON_DOTENV_DISABLED=1` 与 `READING_OBSERVABILITY_OTLP_ENABLED=0`，因此该验收进程没有加载 backend `.env` 或尝试 OTLP export。
- [x] 离线全书用例覆盖空 Marginalia、Highlight、Note、坏锚点仅淘汰该条、Product-commit-ahead crash/resume 且不重复 Digest、source mutation 拒绝、重复 runner 和重复 Pack export `unchanged`；同样隔离条件下，专用 lifecycle 用例为 `1 passed`，包含 Reading Product、默认 runtime 与 Tiny Reader Pack consumer 的组合 focused set 为 `39 passed`。
- [x] 相关 Slice 证据还包括 Reading Product core `22 passed`、attentional runtime `101 passed`、Annotation Pack/consumer set `803 passed`、Tiny Reader `10` 个 deterministic files byte-exact，以及 `make annotation-pack-contract-check` 的 `55 passed`。
- [x] 最终串行 `make reading-product-contract-check`、`make annotation-pack-contract-check`、`make contract-check` 和 `make agent-check` 均 exit `0`；完整 backend suite 为 `1834 passed, 9 failed`，九项均属于已单列的 legacy monkeypatch、eval active-pointer 或隔离环境 target-count baseline 类别，没有 Reading Product/Annotation Pack 新失败。
- [x] Slice 5 以 `a81a935`（`test(reading-product): accept offline whole-book lifecycle`）完成 commit/push；push 后本地与 `origin/codex/annotation-pack-v0` 均解析为 `a81a9356988f7c711de5cac37eb7ae248e929134`。

上述 Slice 1–5 证据只支持第 20.6 节的 repo-local 离线声明；后续独立 live Gate 的证据见第 20.9 节。

### 20.9 Reading Product live-model follow-through

`TASK-READING-PRODUCT-OUTPUT-V1-LIVE-ACCEPTANCE` 已在 tracked Tiny Reader 短小真实 EPUB 上完成。普通 `parse_book` / `read_book` 入口通过 `cpa_codex_local` / `gpt-5.6-luna` 进行了真实模型调用，默认机制发布 `complete` Reading Product（`2` Units、`6` Marginalia），由 Product Unit 派生两份章节兼容投影，并由默认 adapter 生成 detached Annotation Pack。独立 validate/inspect 均通过：`6` items 全部导出，`0` skip、`0` warning、`0` error，包含 `4` Highlights 与 `2` Notes。

初始注册 job 在真实阅读与 Product 发布完成后，因验收 harness 的 compatibility helper 调用错误而以 `failed` 收尾；随后四次 retry 均未调用模型，只修正验收 harness，最终 `validation_retry4` 完成。因此 run ledger 同时保留初始失败 job 与最终通过 job，不把 wrapper 失败改写成全程一次通过。

新增证据只允许声明：**在 tracked Tiny Reader 短小真实 EPUB 上，当前默认机制已通过 CPA Luna 的真实 LLM 调用完成普通入口整书阅读，并生成 complete Reading Product、章节兼容投影和独立验证通过的 Annotation Pack。** 仍不得据此声明旧《悉达多》《纳瓦尔宝典》已转换、生产规模整书质量/性能已验证、Pages IRI 已公开上线，或原生 Unit API、frontend Understanding/Response、Library/API/Reader 集成已经完成。

### 20.10 Safe HTML5 DOCTYPE parser repair

The exact XHTML/HTML resource parser now accepts exactly one simple HTML5 `<!DOCTYPE html>` in the initial resource prolog after optional BOM/whitespace and an optional XML declaration. It continues to reject `ENTITY`, internal subsets, `SYSTEM`, `PUBLIC`, wrong doctype names, duplicate/misplaced declarations, malformed XML, oversized structures, and hostile ZIP inputs. Container and OPF XML remain DTD-free.

Focused source/resource tests pass `246` cases and the complete Annotation Pack suite passes `804` cases. The retained exact Xidaduo EPUB (`f239921773ac5abc86527fb78379cbd68cdf2cb901d253e085b2883180984a4f`) now produces `22` resource texts, all `590` paragraph ranges, and zero unverifiable hrefs through the committed production parser. This removes the parser false positive only; it does not migrate the historical phase9 eval artifact, invent a terminal state, persist its segment-coordinate bridge, resolve its one ambiguous quote, or publish a Pack from it. New Reading Product outputs already carry canonical coordinates and a true complete state.

## Appendix A. Superseded first-implementation Definition Of Done and closure record

以下内容是 `DEC-155` 重型 v0 在 `2026-08-24` 的本地/仓库验收记录，仅作实施历史；不再定义当前 v0 wire 或完成条件。

第一实现 Epic 只有在以下条件全部满足时才是 `done`：

- [x] `contract/annotation-pack/v0/` 中有一个 canonical spec入口、一个 canonical Pack wire JSON Schema、不重定义 wire 的 publication-pointer/validation-report auxiliary schemas、一个 committed SR context、pinned W3C standards说明；无三套手写事实。
- [x] Python reference implementation可从 producer-neutral inputs构建、验证、canonical serialize Pack；generated bindings/schema drift check通过。
- [x] `SecondReaderProducerAdapter` 只读 current native settled Marginalia，正确输出至少一 Highlight和一 Note；compatibility/historical rows不被误识别。
- [x] publication Work/Edition/File identity、raw file SHA-256、normalized content/chapter fingerprints和 deterministic IDs有 fixed vectors。
- [x] required href/quote/prefix/suffix/paragraph-char/chapter anchors可回查 exact fixture EPUB；current不可靠 CFI省略，verified CFI才可发出。
- [x] explicit exporter CLI支持 completed与显式 partial政策、strict/degraded/empty政策、snapshot/idempotent/atomic publish。
- [x] validator与safe inspector同时支持 `annotations.json` 和 `.annotations`，提供 stable machine-readable report/error codes。
- [x] 正式 `<track>.annotations` 是可独立打开/验证的 detached artifact，只含 root `annotations.json`，不含 EPUB。
- [x] 一个 public-safe、可重建、可确定 hash 的真 EPUB golden fixture被提交，含至少一 Highlight/一 Note且anchors resolve。
- [x] unit/contract/artifact/golden/security tests与相关 existing regressions通过；root `contract-check` / `agent-check`通过或清楚记录无关 baseline blocker。
- [x] public output位于 `output/<book_id>/public/annotation-packs/<track_slug>/`，不依赖 `_mechanisms/attentional_v2` 才能被独立理解。
- [x] public revisions immutable，`current.json` 单文件原子切换且所有 relative paths/digests可验证；JSON-only升级到 packaged revision不修改旧目录。
- [x] public Pack与report无 Agent Understanding、Memory、selection reason、prompt/reasoning、runtime trace/audit/job/progress/feedback/rating/download/rank、compat taxonomy、local path或private book content。
- [x] normal Agent mechanism、prompt、Digest、Memory、reading loop和completion success path没有变化；Pack export失败不影响阅读完成。
- [x] 没有 Readest、Library、Hypothesis、KOReader、Readwise、database、community或cross-edition fuzzy dependency。
- [x] README/source-of-truth/state aggregation/current-state/task registry/decision evidence按实际 landed能力最小同步；每个 Slice 都有 focused checks、独立 commit，并按 owner 授权 push 到 `codex/annotation-pack-v0`。

### Historical DEC-155 implementation checkpoint (superseded)

以下 Slices 1–8、计数与能力描述记录 `2026-08-24` 重型首轮实现，只用于追溯。其中出现的 Work/Edition/File、Track、ParagraphChar、CFI、`sr:*`、provenance 或 public digest 均不是当前极简 v0 的完成证据。

**Slice 1 — Contract skeleton + canonical schema authority** 已验收：稳定 namespace/schema IRI 已确认，字段约束已经成为 canonical schema/examples/offline drift check，Pages publication mapping 可重复构建。

**Slice 2 — Publication identity + fingerprinting** 已验收：strict verifier把 raw File identity与同一 verified handle上的 exact BookDocument reparse绑定；Work/Edition/File、content/chapter/substrate fingerprints、fixed UUID vectors、manifest text-resource gate、safe metadata/URI gates与 neutral no-write EPUB builder均已实现。Slice 2 + iterator acceptance为 `439 passed`；完整 affected regression set为 `538 passed, 2 failed`，两条 `attentional_v2.slow_cycle`测试/接口漂移已确认存在于 base `2d8aac2`并单列在 baseline observations。Contract/governance checks exit `0`，warning-only历史 traceability、LangChain deprecation与 decision-log reminder不冒充本 Slice缺陷；本 Slice落实既有 `DEC-155`，未建立新的产品/架构方向，因此不新增 decision-log entry。

**Slice 3 — Anchor model + serialization primitives** 已验收：exact verified-handle XHTML resource stream/ranges、strict paragraph-char→href/quote/context/chapter anchors、grapheme boundary gate、optional verified-CFI seam、Anchor UUID fixed vectors、`sr-canonical-json-v1`和 semantic digest均已实现。Canonical JSON现明确拒绝 float并限制为 interoperable safe integers，六个 Anchor坐标各自使用独立 NUL field；XHTML element/depth/parse-memory/traversal-amplification gates和 auxiliary cross-href adversarial tests均已通过两轮独立审查。Focused acceptance为 `543 passed`；完整 affected regression set为 `612 passed, 2 failed`，仍只有已单列的两条 pre-existing `attentional_v2.slow_cycle`测试/接口漂移。Default路径不生成 CFI，当前只证明 protocol seam与exact range guard，不声称 Reader/CFI interoperability。本 Slice只落实既有 `DEC-155`的已批准协议框架，没有改变产品方向、默认机制、runtime或公共路由，因此不新增 decision-log entry。

**Slice 4 — Generic Pack Builder and validator** 已验收：producer-neutral `AnnotationPackBuilder` 可从 immutable identity/anchor inputs构建 Highlight/Note完整 Pack，支持 Software/Person/Organization creator、deterministic Pack/Track/Annotation IDs、NFC/second-precision gates、canonical item sort和递归只读输出；caller-owned publication/target mappings各做一次 detached snapshot，ID、digest、validation与freeze共用同一份数据。纯 validator实现 canonical schema、cross-object ID/semantic、strict/compatible extension、bounded privacy、public IRI和有限 numeric-step CFI gate、empty/degraded accounting、frozen pre-artifact `ValidationResult`与一次性 final `ValidationReport`；兼容 extension内嵌 authority与report trust boundary也经构造性反例复核。`serialize_pack()` 对 caller state只取一次 canonical snapshot，并验证后返回同一 bytes；validator preflight只信任 exact built-in JSON scalar/key并把容器单次脱离，report schema同时锁定 package digest不得脱离 annotations JSON digest。Focused acceptance为 `636 passed`；完整 affected regression set为 `770 passed, 2 failed`，仍只有已单列的两条 pre-existing `attentional_v2.slow_cycle`测试/接口漂移。Contract与agent checks exit `0`，warning-only历史 traceability和依赖 deprecation继续单列。本 Slice落实既有 `DEC-155`而未改变产品方向、默认机制、runtime或公共路由，因此不新增 decision-log entry。

**Slice 5 — `SecondReaderProducerAdapter`** 已验收：唯一 producer-specific module只 import `attentional_v2.storage.reaction_records_file`，从 exact phase9 ledger envelope读取 current native settled rows并返回中性 `AnnotationDraft`、exact ledger SHA、真实 `input_count`、adapter成功 row digests和固定 catalog findings。Adapter只接受 `record_source=read_surface`、显式 `marginalia_kind`、unique `matched/exact_text` primary SourceRef、primitive same-chapter coordinates与Z-only 0–6 fractional timestamp；Note body在限长前NFC，Highlight不伪造body，compat/type/search/lineage/private IDs均不进入draft，也不从compat aliases推断kind。Ledger读取逐路径组件no-follow、regular-only、strict UTF-8 JSON、bounded bytes/records/depth/nodes/strings/row size，并通过fd/path前后核对与全路径重开拒绝symlink、pathname replacement和原位mutation；ledger-level异常不得row-skip。`ProducerAdapterError`只接safe code并重建catalog finding，forged finding/message不能泄露。Focused acceptance为 `46 passed`，multiple hash seeds和独立动态对抗审计均PASS；完整 Annotation Pack suite为 `682 passed`，完整 affected regression set为 `816 passed, 2 failed`，仍只有已单列的两条 pre-existing `attentional_v2.slow_cycle`测试/接口漂移。Root annotation contract、contract和agent checks均exit `0`，既有warning-only traceability与依赖deprecation继续单列。本 Slice只落实既有 `DEC-155`的producer boundary，未改变产品方向、默认机制、runtime、prompt或公共路由，因此不新增 decision-log entry。

**Slice 6 — CLI export / inspect / validate tools** 已验收：显式 `--deliverables json` exporter现在从safe book output解析run-state gate、exact BookDocument/EPUB/settled ledger snapshot，在book-scoped writer exclusion内完成adapter→anchor→builder→validator→canonical bytes，并只用最终resolved/published rows构造input-snapshot `R` frames。Completed、partial、skips与empty政策保持独立；missing/unknown/active writer和未实现detached请求稳定fail closed。Publication通过pinned all-component no-follow dirfds写入temp、fsync、no-replace immutable revision，再以单文件atomic `current.json`切换；revision files/dir冻结为`0444/0555`，existing revision必须byte/mode完全一致，pointer/JSON/report path+digest+identity现场复核，post-switch内容失败执行conditional CAS rollback且不覆盖第三方pointer。Pointer切换后的fsync failure可按既定语义返回failed但只允许留下完整immutable current，重复命令则验证后返回unchanged。Book lock锚在受信`job_registry` namespace，sidecar扫描使用pinned `leases` fd；同书acquire不能用leases-child replacement绕过，其他书heartbeat不被全局阻塞，job id不能形成越界path。Bare JSON validator与safe inspector均为bounded strict machine-readable CLI，不输出全文/local paths；真实 subprocess已完成export→unchanged→validate→inspect。Focused exporter/CLI/lease/artifact acceptance为`174 passed`，完整 Annotation Pack suite为`782 passed`；完整 affected regression set为`134 passed, 2 failed`，仍只包含已单列且可在base复现的两条`attentional_v2.slow_cycle` monkeypatch/interface drift。Root annotation contract check为`42 passed`且Pages projection有效，`contract-check`/`agent-check`均exit `0`；warning-only依赖deprecation、历史traceability debt与decision reminder不冒充Slice缺陷。本 Slice实现既有`DEC-155`和已批准public artifact placement，不改变产品方向、默认机制、runtime lifecycle、prompt或公共API，因此不新增decision-log entry。

**Slice 7 — Detached package generation** 已验收：默认export现发布canonical JSON、`<track_slug>.annotations`与deterministic validation report组成的完整immutable revision；显式`deliverables=json`仍保留development模式且被定义为最低要求，不会撤回已经存在的package。Package层是producer-neutral bounded classic-ZIP实现，只允许root `annotations.json`，固定timestamp/mode/flags/DEFLATE level且拒绝ZIP64、multi-disk、prefix/trailing bytes、extra/comment、unsafe entry/mode、encryption/data descriptor、local-central drift、8 MiB outer limit、16 MiB entry limit、ratio>100、raw-DEFLATE/CRC/EOF异常与noncanonical/semantic-invalid JSON；独立validator不以本机zlib重压缩bytes作为合法性条件。Path reader全组件no-follow、regular-only、bounded并重验path/inode；standalone O_EXCL writer只conditional cleanup自己创建的identity，第三方replacement不被unlink。JSON-only→detached默认复用旧revision exact JSON bytes，新建J/P/R revision且旧目录不变；packaged current重验package path/digest、sibling JSON、report binding、revision framing、exact file set、`0444/0555`与late mutation。Package build/write、pointer前失败保留current，post-switch package corruption执行candidate CAS rollback且不覆盖third-party pointer。Validate/inspect可在无EPUB/BookDocument/ledger时独立处理JSON或package，输出相同safe metadata且不extract/泄露正文路径。Focused package/exporter/CLI/artifact acceptance为`221 passed`，完整Annotation Pack suite为`876 passed`；affected existing regressions为`134 passed, 2 failed`，仍只有已单列的pre-existing `attentional_v2.slow_cycle` drift。Compileall/Ruff clean；本Slice只是落实既有`DEC-155`，未改变产品方向、默认机制、runtime lifecycle、prompt或公共API，因此不新增decision-log entry。

**Slice 8 — Golden fixtures, full tests, docs and contract checks** 已验收：tracked Tiny Reader提交项目原创/CC0、可离线重建的真实EPUB 3（`3158` bytes，SHA-256 `1325ba2f76406fb22a1bb0f02edd735983cc150f64cc4af5bb00fbf6d873f7a7`）、真实parser生成并复验的BookDocument、current-shaped settled Highlight+Note ledger，以及canonical JSON、single-root detached package、report、pointer和digest goldens。固定generator重建并byte-check九个generated files；path/stream parse等价、两个XHTML href、chapter fingerprint、TextQuote exact/prefix/suffix、paragraph-char与exact resource bytes逐项回查，happy path只含两个required selectors且不依赖CFI。临时真实fragment-nav EPUB继续暴露duplicate same-resource/spine-zero/CFI-null warning；旧substrate缺optional locator/HTML/sentence fields仍能CFI-free resolve，缺required href则被真实identity coherence gate拒绝。Public JSON/package/report/pointer对完整private vocabulary和local path做负向扫描，独立validate/inspect不需要producer artifacts。

Slice 8同时修复完整backend suite发现的一条Slice 6 lease-scan竞争：在已持有book lock时，逐sidecar读取复用现有job lock，保持`book -> job`锁序和原no-follow/identity gates，使合法heartbeat原子替换不再被误判为攻击性pathname race。Focused golden/lease/concurrent-resume为`55 passed`，完整Annotation Pack suite为`882 passed`；required affected regression set为`183 passed, 2 failed`，完整backend为`1882 passed, 9 failed`。剩余九项均以exact test replay在base `2d8aac2`复现并单列；新增concurrent-resume failure已消失。Ruff、compileall、fixture rebuild和diff checks通过；root Annotation Pack contract check保持`42 passed`且Pages projection有效，`contract-check`与`agent-check`均exit `0`，历史traceability和dependency warnings继续单列。旧版 Section 20 的本地 DoD 当时已闭环，Slices 1–8各自独立commit/push；该历史结论不代表 `DEC-156` 极简 v0 已完成 Slice 3 收口。

外部 IRI 当时仍须等待 workflow 进入 `main`、Pages 启用并成功部署后做 HTTP byte comparison，不得称为 live。此处“完成”仅指 `DEC-155` 重型第一实现的本地与仓库范围历史结论；Reader/Library discovery或第三方互操作属于另立任务。

### Historical DEC-155 non-goals confirmation (superseded checkpoint)

截至 `2026-08-24` 的旧 Slice 8，仓库曾按 `DEC-155` 重型 wire 实现 contract/schema/context/examples、producer-neutral离线schema loader、deterministic generated bindings/runtime resources、focused checks/Pages projection、verified EPUB publication identity/fingerprints/coherence gate、exact XHTML resource index、strict anchors、canonical serialization/semantic digest、generic Pack builder、bounded schema/semantic/privacy validator/final report primitives、只读current native settled ledger的strict producer adapter、显式JSON/detached exporter、独立validator/safe inspector、immutable public revision/atomic pointer publication，以及public-safe真实EPUB/current-shaped Highlight+Note end-to-end golden与完整anchor回查。该段仅保留历史可辨识性，不是当前极简 wire 字段清单或验收口径。Catalog/API/UI discovery未实现；当时也不声称真实CFI或外部Reader互操作。Agent prompt、Digest、Memory、reading loop、Readest、Library和public HTTP API均未修改。
