# Meta 规则说明

整理日期：2026-11-16；发布日期：2026-11-17。

## 组成

117 条规则：113 条 DOMAIN-SUFFIX、1 条精确 DOMAIN、3 条 IP-ASN。相比最初 51 条版本新增 66 条，包含 Instagram 短链、品牌与开发者域名、历史兼容域名及两个 ASN。

Meta AI/Muse 的 hatch-api.meta.ai、hatch.metaaivm.com 分别由 meta.ai、metaaivm.com 覆盖。RaybanMeta 清单的 5 个后缀全部覆盖。没有将眼镜品牌商的整个站点直接视为 Meta App 的依赖。

AS11917、AS32934、AS63293 来自 [Meta 的 PeeringDB 组织登记](https://www.peeringdb.com/org/9660)。匹配依赖 Surge 本地 ASN 数据库，不能覆盖所有第三方托管网络。

## 交叉整理方法

读取 5 个项目的 15 份清单，得到 618 个精确去重候选。筛选后保留本文件的 117 条，按类型与目标去重，避免重复添加父后缀已经覆盖的子域。

没有直接合并所有候选：未核实的拼写变体、营销及其他历史域名、旧静态 IP、宽泛关键词，以及 bintray.com 等共享基础设施均未纳入。保留的品牌、开发者与历史兼容条目仍属于社区归类，不应理解为逐条获得官方确认。

数据发布后没有自动追踪上游；后续按需求更新。规则与上游之间不是同步镜像。

## 来源

- [metacubex-meta](https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/meta/geo/geosite/classical/meta.list)
- [g94-rayban](https://raw.githubusercontent.com/G94Cloud/CustomRules/main/RaybanMeta.list)
- [lm-facebook](https://raw.githubusercontent.com/LM-Firefly/Rules/master/PROXY/Facebook.list)
- [blackmatrix7-Facebook](https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Surge/Facebook/Facebook.list)
- [blackmatrix7-Instagram](https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Surge/Instagram/Instagram.list)
- [blackmatrix7-Threads](https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Surge/Threads/Threads.list)
- [blackmatrix7-Whatsapp](https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Surge/Whatsapp/Whatsapp.list)
- [v2fly-meta](https://raw.githubusercontent.com/v2fly/domain-list-community/master/data/meta)
- [v2fly-facebook](https://raw.githubusercontent.com/v2fly/domain-list-community/master/data/facebook)
- [v2fly-facebook-dev](https://raw.githubusercontent.com/v2fly/domain-list-community/master/data/facebook-dev)
- [v2fly-instagram](https://raw.githubusercontent.com/v2fly/domain-list-community/master/data/instagram)
- [v2fly-messenger](https://raw.githubusercontent.com/v2fly/domain-list-community/master/data/messenger)
- [v2fly-oculus](https://raw.githubusercontent.com/v2fly/domain-list-community/master/data/oculus)
- [v2fly-threads](https://raw.githubusercontent.com/v2fly/domain-list-community/master/data/threads)
- [v2fly-whatsapp](https://raw.githubusercontent.com/v2fly/domain-list-community/master/data/whatsapp)

## 验证

本地 Surge 6.10.0 离线语法检查通过；确认条数及无重复，粘贴版与规则集条目一致。未执行 App 全功能验证。
