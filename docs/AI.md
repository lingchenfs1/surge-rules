# AI 规则整理

日期：2026-11-17。依据当前运行配置中明确指向 AI 策略组的 21 条入口规则整理；其中有 9 条远程 RULE-SET、2 条本机进程规则、10 条其他规则（含 1 条 OR）。只整理并发布仓库文件，没有修改本机配置。

## 交付

- `rules/AI.list`：148 条不带策略的目标规则。
- `snippets/AI.txt`：同一内容，带 AI 策略占位，可粘贴到 [Rule]。
- `snippets/AI-processes.txt`：2 条可选 macOS 进程规则，独立存放；不包含用户名或设备身份。
- `sources/ai/`：9 份公开上游原文快照（保留作者和许可注释）、脱敏的手工目标规则以及 URL/哈希清单。
- `docs/ai-build.json`：逐条来源、数量及被父后缀覆盖的条目记录。
- `scripts/build_ai.py`：从已保存快照确定性重建，不访问本机 Surge 或网络。

远程条目来自整理时在线取得的最新清单，不保证与 Surge 本地缓存逐字一致；上游可能变动。此版本是快照，不加入 Meta 定时同步工作流。

## 合并方式

展开 9 份远程清单以及手工 OR 中的条件，共 294 条目标规则。去除 132 条精确重复及 14 条被相同选项的父后缀覆盖的域名，保留 148 条。两个 OpenAI 清单内容相同，合并为一份。

保留原有宽泛关键词、IP/ASN、URL-REGEX 和第三方域名。没有用关键词规则去删除精确域名，以便后续审查；只对选项相同的父子域进行覆盖去重。Apple Intelligence 外层原有的 extended-matching 转移到对应的域名条目；其他条目未统一扩大 SNI 匹配范围。

## 使用

在 [Rule] 中按所需优先级引用：

```ini
RULE-SET,https://raw.githubusercontent.com/lingchenfs1/surge-rules/main/rules/AI.list,AI
```

AI 必须是已有策略组。为保留导出的匹配选项，此处不额外添加外层 extended-matching；Apple Intelligence 条目已单独带该选项。

合并为一条 RULE-SET 会改变这些规则与其他组之间的交错顺序，不能自动保持原配置的所有优先级。若希望 Meta 始终走 Meta 组，请将 Meta.list 引用放在 AI.list 之前；本文件保留了原有 meta.ai。

原有的分散 AI 规则若继续位于前面，仍可能先命中；本仓库未替用户删除或移动任何配置。可选进程规则会将对应 App 的全部流量匹配到 AI，应单独决定其顺序。

## 当前匹配范围提醒

这是现有配置的整理，不是 AI 官方域名白名单。现有规则包括：

- sora、colab、developerprofiles、sift、sentry、datadog、claude、anthropic、openai 等关键词，可能命中其他业务。
- auth0.com、stripe.com、segment.io、intercom.io、apis.google.com 等共享服务。
- AS14061、AS20473 等上游原有 ASN 匹配，范围不局限于某个 AI 产品；这里只保留原规则，未重新核实其必要性。
- URL-REGEX 匹配依赖 Surge 可见的 URL；HTTPS 内容不可见时不能假定一定命中。未开启 MITM。
- meta.ai 同时被 Meta 规则覆盖，先匹配者决定出口。

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
