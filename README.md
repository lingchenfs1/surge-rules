# Surge Rules

个人 Surge 分流规则仓库，按服务分类维护。

## 当前规则

| 规则 | 内容 | 条数 | 更新方式 |
| --- | --- | ---: | --- |
| [Meta](rules/Meta.list) | Facebook、Instagram、Threads、WhatsApp、Messenger、Meta AI/Muse、Quest/Oculus，以及相关品牌、开发者和历史兼容域名 | 见[同步报告](docs/meta-sync.json) | 自动检查 |
| [Claude](rules/Claude.list) | Claude/Anthropic 专属服务；[共享依赖](rules/Claude-Shared.list)单独可选 | 见[同步报告](docs/claude-sync.json) | 自动检查 |
| [AI](rules/AI.list) | OpenAI、Gemini、GitHub Copilot、Cursor、Kiro、Windsurf、Apple Intelligence 等；排除 Meta 和 Claude 专属条目 | 见[同步报告](docs/ai-build.json) | 自动检查 |

## 在 Surge 中使用

在已有配置的 `[Rule]` 段添加以下规则，将 `META`、`CLAUDE` 和 `AI` 分别替换为已有策略组或节点名称：

```ini
RULE-SET,https://raw.githubusercontent.com/lingchenfs1/surge-rules/main/rules/Meta.list,META,extended-matching
RULE-SET,https://raw.githubusercontent.com/lingchenfs1/surge-rules/main/rules/Claude.list,CLAUDE,extended-matching
RULE-SET,https://raw.githubusercontent.com/lingchenfs1/surge-rules/main/rules/AI.list,AI
```

放在希望被其覆盖的整机分流规则以及 `FINAL` 之前。是否优先于广告拦截规则，请按自己的需求决定。这些规则适用于所有设备，不限定 MAC 地址。

- [Meta Raw 订阅地址](https://raw.githubusercontent.com/lingchenfs1/surge-rules/main/rules/Meta.list)
- [Claude Raw 订阅地址](https://raw.githubusercontent.com/lingchenfs1/surge-rules/main/rules/Claude.list)；[使用与拆分说明](docs/Claude.md)。Claude 应在 AI 前匹配，避免共享父域抢先命中。
- [AI Raw 订阅地址](https://raw.githubusercontent.com/lingchenfs1/surge-rules/main/rules/AI.list)
- 直接粘贴版：[Meta](snippets/Meta.txt)、[Claude](snippets/Claude.txt)、[AI](snippets/AI.txt)。与对应规则集二选一，不必重复添加；同样需要替换策略名称。
- 来源与覆盖说明：[Meta](docs/Meta.md)、[Claude](docs/Claude.md)、[AI](docs/AI.md)。
- [可选 macOS 进程规则](snippets/AI-processes.txt)：仅保留 Alma；[Claude Desktop 进程规则](snippets/Claude-processes.txt)已独立。进程规则均单独配置，不包含在订阅内。

`rules/*.list` 不绑定策略；引用时在 `RULE-SET` 外层指定策略。Meta 和 Claude 外层使用 `extended-matching`。AI 保留原有逐条匹配选项，Apple Intelligence 的扩展匹配已写入对应条目，不必给整个 AI 规则集额外添加该参数。IP-ASN 条目保留 `no-resolve`。

第一批编程助手补充已加入：Cursor 的 API/CDN/云端主机、GitHub Copilot 服务域、Kiro 核心域与两个精确 AWS 服务主机、Windsurf/Codeium 域名。详见 [新增条目和覆盖边界](docs/AI.md#第一批编程助手补充)。

## 自动更新

每天台北时间 **06:23** 在 GitHub 依次检查 Meta、Claude 和 AI 上游，自动补充符合条件的缺项、去重并提交；支持手动触发。详见 [自动更新规则与失败处理](docs/Automation.md)，最新来源哈希及待复核项见 [Meta 报告](docs/meta-sync.json)、[Claude 报告](docs/claude-sync.json)和 [AI 报告](docs/ai-build.json)。AI 每次更新都会排除 Meta 和 Claude 专属条目；源快照保留上游原文用于审计。

## 维护约定

1. 新服务使用 `rules/服务名.list`，保持已有订阅路径稳定。
2. 更新时核对来源、去除重复项和父域已覆盖的子域规则，同步更新 README 中的规则目录、订阅示例、更新方式和使用限制，以及相关说明和变更记录。
3. 避免无依据加入关键词、共享云平台根域或旧 IP 大网段。
4. 不存放节点凭据、完整个人配置、设备标识或请求日志。
5. 提交前做 Surge 离线语法检查；语法通过不代表所有业务功能均验证成功。

## 完整性

规则由社区资料交叉整理，并按明确筛选条件定期增量更新。多个项目可能使用相同上游，重复收录不等于独立验证。开发者、品牌和历史兼容域名没有逐一完成当前所有权或存活验证；第三方托管、点对点通话及未来新增服务可能无法全部覆盖。

数据来源保留在各服务说明中；引用的上游材料遵循各自许可，本仓库不将其重新声明为独占原创。
