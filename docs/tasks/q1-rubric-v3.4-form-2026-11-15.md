# Q1 rubric v3.4 Note form

Status: done; initial service-based UI superseded by the offline follow-up below. Scope: implement the owner-approved Note form and isolated session protocol.
No sampling, generation, old-type conversion, Highlight form, statistical adapter or scoring snapshot.

## Implementation

- Immutable `q1-v3.4.form.v1` publication and protocol validation: `b870d6e`.
- Dedicated local entrypoint: `reading-companion-backend/scripts/q1_note_review.py`.
- Source packaging: `scripts/q1_note_context.py`; durable state/reader: `scripts/q1_note_session.py`.
- UI: `tools/q1-note-annotator.{html,css,js}`. Old v0/v1 entrypoint and forms are unchanged.
- Canonical operator/schema documentation: [rubric review](../../reading-companion-backend/experiments/rubric-review.md#published-v34-note-review-2026-11-15).

The prepared formal session is
`reading-companion-backend/state/q1_rubric_reviews/Q1-DIGEST-DIAG-001-q1-v3.4`.
It contains all 51 Notes from the existing 16-window, two-book DIAG-001 bundle,
with an empty formal judgment journal. Preparing a display session did not resample
or change the original 81-annotation bundle or its Highlights.

UI fixtures and browser evidence are isolated at
`reading-companion-backend/state/q1_rubric_reviews/qa/v3.4-20261115/`.
Three existing Notes were exercised: civil/church marriage (pass), insurance adverse
selection (N1 pass, difficulty veto), and the wedding-ring interpretation (N1 fail).
These agent-operated test judgments are not human gold or evaluation results.
The first case also has a later test revision for validation/flag-clearing checks;
unit-note exclusion was toggled on then off without rewriting annotation rows.
`example-record.json` contains a complete test record with difficulty amendment history.

## Validation

- 128 Python tests pass across new form/session, old form/review, comparison/scoring
  and iteration-provenance tests.
- 48 existing Node storage/keyboard/form tests pass; the old HTML/JS are untouched.
- Ruff check and JavaScript syntax checks pass.
- Workspace traceability check exits successfully with 18 existing warnings about
  historical evidence paths and duplicate decision IDs; none concern this new task.
- History check gives its warning-only reminder for the runtime-document update;
  the concrete reason for leaving the decision log unchanged is recorded below.
- Published-form/rubric hashes and old frozen registrations verified against the
  pre-task Git base. `experiments/scorings.jsonl` and `q1_scoring.py` remain unchanged.
- Read-only context verification covers all 51 DIAG Notes: exact anchor matches,
  chapter-bounded following text, and 16 resolved note-link occurrences in the relevant
  prefixes. No ambiguous/conflicting note resolutions were encountered. Absence of a
  resolved link is reported as unresolved, not proof that the book has no notes.
- Browser checks: first-choice mandatory, first-impression lock across reload, stage
  gating, three-way difficulty and correction, auto/manual uncertainty, N1 conditional
  required fields, independent spoiler step after N1 failure, following expand/collapse,
  uncovered reason and tag/star clearing, original-note unresolved display, unit-note
  exclusion and reversal, append-only submission, reload restore and navigation.
- Layout inspected at 1440×1000 and 390×844 and a native browser context. Natural page
  scrolling preserves long content; no horizontal overflow or clipped decision controls
  found in inspected states. Screenshots remain in the private QA directory.

## Decisions and limitations

The rubric owns options/thresholds and the annotation guide owns sequence. “其他”
failure is already in rubric 2.2. The fourth following-use branch is owner-approved
and does not replace the independent spoiler judgment. The anchor endpoint means the
end of the complete selected source range, including same-paragraph clipping.

Difficulty final choice controls veto/statistics; original choice and every from/to
transition remain available. Uncertainty sources are distinct, and automatic difficulty
uncertainty is removed when its triggering choice changes while manual uncertainty
stays. Following text cannot go beyond the chapter. Unresolved original notes do not
block; ambiguous source/target resolution stops for owner review.

Long original passages make source/decision navigation slower; added “定位锚点” and
“返回判定”. N1 help is long and defaults collapsed. The form cannot verify whether a
human really read once or knows later chapters. Timing records visible-page interaction,
not cognitive reading time. DIAG material has prior exposure; this UI cannot restore
an unseen blind experiment. Future freeze thresholds are not invented here.

The task uses two commits as requested. Generated material already lies under the
existing ignored backend `state/` boundary, so no additional ignore rule is needed.
No decision-log update: this implements the already-published rubric and approved
annotation protocol, without changing product direction or the reading mechanism;
its decisions are recoverable from the frozen form, operator contract and this record.


## Offline integration follow-up (annotator 3.3)

The owner required continuity with the original offline tool after using the separate UI.
The current entrypoint is `tools/q1-annotator.html`: same directory picker, IndexedDB
store and tab lock. Existing 3.2 stylesheet/layout is reused at runtime for v3.4;
legacy controls remain isolated from v3.4 controls. Both modes share prefix-preserving
journal append I/O. Tool version advances to 3.3; published forms and their hashes,
rubric versions and existing records are not changed. Legacy version readers accept
3.3 while the Note journal keeps `q1-note-judgment/1`.

Browser drafts replace ongoing service progress writes; existing progress is read-only
input. Locks, amendments, timing, uncertainty sources, chapter cutoff and statistics
fields retain the approved semantics. `serve`/`launch` now open the offline entrypoint;
the old standalone Note HTML provides an explicit link to it. No migration of formal
journals or cache entries is performed. No sampling, conversion or scoring work.

QA inventory/evidence is private under `state/q1_rubric_reviews/qa/offline-3.3/`.
Node protocol/storage tests run the new implementation, in addition to legacy tests.
Browser cases use isolated directory handles and copied Notes; no formal record writes.
This change restores the existing tool architecture; it does not change rubric rules
or the reading mechanism, so no new mechanism decision-log entry is needed.

Offline follow-up validation:

- 67 Node tests cover the new browser protocol and storage plus legacy keyboard/form/
  storage regressions; 128 focused Python tests pass. Browser-written test judgments
  are accepted by the existing Python Note reader, without schema conversion.
- Three existing Notes exercised with real UI input: pass, difficulty correction veto,
  and N1 failure with subsequent veto steps. P/F, Enter, focused-button Shift+Enter,
  read-only step browsing, help, source reveal/collapse, R input, multiline text,
  simulated Chinese composition, reload/close-and-reopen recovery, injected disk
  failure/retry, and switching back to the original Open Coding mode were checked.
- Browser fixtures use real isolated OPFS directory handles through the folder button;
  the macOS native directory chooser itself was not automated. The actual file:// HTML
  entry was separately opened and its folder control verified enabled. A temporary
  static test server supplies only assets for OPFS automation; no backend endpoints
  are used by the new UI. IME composition is simulated, not an OS candidate-menu test.
- Visual checks at 1600×1000, 1100×800, 390×844 and a native window. Corrected medium/
  narrow sticky-panel overlap and heading navigation under the toolbar. Long help and
  reasons flow naturally, no horizontal overflow in the inspected narrow state.
- Formal judgments remain empty. Existing formal `progress.jsonl` is 109880 bytes,
  SHA-256 `d7123d1a7c24a7c04392c6b57fe23bff236e04f22b8201c58c3d1db1264498ec`;
  these existing user drafts were not rewritten or removed.
- Workspace traceability retains its existing warnings. Runtime-doc history reminder
  is addressed by the concrete no-new-mechanism-decision rationale above.

## Desktop usability follow-up (annotator 3.4, 2026-11-17)

Tool 3.4 retains the frozen form and record schema. Decision fields and uncertainty
flags now precede collapsible full guidance; per-step expansion preferences stay in
local browser UI storage, outside judgments. The decision area can reveal the full
current Note, the header/session controls are compact, and cases open at their anchor
without revealing following text. Read-only outcomes use Chinese and return controls
name the destination. Pending steps remain disabled after a save. Old journal versions,
including 3.3, remain readable; the comparison reader only expands its tool-version
allowlist, with no new statistics or snapshot logic.

Acceptance targets PC at normal usage sizes (100% and the owner's 125% zoom), not
mobile annotation. Native Edge Computer Use verified three/two-column layouts,
full-Note disclosure, read-only first impression, explicit return target, anchor
positioning, help preference across refresh, M/Esc/Enter and step-5 restoration with
synced status. Test interaction used only the existing isolated `qa/offline-3.3/session`;
no formal judgment was entered or submitted. Screenshots are in private
`state/q1_rubric_reviews/qa/offline-3.4/` (before, medium, wide, supplementary zoom).
This was a focused usability check, not a full accessibility certification.

Validation: 73 Node tests and 111 focused Python tests pass; immutable prompt releases
and iteration provenance checks pass. Workspace agent checks pass with existing
historical traceability warnings and the existing scoring evidence-not-verified notice.
No new architecture decision is introduced: this is a usability correction within the
already-approved offline approach, so the decision log is unchanged.


## New validation batch connected (2026-11-17)

The owner requested the completed new batch, not DIAG-001 reannotation. Source is
`Q1-RUBRIC-V34-VALIDATION-001-RESULT-001` in the separate worktree
`/Users/baiweijiang/.codex/worktrees/261115-new-batch/reading-companion`, commit
`fcad1a346893`. Its branch has not been merged as part of this handoff.

The existing fixed-history exporter verifies the registered unit-set hash, each of
26 result hashes, packet hashes and exact source anchors. Window metadata comes from
the accepted packets; the existing comparison builder assigns opaque identities and
retains all 46 Notes and 10 Highlights. The existing Note session preparer creates
chapter-bounded contexts and a seeded mixed-book order (20261115). Counts verified:
18 Bovary Notes and 28 Sapiens Notes. Original-note resolution: 10 cases resolved,
36 unresolved; no ambiguity raised. No model calls or original-result edits.

Private paths relative to backend:
- Active formal session: `state/q1_rubric_reviews/Q1-RUBRIC-V34-VALIDATION-001-q1-v3.4/`.
- Source export, canonical bundle, blind identity map and receipt:
  `state/experiments/Q1-RUBRIC-V34-VALIDATION-001/annotation-handoff/`.
- `receipt.json` binds the source/result registration, unit set, session manifest,
  randomization and frozen stability receipt without disclosing selection identities.
  The blind key preserves source/unit/original marginalia IDs for later stability use.

Native Edge opened this session and displayed `1 / 46`, `0 / 46`, synchronized,
first impression unselected. No judgment was entered by the agent. DIAG-001 and QA
sessions remain separate. This is an artifact handoff using existing validated code;
no form/schema change, score snapshot, quality assessment or architecture decision.


## Generation branch merged (2026-11-17)

Owner authorized merging `codex/261115-new-batch` into main after both parallel tasks
completed. Its three commits (`0257f03`, `48d463e`, `fcad1a3`) merged without conflicts;
the experiment log retains the main prefix plus the five branch additions. All 596
private evidence files were copied from the generation worktree into the matching
main-workspace `state/experiments/Q1-RUBRIC-V34-VALIDATION-001/` paths and verified
byte-for-byte. Completed job records were copied only where absent. Neither the
source worktree nor the frozen stability sample was deleted or changed.

The active session was backed up under
`state/q1_rubric_reviews/merge-backups/20261117T115456Z/` before merging. Its immutable
files remain identical, and its journal prefixes remain intact (owner appends during
annotation are allowed). Browser state was not touched. No generation or scoring
snapshot was run, and no push was requested.


### First-impression selection redraw fix (2026-11-17)

The 3.4 Chinese read-only display change accidentally passed a translated label into
the editable first-impression radio renderer. A saved `pass`/`fail` consequently
redrew as unselected. Restore the protocol value at that call site; keep translation
only in labels/read-only summaries. Regression coverage renders null/pass/fail and
checks the selected input after redraw. No journal, schema, lock or assessment change.


### 2026-11-17：校验提示与结论说明修复

- 离线适配器仅在协议转换被拒绝时标记 FORM_VALIDATION；磁盘、浏览器存储和版本冲突仍走保存恢复路径。界面校验提示显示具体缺项，不再显示恢复授权按钮。
- 结论步骤使用可读的合成规则提示，避免把冻结表单说明的 Markdown 表头当成摘要。冻结表单、规则及数据格式不变。
- 新增测试覆盖校验/存储错误区分、重试入口显隐和结论摘要；Computer Use 在独立 QA 会话复现“其他写法缺说明”，补齐后推进到结论并提交。正式会话 5 个文件前后哈希一致，未刷新正式标签页。
- QA 路径：`state/q1_rubric_reviews/qa/flow-3.4-20261117/`。只修界面反馈，未改变任务状态、产品方向或评分口径。


### 2026-11-17：27 寸桌面布局调整

v3.4 Note 独立视图改为左原文（46%）、右批注与判定（54%），取消宽屏第三列的空白。正文保持原字号，布局最大宽度 1600 CSS px；紧凑步骤、进度、选项间距，保留自然页面滚动、独立原文滚动与 sticky 提交操作。旧表单布局与冻结定义不变。

Computer Use 在当前桌面 Edge 100% / 125% 缩放检查初始页、选项选中、锚点定位、推进费劲和 N1 以及长表单滚动。独立测试目录 `state/q1_rubric_reviews/qa/desktop-layout-20261117/` 保存截图；正式会话 5 个文件哈希一致，未刷新正式标签页。此次是同一工具的显示调整，不改变任务状态、评分规则或数据格式。


### 2026-11-17：全程键盘操作

补齐 D/B/W/X/T 选项组定位、N 拿不准、C 返回当前判定、A/E/O/H/L 上下文入口；保留原有快捷键及原生 Tab/方向键/空格。保存重绘恢复控件焦点与文本选区，不抢占已经移动的焦点；缺项定位到对应输入。帮助弹窗隔离全局快捷键。冻结表单、记录格式、旧表单不变。

79 项 Node 测试通过（新增重绘焦点与键盘作用域测试）。Computer Use 在独立 desktop-layout-20261117 测试会话中，仅键盘完成通过、N1 不过及未覆盖三条记录，覆盖后文展开、失败类型“其他”缺项定位、手动拿不准、标签、提交下一条和刷新草稿恢复。费劲修正入口可通过 Tab 到达；本次 UI 未产生实际费劲值修改，值变更保留由协议测试验证。正式会话 5 个文件前后哈希一致，未刷新正式页。


### 2026-11-17：补齐费劲页直接快捷键

根据用户截图反馈，组定位之外增加 Q/G/Z 直接选择费劲三选一、Y 复述、I 改写；M 整条理由和 0 未覆盖补上可见提示，P/F 同样标在二选一旁。输入框内不拦截正常文字，Esc 后可使用快捷键。30 项相关 Node 测试通过；本次未操作正式会话或修改判定文件。


### 2026-11-17：费劲选项按 rubric 展开文案

仅显示层展开三选一：一遍准确复述；说不出或说偏但可更直白且不丢内容；说不出或说偏，想法本身复杂、表达已尽量清楚，无法更直白且不丢内容。显示否决/拿不准效果，保留 Q/G/Z，长选项分行。修正下拉、只读摘要及快捷键帮助同步。历史枚举、冻结表单和已有标注文件均未修改。31 项相关测试通过，覆盖实际 radio 的显示文案、旧值及选中状态兼容。


### 2026-11-17：修复费劲长文案重绘丢选中

长文案改动误将显示标签传给 radios 的选中值参数，改回原始 choice。新增覆盖实际渲染调用的 null/全部三个历史值测试，避免只测控件而漏掉调用处。Computer Use 在独立 difficulty-redraw-20261117 测试会话验证鼠标选 G、Z/Q 快捷键、自动拿不准、刷新保持 Q、Enter 进入 N1。正式页未填写或刷新；记录及冻结定义不变。32 项相关测试通过。


### 2026-11-17：已完成步骤可返回纠错

已完成的 N1 及后续步骤增加“修改此步 · Shift+R”，尚未提交也能使用。保留输入与后文查看记录，清除本步及后续步骤完成时间，重新确认后计算结论；旧提交仍留在追加日志中。第一印象锁定、费劲专用修正机制不变，冻结表单和记录枚举不变。

协议与视图回归覆盖返回编辑、保留值、失效后续确认、禁止重开第一印象/费劲及无效步骤、快捷键输入保护。Computer Use 在隔离 difficulty-redraw-20261117 会话中完成 N1 后返回，验证修改入口与 Shift+R，看到原失败类型保留且控件恢复可编辑。随后用户切换浏览器做其他工作，因此停止 UI 操作；未在界面走完改判重提，重提由协议回归覆盖。此修复不改变任务状态或产品方向。

验证：88 项 Node 测试、46 项 Python 会话测试通过，git diff --check 通过。正式会话 5 个文件与修复前 SHA-256 完全一致。


### 2026-11-17：第二步即时返回修正

第二步回看也提供“修改此步 · Shift+R”，展开修正表单并聚焦选项；取消必须等到结论页才能修正的限制。保留首次值、最终值、from/to 历史和自动拿不准逻辑，结论按最终值计算。第一印象仍不可修改；第 3～7 步沿用返回编辑。正式会话和冻结定义未修改。90 项 Node、47 项 Python 测试覆盖入口、即时修正、原值和历史保留；未操作用户浏览器。本次是修正入口补齐，不改变任务状态或产品方向。


### 2026-11-17：返回步骤直接使用原表单

按用户反馈撤掉“修改此步”中间入口、Shift+R 和独立费劲修正表单。点击已完成的第二步及后续步骤，直接显示原来的选项、输入、快捷键和继续按钮，保留已填内容；返回处及之后重新确认。第一印象仍只读。第二步通过原表单保存时自动追加 from/to/时间，保留初值；相同值重复保存不算修正，结论和自动拿不准依据最终值计算。协议的既有 amend 操作保留用于兼容，冻结定义和历史记录不变。

91 项 Node、47 项 Python 测试通过，覆盖所有可编辑步骤的直接返回、第二步原值/修改链/自动与手动拿不准、旧提交前缀保留和新修订提交。隔离 QA 脚本副本已同步；本轮 Computer Use 在获取浏览器时因当前 URL 不允许操作而被中止，因此未完成本轮 UI 实测。没有绕过工具限制或操作正式页，正式会话 5 个文件哈希一致。这是同一工具的交互简化，不改变任务状态、评分口径或产品方向。
