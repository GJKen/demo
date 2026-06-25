# 订阅转换.html — OpenClash 订阅附加规则器

## 这是什么

一个**纯前端单文件工具**(`订阅转换.html`),把机场订阅转换成带完整附加规则的 Clash/Mihomo 配置。
**无后端、无构建步骤、无依赖管理**——所有代码(HTML/CSS/JS)都在这一个文件里,双击即用。

外部依赖仅两个 CDN:
- `highlight.js` 11.11.1 — YAML 语法高亮
- Google Fonts(Noto Sans SC / IBM Plex Mono)

## 文件结构(单文件内的分区)

| 行号(约) | 区块 | 说明 |
|---|---|---|
| 10–211 | `<style>` | GitHub 深色风主题、滚动容器、textarea resize handle、modal、分组拖拽态(`.dragging`/`.drag-over`/`.drag-handle`)。顶栏/代码区用**分组选择器**共享 base(见「关键约定」CSS 一节) |
| 214–309 | HTML 骨架 | 三栏布局 + 多行订阅链接/多框手动粘贴 + 统一「🔄 获取全部并生成配置」按钮 + 全屏弹层 + 节点列表 modal |
| 312–500 | 硬编码常量 | `FIXED_HEADER`(端口/DNS)、`RULE_PROVIDERS`(规则集)、`RULES`(分流规则) |
| 504–562 | 配置数据 | `DEFAULT_GROUPS`(代理组定义,含国家组 + `🌐其他` 兜底组)、`COUNTRY_RULES`(国家分类关键词)、`INFO_NODE_RE`+`isInfoNode()`(信息节点判定,**全局唯一来源**)、`STRIP_EMOJI` |
| 567–592 | 排序持久化 | `loadGroupOrder()` / `saveGroupOrder()`,分组顺序存 `localStorage` |
| 595–654 | 分类逻辑 | `refreshActiveCountryGroups()`、`getNodeCountry()`(token/大小写匹配)、`classifyNodes()`(产出 `countryMap` + `others`) |
| 658–696 | `generateConfig()` | **核心**:拼接最终 YAML(按 `DEFAULT_GROUPS` 顺序输出 proxy-groups) |
| 744–798 | `renderGroupConfig()` | 渲染左侧分组面板,卡片 `draggable` |
| 845–1238 | 解析器 | Clash YAML 块/单行节点、`parseVlessUri`、`parseHysteria2Uri`、`nodeToYamlLine`、base64、`getProxyEndpoint` |
| 1224–1305 | 多源编排 | `getProxyContentKey`(整块去重键)、`isInfoNode`、`mergeNodes()`(整块去重 + 丢信息节点)、`parseAnyContent()`、`mergeSource()` |
| 1307–1399 | 抓取与重建 | `fetchUrlBody()`(CORS 轮询)、`fetchAll()`(重建池) |
| 1400–1520 | 交互逻辑 | 事件绑定、追加/删除行、复制/下载/清空、全屏、节点弹窗、`setupGroupDrag()` 拖拽委托 |

## 核心数据流

```
[🔄 获取全部并生成配置] → fetchAll() 重建节点池
   ├─ 收集所有 .url-input 行 + 所有 .manual-input 框(各自可多行/多框)
   ├─ 清空 parsedProxies[] / parsedNodeNames[] / activeCountryGroups
   ├─ 每个 URL 行 → fetchUrlBody()(CORS 代理轮询) → 正文
   └─ 每个来源正文 → mergeSource() → mergeNodes() 整块去重 + 丢信息节点 合并进池
        ↓ 单来源解析: parseAnyContent() 探测格式
            ├─ base64? → atob 解码
            ├─ vless://、hysteria2:// → parseUriLinks()
            └─ Clash YAML → parseSubscription()
        ↓
parsedProxies[] + parsedNodeNames[]  (两个全局数组, 已不含信息节点)
        ↓
refreshActiveCountryGroups() 按 COUNTRY_RULES 关键词归类到国家组
        ↓
generateConfig() = FIXED_HEADER + proxies + proxy-groups + RULE_PROVIDERS + RULES
        ↓
updateOutput() 脏检查 + 离屏 hljs 高亮 → 写入 DOM
```

## 当前能力

- 支持 Clash `proxies:` 下的两种节点写法:
  - 单行 map: `- { name: ..., type: ..., server: ... }`
  - 分块 YAML: `- name: ...` 后续多行字段
