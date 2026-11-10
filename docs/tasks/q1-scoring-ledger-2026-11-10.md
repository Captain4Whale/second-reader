# Q1 评分账与私有证据归位

状态：完成。用户授权四个独立提交，不 push；不跑模型，不修改 prompt、rubric、表单或已有标注。

1. 已将 DIAG-001 的 914 个文件独立复制到 `reading-companion-backend/state/experiments/Q1-DIGEST-DIAG-001/files`，逐文件大小和 SHA-256 一致。manifest 在父目录，哈希绑定在追加的 LOCATION-001 记录。原工作树、软链接、文件字节均保留。
2. 精确接入 `b431889` 的历史揭晓日志行、任务证据及 ledger 更新；保留主线较新的 rubric 发布记录和标注器 2.5。
3. 评分账、确认后的收尾、中文 INDEX、本机快照与恢复复算均已完成。

验证：2 项快照测试通过，覆盖独立副本、拒绝覆盖、篡改检测和拒绝隐式跟随软链接；ledger 与冻结溯源检查通过。


评分账已补登三个独立范围：第一批开放编码（303+302 修订，67 单元）、DIAG 混合盲标（313 修订，16 单元）、q1-v0 重判（空快照，待标）。全部结果由脚本从冻结输入复算，开放编码的条款计数不适用；登记日期不冒充标注日期。

收尾文字经用户确认并追加其 Highlight 限定句，写入 CLOSE-001。其结论只使用 Note：同 prompt 下 B 明显更好，不支持 prompt 为主因，模型配置是重要杠杆；模型/推理未拆分，prompt 作用未检验。模型对比暂停，后续 Luna medium，GPT-6 Sol high 留作参照。


## INDEX 与备份验收

主表三个评分范围各显示最新快照，详细证据与历史快照折叠。自动合并同一实验的关联日志；`--check` 能拒绝过期 INDEX，`make agent-check` 已接入评分及总表检查。数值未手填、原标注未改。

本机备份：`/Users/baiweijiang/Backups/second-reader/20261110T121328Z/`（2026-11-10 20:13 +08:00）。1,528 个文件，233,581,245 字节；manifest SHA-256 `85377a77cf7e9e7b31e49d3b731d1146d4c9f743bdac95174d7b7ab93a93df1c`。

独立恢复路径：`reading-companion-backend/state/backup_verification/20261110T121328Z/restore/files/reading-companion-backend`。逐文件哈希一致，224 个 JSONL 解析通过，三个评分从恢复目录内的冻结证据复算一致，恢复的 INDEX 检查通过；原始源目录清单未变。详细 `verification.json` 同时保存在备份根目录与本机验证目录。

备份范围为 Q1：DIAG 所有产物/请求/映射/标注、原整书产物、冻结清单引用的四个批次、当前重判会话、评分快照、私有 rubric 示例和 few-shot，以及复算配置和脚本。保留批次仅字节备份、JSON 语法校验，没有评分或审阅。第一次暂存检测到旧标注工作树 QA 浏览器 profile 的软链接而明确停止；改为从冻结 dev/holdout 清单选择真实批次后通过，失败暂存保留且没有成功备份标记。

未安装定时任务，未上传外部服务，未删除任何原目录或旧备份。此快照不包含今后的新标注；后续应手动再备份。四个本地提交，不 push。

最终检查：50 项相关 Python 测试通过（含追加允许、旧行改写拒绝的 Git 前缀回归）；冻结 prompt（3 版）、rubric/form、单元清单及原始 legacy 标注前缀检查通过；全部评分证据复算通过。`make agent-check` 的契约/OpenAPI/前端检查通过，新增评分/INDEX 检查通过；本任务新增的状态引用告警已修复，只余 17 条原有历史溯源告警。
