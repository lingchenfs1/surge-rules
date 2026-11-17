# AI 规则整理

日期：2026-11-17。依据当前运行配置中明确指向 AI 策略组的 21 条入口规则整理；其中有 9 条远程 RULE-SET、最初 2 条本机进程规则、10 条其他规则（含 1 条 OR）。只整理并发布仓库文件，没有修改本机配置。

## 交付

- `rules/AI.list`：不带策略的目标规则，当前条数见 `docs/ai-build.json`（接入自动更新并排除 Meta 后首次为 147 条）。
- `snippets/AI.txt`：同一内容，带 AI 策略占位，可粘贴到 [Rule]。
- `snippets/AI-processes.txt`：目前仅保留 Alma；Claude Desktop 已迁移到 Claude-processes.txt，独立存放；不包含用户名或设备身份。
- `sources/ai/`：当前 10 份订阅上游快照（旧 Claude 04.list 仅作历史审计）（保留作者和许可注释）、脱敏的手工目标规则以及 URL/哈希清单。
- `docs/ai-build.json`：逐条来源、数量及被父后缀覆盖的条目记录。
- `scripts/build_ai.py`：从已保存快照和上次发布结果增量重建、去重并排除 Meta；`scripts/update_ai.py` 抓取上游后在临时目录验证，通过后更新发布文件。均不访问本机 Surge。

远程条目来自整理时在线取得的最新清单，不保证与 Surge 本地缓存逐字一致；上游可能变动。现已加入每日定时工作流，与 Meta 串行更新，避免并发提交冲突。

## 合并方式

初次导出时展开 9 份远程清单以及手工 OR 中的条件，共 294 条目标规则。去除 132 条精确重复及 14 条被相同选项的父后缀覆盖的域名，保留 148 条。两个 OpenAI 清单内容相同，合并为一份。

保留原有非 Meta 的宽泛关键词、IP/ASN、URL-REGEX 和第三方域名；新增规则受自动更新限制。没有用关键词规则去删除精确域名，以便后续审查；只对选项相同的父子域进行覆盖去重。Apple Intelligence 外层原有的 extended-matching 转移到对应的域名条目；其他条目未统一扩大 SNI 匹配范围。

## 使用

在 [Rule] 中按所需优先级引用：

```ini
RULE-SET,https://raw.githubusercontent.com/lingchenfs1/surge-rules/main/rules/AI.list,AI
```

AI 必须是已有策略组。为保留导出的匹配选项，此处不额外添加外层 extended-matching；Apple Intelligence 条目已单独带该选项。

合并为一条 RULE-SET 会改变这些规则与其他组之间的交错顺序，不能自动保持原配置的所有优先级。发布的 AI.list 已排除 meta.ai 及 Meta.list 中的域名/ASN；独立 Meta.list 仍可按需要使用。源快照会保留上游原文中的 Meta 条目作为审计证据，它们不是被订阅的 AI 规则。

原有的分散 AI 规则若继续位于前面，仍可能先命中；本仓库未替用户删除或移动任何配置。可选进程规则会将对应 App 的全部流量匹配到 AI，应单独决定其顺序。

## 当前匹配范围提醒

这是现有配置的整理，不是 AI 官方域名白名单。现有规则包括：

- sora、colab、developerprofiles、sift、sentry、datadog、claude、anthropic、openai 等关键词，可能命中其他业务。
- auth0.com、stripe.com、segment.io、intercom.io、apis.google.com 等共享服务。
- AS14061、AS20473 等上游原有 ASN 匹配，范围不局限于某个 AI 产品；这里只保留原规则，未重新核实其必要性。
- URL-REGEX 匹配依赖 Surge 可见的 URL；HTTPS 内容不可见时不能假定一定命中。未开启 MITM。
- 发布结果排除与 Meta 域名相关的精确/后缀规则、可识别的 Meta 关键词和 URL 正则，以及相同 Meta ASN。通用云平台 IP 或任意复杂正则不能据此保证与 Meta 流量绝对隔离。

## 来源与许可

上游原文保留于 sources/ai，相关内容遵循各自上游许可；这次对规则做了展开、合并和去重，不声明为独占原创。