- 支持 `name: "\U0001F1FA\U0001F1F8美国..."` 这类 YAML 双引号 Unicode 转义,会还原成真实国旗/中文用于分组。
- URI 输入支持 `hysteria2://` 和 `vless://`,最终节点池统一输出为分块 YAML,不再输出旧的单行 `{ ... }` 节点。URI 解析对齐 Mihomo 字段要求:
  - **vless ws 的 `path` 会 URL 解码**(`%2Fdjjc%2Fus1` → `/djjc/us1`),否则 Clash 握手必失败。
  - **vless+tls/reality 的 TLS 域名统一用 `servername`**(不是 `sni`);`fp` 在 reality 和普通 tls 下都输出为 `client-fingerprint`;`packetEncoding` → `packet-encoding`。
  - **hysteria2 端口跳跃只输出 `ports`**(`mport` 是非标准字段,不输出);`insecure=1/true` 或带 `pinSHA256` 时 `skip-cert-verify: true`(机场普遍伪造 SNI + 自签证书,Mihomo 无法像客户端那样 pin,跳过校验以匹配机场自己的 sing-box `insecure=1` 行为)。
- 国家自动组按需输出,当前包含香港、台湾、新加坡、日本、美国、欧洲、韩国、印度、加拿大、巴西、阿联酋、南非、墨西哥。
- **多源输入**:订阅链接和手动粘贴都支持「➕ 追加」多行/多框;点「🔄 获取全部并生成配置」时 `fetchAll()` 会**重建**节点池(清空后把所有来源依次合并),而不是在旧池上累加。
- **去重 + 信息节点过滤**:`mergeNodes()` 用 `getProxyContentKey()`(**整个 YAML 块忽略 name 行**)做去重键——同一机场大量节点共用 `server:port`(CDN 中转 / 端口跳跃),只按 `server:port` 去重会误杀真·不同节点,故改用整块比对,只有连接参数完全一致(仅名字不同)的才算重复;重名加 `(2)` 后缀。机场塞进订阅的「信息节点」(剩余流量 / 套餐到期 / 重置时间等)由 `isInfoNode()` 在合并阶段直接丢弃。
- **国家匹配**:`getNodeCountry()` 对中文/国旗 emoji/完整英文名做**大小写不敏感**子串匹配;对 2~3 字母国家/机场代码(`KR`/`US`/`LAX`…)按 `nameTokens()` 切出的**整 token** 比对,既能命中 `kr-ld` 这类小写命名,又不会让 `Singapore` 里的 `in` 误判成印度。
- **🌐其他兜底组**:`classifyNodes()` 把没匹配到任何国家的 `normal` 节点收进 `others`,生成一个 `isOther` 的 `🌐其他 Auto` 组(仅当有未归类节点时输出),保证任何节点都不会从分组里凭空消失。
- **应用分流组含手动选择**:AIGC/PikPak/PicHub/Telegram/Google/漏网之鱼 的 proxies 第一项是 `🚀手动选择`(`getSelectableGroups()` 只返回 url-test 组,所以 select 型的手动选择要在 `generateConfig` 里单独前置)。ADblock/Adobe 是固定 `REJECT/DIRECT`,不含手动选择。
- **分组可拖拽排序**:分组卡片 `draggable`,拖放后重排 `DEFAULT_GROUPS` 数组(输出顺序即数组顺序)并 `updateOutput()`;顺序存 `localStorage`(`GROUP_ORDER_KEY`),`loadGroupOrder()` 在启动时还原、新增组按原位补到末尾。proxy-groups 顺序在 Clash 里只影响客户端显示、不影响分流。
- 输出代码区和全屏代码区都需要保留 `overflow:auto; min-height:0`,否则 flex 布局下鼠标滚轮可能无法滚动。
- 节点列表 modal 支持关闭按钮、Esc、点击外部遮罩关闭;点击弹窗内容区不会误关。

## 关键约定 / 设计

