# Surge Rules

个人 Surge 分流规则仓库，按服务分类维护。

## 当前规则

| 规则 | 内容 | 条数 | 数据整理日期 |
| --- | --- | ---: | --- |
| [Meta](rules/Meta.list) | Facebook、Instagram、Threads、WhatsApp、Messenger、Meta AI/Muse、Quest/Oculus，以及相关品牌、开发者和历史兼容域名 | 见[同步报告](docs/meta-sync.json) | 自动检查 |

## 在 Surge 中使用

在已有配置的 `[Rule]` 段添加以下规则，将 `META` 替换为已有策略组或节点名称：

```ini
RULE-SET,https://raw.githubusercontent.com/lingchenfs1/surge-rules/main/rules/Meta.list,META,extended-matching
```

放在希望被其覆盖的整机分流规则以及 `FINAL` 之前。是否优先于广告拦截规则，请按自己的需求决定。这条规则适用于所有设备，不限定 MAC 地址。

- [Meta Raw 订阅地址](https://raw.githubusercontent.com/lingchenfs1/surge-rules/main/rules/Meta.list)
- [直接粘贴版](snippets/Meta.txt)：与规则集二选一，不必重复添加；同样需要替换 `META`。
- [来源与覆盖说明](docs/Meta.md)

`rules/*.list` 不绑定策略；引用时在 `RULE-SET` 外层指定策略。`extended-matching` 用于扩展域名匹配；IP-ASN 条目保留 `no-resolve`。

## 自动更新

每天台北时间 **06:23** 在 GitHub 检查上游，自动补充符合条件的缺项、去重并提交；支持手动触发。详见 [自动更新规则与失败处理](docs/Automation.md)，最新来源哈希及待复核项见 [同步报告](docs/meta-sync.json)。

## 维护约定

1. 新服务使用 `rules/服务名.list`，保持已有订阅路径稳定。
2. 更新时核对来源、去除重复项和父域已覆盖的子域规则，并更新说明和变更记录。
3. 避免无依据加入关键词、共享云平台根域或旧 IP 大网段。
4. 不存放节点凭据、完整个人配置、设备标识或请求日志。
5. 提交前做 Surge 离线语法检查；语法通过不代表所有业务功能均验证成功。

## 完整性

规则由社区资料交叉整理，并按明确筛选条件定期增量更新。多个项目可能使用相同上游，重复收录不等于独立验证。开发者、品牌和历史兼容域名没有逐一完成当前所有权或存活验证；第三方托管、点对点通话及未来新增服务可能无法全部覆盖。

数据来源保留在各服务说明中；引用的上游材料遵循各自许可，本仓库不将其重新声明为独占原创。
