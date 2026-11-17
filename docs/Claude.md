# Claude 独立规则

2026-11-17 从通用 AI 清单拆分，结合 Claude 官方网络要求和 5 个社区清单整理。当前数量见 [同步报告](claude-sync.json)。未修改本机 Surge 配置。

## 文件和使用

- `rules/Claude.list`：16 条专属/品牌服务与网络兜底规则，覆盖 Claude 网页、API、Claude Code、登录、MCP/Artifacts、Chrome 桥接等主机所属域名。
- `rules/Claude-Shared.list`：14 条**可选**共享依赖；日志、客服、下载、GitHub、npm 等也被其他 App 使用。
- `snippets/Claude.txt`、`snippets/Claude-Shared.txt`：对应粘贴版，策略占位名为 CLAUDE。
- `snippets/Claude-processes.txt`：从原 AI 进程示例迁出的 macOS Claude Desktop 进程规则。AI-processes.txt 仅保留 Alma。

将 CLAUDE 替换为已有策略组或节点名，放入 [Rule]，位置在 AI 规则及其他可能覆盖 Claude 的规则之前：

```ini
RULE-SET,https://raw.githubusercontent.com/lingchenfs1/surge-rules/main/rules/Claude.list,CLAUDE,extended-matching
# 仅在需要把共享依赖也交给 CLAUDE 时启用；会影响其他 App 的同域名流量：
# RULE-SET,https://raw.githubusercontent.com/lingchenfs1/surge-rules/main/rules/Claude-Shared.list,CLAUDE,extended-matching
RULE-SET,https://raw.githubusercontent.com/lingchenfs1/surge-rules/main/rules/AI.list,AI
```

应用规则前需自行准备对应策略；本仓库不会创建策略组。保留 AI 作为余下服务的清单。本机如果还配置旧的散落 Claude/AI 规则、旧进程规则，仍可能抢先匹配；发布仓库文件不会自动移除它们。

## 拆分边界

从 AI 发布结果移除了 15 条匹配：7 个 Claude 专属后缀、3 个品牌专属第三方主机、claude/anthropic 两个关键词及 3 条旧网络规则。AI 现为 140 条；共享的 auth0.com、intercom.io、sentry.io、datadog 关键词等继续留在 AI，不能为了 Claude 把其他 AI 服务的依赖删掉。

Claude 专属清单放在 AI 前面才能优先匹配 anthropic.auth0.com 等共享父域下的专属主机。用户无法仅按共享主机名区分每个 App 的请求，因此可选共享清单的作用范围不限 Claude。它不自动启用，也不包含 datadog/sentry/sift 等更宽泛关键词。

官方当前 API 入站范围为 160.79.104.0/23、153.61.224.0/22、2607:6bc0::/48。旧 AI 中的 160.79.104.0/21 属于官方出站范围，不能当作 API 入站段；旧 IPv6 /32 也未沿用。保留此前 AS399358 的网络兜底，其匹配范围由 Surge 的 ASN 数据库决定，可能比上述入站段更宽。

Claude Code 的 downloads.claude.ai、platform.claude.com、sso.claude.com、bridge.claudeusercontent.com 等由对应父域覆盖，无需重复逐条列出。历史品牌 CDN/身份验证主机保留为精确 DOMAIN。新增加 claude.dev 来源于社区清单；不是所有域名都经过逐项所有权认证。

## 自动更新与审计

每日台北时间 06:23 与 Meta、AI 在同一工作流中串行更新。先生成 Claude，再生成排除 Meta/Claude 的 AI 清单。

- 5 份来源全部成功下载、解析和隐私检查后才生成 Claude 输出，任一步失败则工作流不推送。
- 核心边界来自 config/claude.json；既有品牌域的子域可自动合并，未知根域或第三方新主机进入 pending 等待所有权复核。
- v2fly 和 MetaCubeX 共用来源家族，不能把两者重复收录当作独立确认。
- 共享清单固定经过审核的依赖，不自动把社区关键词、平台根域、网络段纳入核心。
- Claude 官方网络文档用于人工审核，不自动解析网页中的全部主机；尤其不把插件、WebFetch、MCP 自定义服务的任意外部地址都归入 Claude。
- AI 构建过滤 Claude 域名、相关关键词/可识别 URL 正则、AS399358、旧网络范围及已识别的候选根域，防止上游重新带回。复杂正则和共享云 IP 不保证绝对流量隔离。
- sources/claude 保存上游原文及报告中的哈希。候选如 chatbotclaude.com、claude.site、claudestudio.com 等没有直接加入核心；源文件中的条目不是自动启用规则。

## 来源

官方：
- [Claude Code 网络要求](https://code.claude.com/docs/en/network-config#network-access-requirements)
- [Anthropic 入站/出站 IP](https://platform.claude.com/docs/en/api/ip-addresses)

社区：
- [v2fly anthropic](https://github.com/v2fly/domain-list-community/blob/master/data/anthropic)
- [MetaCubeX anthropic](https://github.com/MetaCubeX/meta-rules-dat/blob/meta/geo/geosite/classical/anthropic.list)
- [blackmatrix7 Claude](https://github.com/blackmatrix7/ios_rule_script/blob/master/rule/Surge/Claude/Claude.list)
- [erwanjun Claude](https://github.com/erwanjun/surge-claude-rules/blob/main/Surge/Claude.list)
- [ma-wenqian Claude](https://github.com/ma-wenqian/ai-proxy-rules/blob/main/rules/claude.list)

社区资料保留原有注释与来源，遵循各自许可。本仓库做了拆分、筛选、去重及 IP 方向修正，不承诺“全部规则”或任意第三方 Claude 托管入口的完整覆盖。Bedrock、Vertex/Google Cloud、Foundry、自建 API 网关还需要按实际入口配置。语法及自动化测试不等于所有 App 功能已经实测。