- [00](https://ruleset.skk.moe/List/non_ip/ai.conf)：59 条。
- [01](https://ruleset.skk.moe/List/non_ip/apple_intelligence.conf)：6 条。
- [02](https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Surge/OpenAI/OpenAI.list)：35 条。
- [03](https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/refs/heads/master/rule/Clash/OpenAI/OpenAI.list)：35 条。
- [04](https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/refs/heads/master/rule/Clash/Claude/Claude.list)：3 条。
- [05](https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/refs/heads/master/rule/Clash/BardAI/BardAI.list)：10 条。
- [06](https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/refs/heads/master/rule/Clash/Gemini/Gemini.list)：13 条。
- [07](https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Clash/Copilot/Copilot.list)：51 条。
- [08](https://raw.githubusercontent.com/ACL4SSR/ACL4SSR/master/Clash/Ruleset/AI.list)：49 条。

Sukka 原文声明 AGPL-3.0，blackmatrix7 仓库提供 GPL-2.0；上游许可全文见 sources/ai/licenses/。ACL4SSR 来源及其仓库声明见对应上游，未替上游重新授权。

## 验证

生成结果通过本地 Surge 6.10.0 离线语法检查；重建与去重覆盖检查通过。未验证所有 AI 服务端到端可用性。

## 每日自动更新

每天台北时间 06:23，先同步 Meta，再检查这里配置的 10 份 AI 上游。新域名从已指定清单补充；已有非 Meta 规则保留，不因上游删除而自动删减。DOMAIN 和 DOMAIN-SUFFIX 自动补充并去重；新关键词、IP、ASN、URL-REGEX 进入报告 pending，不自动扩大匹配范围。共享平台根域的新增也需复核。单次超过 25 条新增、任何来源失败/格式异常/隐私检查失败，整个工作流不提交。

Meta 排除在每次构建最后执行，包含 config/ai-update.json 的固定根域和当次 Meta.list；上游再次出现 meta.ai 时也不会恢复到 AI.list。原有进程规则是独立的可选文件，仍可能匹配 App 的全部流量，不由本更新器加载或修改。

AI 的来源选择沿用当前配置，不要求像 Meta 更新器一样有两个来源家族支持；不代表域名官方归属已经核实。首次改动为移除一条 DOMAIN-SUFFIX,meta.ai，其余发布匹配范围保留。后续源原文、SHA256、待复核条目均可在仓库审计。

## 第一批编程助手补充

2026-11-17 按用户选择新增 12 条匹配项，并去掉 4 条由新父后缀覆盖的旧精确主机，发布规则由 147 条变为 155 条。新增没有扩大到整个 AWS、GitHub 或 Azure 域名。

| 服务 | 新增匹配目标 | 方式 |
| --- | --- | --- |
| Cursor | cursorapi.com、cursor-cdn.com、cursorvm.com | DOMAIN-SUFFIX |
| GitHub Copilot | githubcopilot.com | DOMAIN-SUFFIX |
| GitHub Copilot | origin-tracker.githubusercontent.com | DOMAIN |
| Kiro | kiro.dev | DOMAIN-SUFFIX |
| Kiro | q.us-east-1.amazonaws.com、q.eu-central-1.amazonaws.com | DOMAIN |
| Windsurf | windsurf.com、windsurf.build、codeium.com、codeiumdata.com | DOMAIN-SUFFIX |

Cursor 和 Windsurf 已接入两个专项远程清单，每日一同检查：

- [Cursor 清单](https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/meta/geo/geosite/classical/cursor.list)
- [Windsurf 清单](https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/meta/geo/geosite/classical/windsurf.list)

Copilot 与 Kiro 的五条补充作为有来源的固定规则存入 manual.list，每次重建保留；不会自动解析官网 HTML。

核对来源：[Cursor 官方网络配置](https://cursor.com/docs/enterprise/network-configuration)、[GitHub Copilot 官方允许列表](https://docs.github.com/en/copilot/reference/copilot-allowlist-reference)、[Kiro 官方防火墙文档](https://kiro.dev/docs/privacy-and-security/firewalls/)。Windsurf 域名来自上面的社区专项清单。

去重删除的旧条目为 api.githubcopilot.com、server.codeium.com、inference.codeium.com、server.self-serve.windsurf.com，均仍由新后缀覆盖。

范围仅限已选第一批条目，并非上述产品全部网络依赖。Kiro 的第三方登录/组织 SSO、Cursor 的额外对象存储和登录主机、Copilot 云会话等可能还依赖其他地址；当前未对全部产品进行端到端测试。Meta 排除逻辑和现有隐私检查继续生效。

## Claude 独立拆分

2026-11-17 Claude 已独立为 [Claude.list](../rules/Claude.list)，AI 清单移除 15 条 Claude 专属域名/关键词/网络规则，当前为 140 条。自动更新同时排除 Meta 和 Claude；Claude 专项上游已从 AI manifest 移除，AI 当前10源。旧源快照中出现 Claude 仅供审计，不会直接进入发布结果。共享服务继续保留，使用时把 Claude.list 放在 AI.list 前；可选共享依赖和边界见 [Claude说明](Claude.md)。本文早前148/147/155数量为历史阶段记录，当前数量以同步报告为准。
