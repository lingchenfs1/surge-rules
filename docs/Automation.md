# AI、Meta 与 Claude 自动更新

GitHub Actions 每天 UTC 22:23（次日 Asia/Taipei 06:23）执行，也可以在 Actions → Update AI Meta and Claude rules → Run workflow 手动运行。GitHub 定时任务可能延迟；公开仓库长期无活动时，定时任务可能被平台停用，请留意 Actions 状态。

## Meta 发布方式

- 拉取 `config/meta-upstreams.json` 中的 15 份上游文件。
- 保留当前规则，只补充缺项，不自动删除已收录域名；父后缀可替代重复的子域规则。
- 新域名需至少两个来源家族支持。v2fly 和 MetaCubeX 归为同一家族，其他项目仍可能共享上游，票数不代表所有权验证。
- 初次人工筛选排除的候选域名保持排除；未来需人工复核后修改排除表。
- 不自动添加关键词、IP 网段、ASN，避免旧云服务地址或宽泛匹配。当前三个 ASN 保持不变。
- 共享平台后缀禁止自动加入；现有精确主机不会自动升级为更宽的后缀规则。
- 只出现于一个来源家族的候选记录在 `docs/meta-sync.json` 的 pending 中，等待人工复核。
- 任一来源失败、无有效域名或单次新增超过 25 条时任务失败，不提交部分结果。
- 更新 `rules/Meta.list`、`snippets/Meta.txt` 和来源哈希报告；有变化才提交到 main，不产生每日空提交。

## AI 发布方式

Meta 同步完成后，先通过 scripts/update_claude.py 同步5份Claude清单并生成专属/可选共享规则，再通过 scripts/update_ai.py 同步10份AI清单（含 Cursor、Windsurf 专项源）、增量去重、移除 Meta 和 Claude 专属条目并运行隐私扫描。AI 抓取及构建在临时目录完成，失败不覆盖发布文件；整个工作流任一步失败均不推送。新域名可自动补充，新关键词/IP/ASN/URL 正则待人工复核。详见 [AI 规则说明](AI.md)。

订阅地址保持不变。工作流仅使用 GitHub 提供的临时 GITHUB_TOKEN，权限为本仓库 contents:write，无需保存个人令牌。checkout 固定到提交 SHA；上游仅作为数据解析，绝不执行。

## 验证与范围

CI 使用 Python 标准库解析、格式校验、去重和测试。GitHub Linux runner 不运行 Surge 本体；首次上线已在本机做 Surge 离线语法校验。CI 的通过不等于 App 全功能验证，也不保证新域名确属 Meta。

自动更新发生在 GitHub，不访问本机 Surge 配置。手动订阅后，Surge 是否刷新规则由用户现有设置决定。

## 隐私

后续人工提交使用 GitHub noreply 邮箱，自动提交使用 github-actions[bot] noreply 邮箱。仓库仅保存规则和公开上游资料，不应提交个人完整配置、节点凭据、设备身份或请求日志。

发布前扫描跟踪文件及新增文件中的个人邮箱、常见令牌、私钥、本机用户路径、MAC 和私网 IPv4；检测到风险时失败。扫描不是所有敏感信息的完备证明，仍须避免提交个人数据。

Claude 自动更新边界、未知域名待复核和可选共享依赖说明见 [Claude](Claude.md)。
