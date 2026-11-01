- 我审完后，判断是：

  **这篇 Memory Management & Evolution Design v0 质量很高，可以作为设计 5 的 accepted draft 使用。**
  但和前几篇一样，**它还不应该原封不动交给 Codex 实现**。更合适的状态是：

  ```text
  Status: Accepted draft with minor patch before implementation
  Design quality: 8.7 / 10
  As upstream input: 可用
  As direct implementation input: 还需要压缩成 handoff packet
  Rerun needed: No
  ```

  这篇文档完成了它该完成的核心任务：把已经形成并 settle 的 memory 后续如何被 **更新、刷新、冷却、恢复、合并、链接、解决、废弃、软失效、替代、提升、重解释和审计** 说清楚了。它没有重新定义 Memory，也没有滑向 Retrieval / Evaluation / Codex implementation，这一点很重要。设计路线里本来就把设计 5 定位为 Memory Management & Evolution，目标是解决 lifecycle、supersede、cool、resolve、store-specific legal operation matrix、destructive overwrite / soft invalidate 等问题。

  ## 总体评价

  这篇最强的地方是：它终于把之前散落在 Memory Ontology 和 Formation 里的生命周期词汇，提升成了一个正式的 **evolution contract**。

  P0 已经要求 lifecycle 必须区分 visibility 与 semantic validity，并且坚持 `LLM proposes; deterministic runner settles`。 Memory Ontology 也明确说，store 的 lifecycle meaning 只是 ontology-level semantic boundary，最终 operation matrix 要留给 Management / Evolution 页面。 这篇正好接住了这个责任。

  它做对了几个关键判断：

  ```text
  cooling ≠ invalidation
  resolve ≠ permanent completion
  drop ≠ normal semantic deletion
  supersede ≠ destructive overwrite
  deferred candidate ≠ memory truth
  reaction_records ≠ semantic memory
  knowledge_activations ≠ source truth
  audit / evaluation artifacts ≠ runtime memory
  ```

  这些判断非常关键。它们会直接影响后续 Retrieval、Projection、Audit、FVI 诊断，以及 Codex 实现时如何处理 stale memory。

  ## 做得好的地方

  ### 1. Scope 很稳，没有重开上游设计

  它明确继承 P0、Memory Ontology、Memory Formation & Settlement、Planning Ontology、Navigation Policy，只设计 **settled memory 的 lifecycle 与 evolution contract**。这个边界是对的。

  尤其它没有重新发明 store identity，而是继承：

  - `active_attention`
  - `concept_registry`
  - `thread_trace`
  - `reflective_frames`
  - `reaction_records`
  - `knowledge_activations`
  - `reconsolidation_records`

  这一点很重要，因为 Memory Ontology 已经完成了 store 身份定义，设计 5 应该做的是“这些 store 如何演化”，而不是重新讨论“它们是什么”。

  ### 2. 当前实现理解比较扎实

  文档正确抓住了当前实现里的 lifecycle 线索：

  - `StateOperationType` 已有 `cool / drop / promote / supersede / reactivate / resolve` 等词；
  - `state_ops.py` 对 `active_attention` 已支持 create / update / reactivate / cool / resolve / link / drop；
  - concept / thread 当前有 update / resolve / drop / source_refs merge；
  - `reflective_frames` 已经有 `supersede_reflective_item`，并且是不改写旧 statement 的 soft supersede；
  - `reaction_records` 与 `reconsolidation_records` 是 append-only；
  - `knowledge_activations` 已有 weak / plausible / strong / rejected / dropped 这样的 warrant lifecycle。

  这说明它不是抽象写一个“记忆管理理论”，而是在真实 `attentional_v2` 机制上收紧语义。

  ### 3. Visibility lifecycle / Semantic validity lifecycle 的区分很关键

  这是整篇最有价值的设计之一。

  它把 lifecycle 分成：

  ```text
  Visibility lifecycle:
  active / hot / cooling / cooled / dormant / reactivated / hidden_from_projection / carried_forward / not_carried
  
  Semantic validity lifecycle:
  provisional / source_supported / refined / resolved / superseded / invalidated / rejected / contradicted / uncertain / retired
  ```

  这个区分非常必要。因为阅读中的很多变化不是“旧理解错了”，而是“暂时不需要继续显式带着它读”。如果没有这个区分，系统很容易把 `cool` 当成失效，把 `drop` 当成删除，把 `resolve` 当成永久完成。

  Memory Assessment 也指出，当前 lifecycle 仍像词汇表，不是成熟演化机制；特别是后文修正前文时，必须优先使用 supersede / invalidate / retire，而不是 destructive overwrite。 这篇正面补上了这个缺口。

  ### 4. Store-specific operation matrix 很可用

  每个 store 的 legal operations 写得比较清楚，尤其这几组判断很稳：

  ```text
  active_attention:
  主要是 visibility lifecycle，不承载 stable semantic truth。
  
  concept_registry:
  概念本体通常不被 resolve 成“完成”；resolve 只关闭 attached ambiguity / pending question。
  
  thread_trace:
  thread 是 development line，不是 concept dictionary；可以 dormant 后 reactivated。
  
  reflective_frames:
  只能由 slow-cycle / chapter boundary 正常写入；read-path 不写。
  
  reaction_records:
  visible trace ledger；strong reaction 不自动进入 semantic memory。
  
  knowledge_activations:
  warrant ledger；不能单独驱动 detour / recommendation。
  
  reconsolidation_records:
  reinterpretation ledger；不是 reflective frame，也不替代 supersede。
  ```

  这些判断会直接帮助后续 Retrieval / Utilization 页面决定：哪些 item 可以作为 current truth，被普通 projection 使用；哪些只能作为 lineage / audit / visible trace 使用。

  ### 5. “后文修正前文”设计是亮点

  第 7 节很好。它区分了：

  ```text
  update / refine:
  旧 item 仍 source-supported，只是后文补充精度。
  
  resolve:
  local question / ambiguity / tension 被关闭。
  
  supersede:
  后文建立了新理解，替代旧 current understanding。
  
  invalidate / reject:
  后文 source 或 warrant failure 证明旧 claim 不应继续使用。
  
  reconsolidation:
  后文改变了 earlier visible reaction 的意义。
  
  active_attention cooling:
  只是 hot focus 不再拉动近端阅读。
  ```

  这正是 reading memory 的核心场景：不是“一次性抽取事实”，而是“随着阅读推进，理解不断被修正”。这一节可以成为后续 Retrieval、FVI、Evaluation 的重要上游输入。

  ### 6. Deferred candidates 处理得好

  它继承了 Formation & Settlement 里的 deferred candidate carrier，并进一步定义：

  ```text
  deferred candidate is not settled memory
  不能进入 prompt-facing projection
  不能被 Retrieval 当 memory item
  可以被 Management / slow-cycle 作为 candidate evidence 读取
  使用时必须重新 admission / validation / settlement
  ```

  这解决了 Formation 设计里一个重要问题：defer 不能等于丢弃，也不能等于写入 memory truth。Formation 设计本来也已经把 deferred candidate 定义为 candidate evidence，而不是 settled memory truth。 这篇进一步把它放进 lifecycle 里，方向正确。

  ### 7. Projection / Retrieval implications 很有用

  它虽然没有设计 Retrieval，但给了后续 Retrieval 必须继承的约束：

  ```text
  superseded / invalidated / rejected items 不应作为 current truth 普通返回；
  cooled / dormant items 只是低优先级，不是假；
  provisional items 必须带 marker；
  knowledge activation 必须带 warrant/status marker；
  reaction_records 必须带 visible trace marker；
  deferred candidates 不进入 projection。
  ```

  这非常重要。后续 Memory Retrieval & Utilization 如果没有这些 status-aware constraints，很容易把旧 memory、visible trace 或 prior activation 塞回 prompt，导致 FVI。

  ### 8. 没有复杂化

  它没有新增 store，没有引入 memory manager agent，没有引入 vector DB / graph DB / Memory OS，也没有把 management 做成一个自治 agent。这符合 P0 的复杂度守门线。

  ## 主要需要修改的地方

  整体不用重跑，但我建议做一次 **acceptance patch**。主要是让它更适合作为后续设计和实现输入。

  ### 1. 需要明确：Management 是 contract，不是新 actor

  文档里多次使用：

  ```text
  deferred_to_management
  Management / slow-cycle reads candidate
  Management can ...
  ```

  这在设计语境里可以理解，但 Codex 或后续模型可能会误以为要新增一个 `MemoryManager` 节点或 agent。

  建议加一段：

  ```text
  Memory Management is a lifecycle contract, not a new runtime actor.
  
  In v0, management actions are executed through existing surfaces:
  - settlement / state_ops for deterministic local lifecycle actions;
  - slow-cycle for promotion, reconsolidation, carry-forward, supersede candidate review;
  - manual/admin repair for exceptional audited correction;
  - evaluation only reports failures and never mutates runtime memory.
  
  `deferred_to_management` means “requires a later lifecycle decision surface,” not “send to a new manager agent.”
  ```

  这是最重要的 patch。否则后面容易从“管理机制”滑向“管理 agent”。

  ### 2. Lifecycle vocabulary 需要分成 conceptual taxonomy 和 MVP implementation subset

  现在 lifecycle 词很多：

  ```text
  active / hot / cooling / cooled / dormant / reactivated / hidden_from_projection / carried_forward / not_carried
  provisional / source_supported / refined / resolved / superseded / invalidated / rejected / contradicted / uncertain / retired
  ```

  作为设计语义是好的，但如果直接实现会太大。

  建议加一个 MVP subset：

  ```text
  MVP visibility markers:
  - active
  - cooling
  - cooled
  - dormant
  - carried_forward
  - not_carried
  
  MVP semantic validity markers:
  - provisional
  - source_supported
  - refined
  - resolved
  - superseded
  - invalidated
  - rejected
  - retired
  
  MVP lineage markers:
  - source_ref_added
  - supersedes_id
  - superseded_by_id
  - invalidating_source_refs
  - conflict_source_refs
  - promoted_from
  - deferred_candidate_used
  ```

  其他如 `hot / hidden_from_projection / contradicted / uncertain / support_expanded / fallback_source_ref_rebound` 可以先作为 reason / audit marker，不一定进入第一轮 enum。

  这能避免 implementation handoff 一开始就被状态空间压垮。

  ### 3. `drop / retire / hide / remove` 还要再收紧

  文档已经说 `drop` 默认不是正常语义删除，但不同 store 的 drop 仍可能被实现混淆。

  建议加一条统一规则：

  ```text
  In v0, drop must be typed by effect:
  
  - projection_drop:
    remove from hot/prompt-facing view, not from durable store.
  
  - repair_drop:
    remove or tombstone corrupted/mistaken entry, always audited.
  
  - policy_hide:
    hide a visible reaction from user-facing surface, preserving internal lineage unless compliance requires deletion.
  
  - hard_delete:
    not a normal lifecycle operation; allowed only under explicit compliance/admin policy.
  ```

  并补一句：

  ```text
  For semantic stores, prefer retire / supersede / invalidate over drop.
  For reaction_records, prefer hide / reconsolidate over delete.
  For audit artifacts, never drop as lifecycle management.
  ```

  这会让 Codex 更不容易把 `drop` 实现成普通删除。

  ### 4. `retire` 需要更明确的 store-specific含义

  `retire` 是一个好概念，但当前文档对它的使用还略抽象。建议增加：

  ```text
  retire means:
  - no longer used in normal current projection;
  - still source-supported or historically valid;
  - still accessible for explicit lineage / audit / historical recall;
  - does not imply falsehood;
  - does not erase source_refs.
  
  Allowed normal writers:
  - slow-cycle
  - management repair / admin
  - possibly settlement only when applying a pre-authorized lifecycle operation
  
  Not allowed:
  - ordinary Read-path
  - Navigation
  - Evaluation direct write
  ```

  特别是 concept/thread/reflective frame 都会用到 retire。这个定义会帮后续 Retrieval 判断 retired item 是否可被 active recall 取回。

  ### 5. `supersede` 需要补充 same-store / cross-store 边界

  现在 supersede 定义很好：旧 item 保留，新 item 替代 current semantic role。但还可以补一个边界：

  ```text
  Same-store supersede is normal:
  - concept → concept
  - thread → thread
  - reflective_frame → reflective_frame
  
  Cross-store supersede is exceptional:
  - active_attention should normally cool/resolve, not supersede a concept;
  - reaction reconsolidation does not supersede concept/thread memory;
  - knowledge_activation rejection does not supersede concept_registry unless a separate source-grounded concept update exists.
  ```

  这样能避免后续出现 “一个 reaction supersedes 一个 concept” 或 “knowledge activation rejected 后直接 invalidate concept” 这种跨层混乱。

  ### 6. Projection 需要区分 current-truth projection 和 lineage projection

  文档已经说 stale item 不应进入普通 projection，但后续 Retrieval 可能仍需要取回 superseded / invalidated items 解释演化。建议把 projection 分成两类：

  ```text
  current_truth_projection:
  - excludes superseded / invalidated / rejected items;
  - includes provisional only with marker;
  - includes cooled/dormant only at low priority.
  
  lineage_projection:
  - may include superseded / invalidated / rejected items;
  - only for correction_lineage, audit_explanation, FVI diagnosis, reconsolidation review;
  - must carry warning markers and current replacement IDs.
  ```

  这会直接帮助后续 Memory Retrieval & Utilization 页面。否则 “不进普通 projection” 和 “完全不可取回” 容易被混淆。

  ### 7. `management_audit` 需要一个 MVP event subset

  文档给了一个不错的最小字段表，但为了 implementation readiness，建议再压一层 MVP：

  ```text
  MVP ManagementEvent:
  - management_event_id
  - timestamp
  - actor
  - target_store
  - target_id
  - operation
  - previous_visibility
  - new_visibility
  - previous_validity
  - new_validity
  - source_refs_used
  - source_refs_added
  - supersedes_id
  - superseded_by_id
  - invalidating_source_refs
  - reason_code
  - outcome
  - projection_impact
  ```

  暂缓：

  ```text
  manual_repair_reason
  policy_version
  slow_cycle_run_id
  linked_item_ids
  deferred_candidate_ids
  ```

  不是说这些没用，而是第一轮可以不全实现。

  ### 8. `knowledge_activations.change_use_policy_mode` 要防止变成策略写入

  文档里允许 `change_use_policy_mode`，方向可以接受，因为当前 `knowledge.py` 本来有 mode 切换。但这个字段容易滑向 procedural/policy memory。

  建议加一句：

  ```text
  change_use_policy_mode is a local knowledge-use gating result, not procedural memory and not prompt/policy self-modification.
  It must be derived from current activation statuses and warrants, not from free-form reflection.
  ```

  这样能防止它变成“模型自己改阅读策略”。

  ### 9. Slow-cycle 的 authority 还可以再轻微收紧

  文档说 slow-cycle 可以做 `supersede candidate review`，但 `review` 和 `apply` 的边界要清楚。

  建议：

  ```text
  Slow-cycle may propose or select supersede / invalidate / retire candidates.
  Final state mutation still goes through deterministic state_ops / settlement-style application.
  Slow-cycle is not allowed to silently rewrite stores as free-form JSON.
  ```

  这其实和 P0 一致：LLM proposes; deterministic runner settles。

  ## 不需要修改的地方

  我不建议重新加入大量外部文献分析。附录已经够了，而且没有把 Evidence Pack 当作直接依据，这一点是好的。

  我也不建议在这篇里展开完整 Retrieval taxonomy。现在它只给 lifecycle-facing constraints，刚刚好。Retrieval 页面后面要单独做。

  也不建议现在写 Codex task。它的 Implementation Readiness Notes 已经区分了 ready / needs later design / explicitly not now，这很符合我们前面的经验。

  ## 可用性判断

  这篇可以作为后续以下页面的上游输入：

  ```text
  Memory Retrieval & Utilization Design
  Memory Audit & Evaluation Design
  Slow-cycle / Macro-planning Design
  Detour / Look-back / Active Recall Policy
  Recommendation Policy
  Implementation Handoff
  ```

  尤其对 Retrieval 很关键，因为它已经定义了：

  ```text
  哪些 memory 是 current truth；
  哪些只是 cooled/dormant；
  哪些 superseded / invalidated / rejected；
  哪些只能 lineage recall；
  哪些不应进入 ordinary projection。
  ```

  但它不能直接交给 Codex 做完整实现。进入实现前，至少要先压成一个 **Memory Management Implementation Handoff Packet**，包括：

  ```text
  1. MVP lifecycle status vocabulary
  2. store-specific operation permissions
  3. management audit MVP fields
  4. projection filtering rules
  5. source-ref-preserving merge/supersede rules
  6. backward compatibility behavior
  7. explicit non-goals
  ```

  ## 建议的 acceptance patch 清单

  可以不重写全文，只加一个短 patch：

  ```text
  Memory Management & Evolution Design v0 — Acceptance Patch
  
  1. Clarify that Memory Management is a lifecycle contract, not a new runtime actor.
  
  2. Split lifecycle vocabulary into:
     - conceptual taxonomy
     - MVP implementation subset
  
  3. Clarify drop / retire / hide / hard delete:
     - drop is not ordinary semantic deletion
     - hard delete only under compliance/admin policy
     - semantic stores prefer retire / supersede / invalidate
  
  4. Define retire more explicitly:
     - not current projection
     - still historically/source valid
     - available only for explicit lineage / audit / historical recall
  
  5. Clarify same-store vs cross-store supersede:
     - same-store supersede normal
     - cross-store supersede exceptional and must not bypass store ontology
  
  6. Split projections:
     - current_truth_projection
     - lineage_projection
  
  7. Add MVP ManagementEvent fields.
  
  8. Clarify knowledge activation use-policy mode:
     - gating result, not procedural memory or prompt self-modification
  
  9. Clarify slow-cycle:
     - may propose lifecycle changes
     - deterministic state_ops / settlement applies final mutation
  ```

  ## 最终判定

  我会把这篇标记为：

  ```text
  Status: Accepted draft with minor patch
  Use as upstream input: Yes
  Use as direct Codex input: No
  Rerun needed: No
  ```

  它最重要的贡献是把 Memory 从“写入以后就放在那里”推进到了真正的阅读状态演化：

  ```text
  memory can cool without becoming false;
  memory can be resolved without being finished forever;
  memory can be superseded without being overwritten;
  memory can be invalidated without being deleted;
  visible reactions can be reconsolidated without becoming semantic memory;
  knowledge activations can be rejected without becoming book truth.
  ```

  这就是设计 5 该完成的事情。

  ------

  你这句话可以用英文这样说：

  > The Memory Management & Evolution design is done. Could you review its quality and usability?

  Useful expression: **lifecycle contract**，意思是“生命周期契约”。例如：

  > This document should define a lifecycle contract, not introduce a new memory manager agent.