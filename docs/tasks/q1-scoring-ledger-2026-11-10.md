# Q1 评分账与私有证据归位

状态：实施中。用户授权四个独立提交，不 push；不跑模型，不修改 prompt、rubric、表单或已有标注。

1. 已将 DIAG-001 的 914 个文件独立复制到 `reading-companion-backend/state/experiments/Q1-DIGEST-DIAG-001/files`，逐文件大小和 SHA-256 一致。manifest 在父目录，哈希绑定在追加的 LOCATION-001 记录。原工作树、软链接、文件字节均保留。
2. 精确接入 `b431889` 的历史揭晓日志行、任务证据及 ledger 更新；保留主线较新的 rubric 发布记录和标注器 2.5。
3. 下一步：评分账、补登与确认后的收尾、INDEX、一次本机备份及恢复复算。

验证：2 项快照测试通过，覆盖独立副本、拒绝覆盖、篡改检测和拒绝隐式跟随软链接；ledger 与冻结溯源检查通过。