- **YAML 仍然主要是字符串拼接生成的,不是完整序列化器**。已有 `formatYamlScalar()` / `parseYamlScalar()` 只覆盖当前节点名、URI 输出和常见标量场景,不是通用 YAML parser。
- **读入节点时尽量保留原始字段结构**:分块 YAML 会经 `normalizeProxyBlock()` 统一缩进后进入 `parsedProxies[]`;单行 map 会经 `blockMapToYaml()` 转成分块输出。
- **代理组名带 emoji 前缀**(如 `🚀手动选择`),`STRIP_EMOJI` 正则用于 UI 显示时剥离,但配置里保留完整名。
- **信息节点判定只有一个来源**:`INFO_NODE_RE` + `isInfoNode()`。`mergeNodes()` 丢弃、`classifyNodes()` / `renderNodeList()` 复用同一个判定;新增关键词只改这一处(不要再引入第二份关键词数组)。
- **去重键 = 整块配置(忽略 name)**:`getProxyContentKey()` 把节点 YAML 块去掉 name 行后整体比对。改去重逻辑时注意:`server:port` 粒度太粗会误杀 CDN/端口跳跃节点。
- **CSS 复用基类用分组选择器,不用 `composes`**:纯 CSS(无构建)**不支持 `composes`**(那是 CSS Modules 语法,浏览器会静默忽略)。顶栏 `.bar-header,.panel-header,.fs-header` 和代码区 `.output-code,.fs-code` 都用分组选择器共享 base、再各自覆盖差异。`.bar-header`/`.code-pane` 这类「只定义不挂到 HTML」的基类是无效的。
- **国家组按需输出**:`COUNTRY_RULES` 用国旗 emoji + 中文 + IATA/英文地名匹配节点;无匹配节点的国家组不会出现在最终配置里。没匹配到任何国家的 `normal` 节点进 `🌐其他 Auto`(`isOther`)兜底组。
- **CORS 代理轮询**:`fetchUrlBody()` 依次尝试 5 个公共代理(gjken→allorigins→corsproxy→codetabs→cors-anywhere),各 15s 超时降级;返回正文文本,全失败返回 `null`。`fetchAll()` 逐个 URL 调用它。
- **状态全局变量**:`parsedNodeNames` / `parsedProxies` / `selectedGroups` / `activeCountryGroups` / `_lastRenderedConfig`(高亮缓存,清空时要置 null)。分组顺序持久化在 `localStorage` 的 `GROUP_ORDER_KEY`,启动时由 `loadGroupOrder()` 还原。

## 已知坑(改之前先看)

1. **不是完整 YAML 解析器**:复杂锚点、跨行字符串、数组对象混排等高级 YAML 语法仍可能解析不完整。
2. **特殊字符 YAML 注入**:节点名/密码含极端字符时,字符串拼接仍可能生成非法 YAML。彻底修复需改用真正的 YAML 序列化。
3. **隐私**:订阅链接(含 token)会发给第三方 CORS 代理。
4. **hysteria2 默认 `skip-cert-verify: true`**:为匹配机场 sing-box(`insecure=1`)行为保证能连,牺牲了证书校验。机场用伪造 SNI(www.bing.com 等)+ 自签证书时这是常态,但若将来接入正经证书的服务端要留意。
5. **vless 字段名**:`ws-opts`/`reality-opts` 仍是手拼对象。已统一 `servername`(TLS SNI)、`client-fingerprint`、`packet-encoding`、ws `path` 解码;若再加字段注意下划线 vs 连字符。
6. `RULE_PROVIDERS` 各条目的 `url` 行末尾不要带逗号。它是字符串模板,逗号会原样进入最终 URL 导致规则集下载失败。

## 修改须知

- **改样式优先复用 CSS 变量 + 分组选择器**(`--chip-*`、`--btn-*`、`--bg*`、`--border*`)。复用一组规则时用分组选择器(`.a,.b{...}`),**不要用 `composes`**(纯 CSS 无效),也不要定义一个不挂到 HTML 的「基类」。
- 改输出区域时注意 `.output-code` / `.fs-code` 的滚动规则,尤其是 `min-height:0`;两者的字体/内边距 base 现在由分组选择器共享。
- 加新协议解析:仿照 `parseVlessUri` / `parseHysteria2Uri`,在 `parseAnyContent` 里加分支,并在 `nodeToYamlLine` 加字段输出;字段名对齐 Mihomo 文档(wiki.metacubex.one)。
- 加新国家/地区:同时改 `DEFAULT_GROUPS`、`COUNTRY_RULES`、`STRIP_EMOJI`,保持名字一致。
- 改信息节点判定:只改 `INFO_NODE_RE`(全局唯一来源),`mergeNodes` / `classifyNodes` / `renderNodeList` 自动跟随。
- 加新规则集/代理组:同时改 `RULE_PROVIDERS`、`RULES`、`DEFAULT_GROUPS` 三处,保持名字一致。
- 没有测试 / 没有 lint,改完直接浏览器打开验证;浏览器若限制 `file://`,至少用脚本级样例验证 `parseAnyContent()` / `mergeSource()` 和 `generateConfig()`(可用 Node 抽取函数体跑真实订阅样例)。
