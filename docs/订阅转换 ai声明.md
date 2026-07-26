# 订阅转换.html — OpenClash 订阅附加规则器

## 这是什么

一个**纯前端单文件工具**(`订阅转换.html`),把机场订阅转换成带完整附加规则的 Clash/Mihomo 配置。
**无后端、无构建步骤、无依赖管理**——所有代码(HTML/CSS/JS)都在这一个文件里,双击即用。

外部依赖三个 CDN:
- `highlight.js` 11.11.1 — YAML 语法高亮
- `js-yaml` 4.1.0 — **模板模式**下解析/序列化 YAML(只有模板模式用到)
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
| — | 模板模式 | `SAMPLE_TEMPLATE`(默认模板)、`expandTemplateGroups`/`generateFromTemplate`(注入+展开)、模板 UI 区、`initTemplateMode`(持久化+事件)。**行号常变,按函数名搜** |

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
  - 单行 map: `- { name: ..., type: ..., server: ... }`;**键可带引号**——JSON 风格 `- {"name":"...","server":"...","type":"..."}` 也支持(`blockMapToYaml` 会剥掉 key 两端引号,否则输出成 `"name": ...` 会让下游 `getProxyName` 的 `name:` 匹配失败,导致整个节点被丢弃)
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
- **附加自定义 Clash 模板(模板模式,可选)**:勾选「附加自定义 Clash 模板」后贴入任意 Clash 模板 YAML,把节点池注入模板生成配置。与内置分组生成**二选一**——勾选且模板非空才走模板路径,默认路径不受影响。设计与坑详见下方两节。

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

### 模板模式(第二条生成路径)

- **与内置生成并存**:`generateFromTemplate()` 和内置 `generateConfig()` 二选一,勾选且模板非空时走它;内置路径一字未改。
- **节点原样文本注入,不过 js-yaml**:节点块(`parsedProxies` 里的文本)直接拼进 `proxies:`,只有模板结构(proxy-groups / dns / rules)走 `jsyaml.load`→`dump` 往返。原因:防止全数字密码、端口等标量被 YAML 重新推断类型(如密码 `0755` 变整数)。做法是把 `proxies` / `proxy-groups` 先设成占位符字符串,dump 后再 `replace` 回手拼文本。
- **`include-all`/`filter` 组就地展开,不透传**:按模板自带的 `filter` 正则在本地筛节点、填成显式列表,并删掉 `include-all`/`filter` 键。原因:sublinkPro 把这俩透传给客户端(只有新版 Mihomo 认),本工具展开后**任何 Clash 内核都能用**。正则用 JS `RegExp`(大小写敏感),`(?i)` 前缀转成 JS `i` flag;正则 JS 端解析不了时该组保留原样透传(降级)。
- **代理组输出成单行**:每组单独 `jsyaml.dump(g,{flowLevel:0})` 成 `{ ... }` 再拼 `    - `。因为 js-yaml 默认块状多行,而本工具一贯是单行 flow map。
- **四条组填充规则**(仿 subconverter/sublink):`filter`/`include-all` 展开 → 含 `__ALL_PROXIES__` 替换成全部节点 → 空 `proxies` 填全部节点 → 非空(组引用)保持不变。

## 已知坑(改之前先看)

1. **不是完整 YAML 解析器**:复杂锚点、跨行字符串、数组对象混排等高级 YAML 语法仍可能解析不完整。
2. **特殊字符 YAML 注入**:节点名/密码含极端字符时,字符串拼接仍可能生成非法 YAML。彻底修复需改用真正的 YAML 序列化。
3. **隐私**:订阅链接(含 token)会发给第三方 CORS 代理。
4. **hysteria2 默认 `skip-cert-verify: true`**:为匹配机场 sing-box(`insecure=1`)行为保证能连,牺牲了证书校验。机场用伪造 SNI(www.bing.com 等)+ 自签证书时这是常态,但若将来接入正经证书的服务端要留意。
5. **vless 字段名**:`ws-opts`/`reality-opts` 仍是手拼对象。已统一 `servername`(TLS SNI)、`client-fingerprint`、`packet-encoding`、ws `path` 解码;若再加字段注意下划线 vs 连字符。
6. `RULE_PROVIDERS` 各条目的 `url` 行末尾不要带逗号。它是字符串模板,逗号会原样进入最终 URL 导致规则集下载失败。
7. **模板模式:localStorage 会盖住 `SAMPLE_TEMPLATE`**。框内容存 `sub_template_v1`、开关存 `sub_template_on_v1`,页面加载时优先回填框——所以**改了 `SAMPLE_TEMPLATE` 源码,不点「示例」或不清 localStorage 就看不到新的**,会一直显示上次存的旧内容。
8. **模板注释会丢**:js-yaml 往返不保留 YAML 注释(sublinkPro 同样如此)。
9. **js-yaml 走 CDN,离线时模板模式不可用**:`generateFromTemplate` 检测到 `jsyaml` 未加载会返回错误提示;取消勾选可回退内置生成。

## 修改须知

- **改样式优先复用 CSS 变量 + 分组选择器**(`--chip-*`、`--btn-*`、`--bg*`、`--border*`)。复用一组规则时用分组选择器(`.a,.b{...}`),**不要用 `composes`**(纯 CSS 无效),也不要定义一个不挂到 HTML 的「基类」。
- 改输出区域时注意 `.output-code` / `.fs-code` 的滚动规则,尤其是 `min-height:0`;两者的字体/内边距 base 现在由分组选择器共享。
- 加新协议解析:仿照 `parseVlessUri` / `parseHysteria2Uri`,在 `parseAnyContent` 里加分支,并在 `nodeToYamlLine` 加字段输出;字段名对齐 Mihomo 文档(wiki.metacubex.one)。
- 加新国家/地区:同时改 `DEFAULT_GROUPS`、`COUNTRY_RULES`、`STRIP_EMOJI`,保持名字一致。
- 改信息节点判定:只改 `INFO_NODE_RE`(全局唯一来源),`mergeNodes` / `classifyNodes` / `renderNodeList` 自动跟随。
- 加新规则集/代理组:同时改 `RULE_PROVIDERS`、`RULES`、`DEFAULT_GROUPS` 三处,保持名字一致。
- 没有测试 / 没有 lint,改完直接浏览器打开验证;浏览器若限制 `file://`,至少用脚本级样例验证 `parseAnyContent()` / `mergeSource()` 和 `generateConfig()`(可用 Node 抽取函数体跑真实订阅样例)。
- 改模板模式:默认模板在 `SAMPLE_TEMPLATE` 常量(反引号模板串,里面别出现反引号或 `${`);注入逻辑在 `generateFromTemplate()` + `expandTemplateGroups()`。改完想看效果,记得**点「示例」或清 `sub_template_v1`**(否则被 localStorage 盖住)。模板要能注入节点,须留钩子:顶层 `proxies:`(注入点)、组里 `__ALL_PROXIES__`、`include-all`+`filter`、或空 `proxies`。
- 模板模式下「代理组配置」面板(内置分组的勾选/拖拽)不参与生成,输出的分组/规则全由模板决定。

---

## 附:用 OpenClash 覆写脚本(`.sh`)在路由器端等价实现

本工具的**分流结构**也可以用 OpenClash 的 `openclash_custom_overwrite.sh`(自定义覆写脚本)在路由器端等价实现 —— 它在 OpenClash 生成配置**之后**执行,`$CONFIG_FILE`(`$1`)是运行配置路径,写在「核心修改区」(`# --- 核心修改开始/结束 ---` 之间)。

**根本区别:节点不用自己解析**。OpenClash 已订阅并把节点解析进 `cfg['proxies']`,所以 `.html` 里最重的 vless/hysteria2/base64 解析、去重、信息节点过滤在 `.sh` 里**全都不做**;`.sh` 只改**结构层**(`proxy-groups` / `rule-providers` / `rules` / `dns` / header)。

**实现载体:一段 `ruby -ryaml -E UTF-8`(读一次 / 写一次)**:

- 静态 YAML(`dns`、19 个 `rule-providers`、15 条 `rules`、13 国 `COUNTRY_RULES`)用**带引号 heredoc** `<<'X'` 经环境变量传入 → **零转义**,直接照搬本文件同名常量的原文。
- Ruby 代码用单引号 `-e '...'` 包裹,**内部只用双引号/正则,绝不出现单引号**(否则提前闭合 shell 单引号)。
- 整段 `begin/rescue => e`(不捕 `SystemExit`):出错就不写文件、配置保持 OpenClash 原样,**不会断网**。

**组结构映射(`generateConfig` 各分支 → `.sh` Ruby)**:

| `.html` 组 | `.sh`(Mihomo 内核) |
|---|---|
| ♻️自动选择(所有节点) | `url-test` + **显式全节点列表**(不靠 include,防某些内核 url-test 空组硬报错) |
| 国家组(该国节点、按需输出) | `url-test` + 显式匹配节点列表,**有节点才输出** |
| 🚀手动选择 / 应用组 | `select` + `proxies:[国家组…, ♻️自动选择, DIRECT]` + `include-all-proxies: true` |
| 🛑ADblock / Adobe | `select` + `[REJECT, DIRECT]` |
| `RULE_PROVIDERS`/`RULES`/`FIXED_HEADER` | `YAML.load` 后赋给 `cfg` 的 `rule-providers`、`rules`、`dns` + 逐个设 header 标量 |

**关键设计(复刻了 `.html` 的哪条逻辑)**:

- **信息节点**:在 `cfg['proxies']` 层先 `reject!`(复刻 `isInfoNode` / `INFO_NODE_RE`),之后所有 include 组自动干净。
- **国家匹配**:Ruby 精确复刻 `getNodeCountry` —— 2~3 字母代码按整 token 匹配、中文/emoji/长名子串匹配(避免 `Singapore` 里的 `in` 误判成印度)。
- **按需输出**:只输出有节点的国家组(复刻 `refreshActiveCountryGroups`)。**空的 `url-test` 组会让 Mihomo 拒绝加载整份配置**,所以宁可不输出。
- **覆盖范围**:本次按「完全照搬 `FIXED_HEADER`」实现,连 `port`/`dns`/`external-controller` 一并覆盖;只改指定字段,不删 OpenClash 的 `redir-port`/`tproxy-port` 等透明代理端口,故不撞端口。

**扩展方法**:加国家改 Ruby 里 `OC_COUNTRY` heredoc(对应 `COUNTRY_RULES`);加规则集/规则改 `OC_RPROV`/`OC_RULES`(对应 `RULE_PROVIDERS`/`RULES`);组顺序在 Ruby 构建数组处(对应 `DEFAULT_GROUPS` 顺序)。

### 落地操作(开新对话照此编辑覆写脚本)

通过 Twinkstar 浏览器 CDP(端口 `9222`)+ `browser-harness` 远程操作 OpenClash「覆写模块」编辑器。踩坑后的稳定流程:

1. **连接** — `Invoke-RestMethod http://127.0.0.1:9222/json/version` 确认 CDP 在线,`switch_tab` 到 OpenWrt LuCI 页(`192.168.1.250/…/openclash/client`)。PowerShell 管道喂 harness 会加 BOM → 把 Python 片段写成**无 BOM 临时文件**,再 `cmd /c "browser-harness < file.py"`。
2. **打开** — 点主页「覆写模块」→ 弹出 **CodeMirror 6** 编辑器(即 `openclash_custom_overwrite.sh`)。判断弹层开没开**别用「覆写设置」文本**(顶部有常驻同名 tab),用可见的 `#oc-icon-save` 图标或「您正在编辑覆写脚本」警告。
3. **写入** — 页面暴露全局 `ocGetActiveEditorInstance()` → 返回 CM6 `EditorView`;用 `view.dispatch({changes:{from,to,insert}})` **只替换 `# --- 核心修改开始/结束 ---` 之间**,别模拟打字(会触发自动缩进/括号补全)。大段文本用 Python `json.dumps` 转成 JS 字符串字面量注入,避 emoji/引号问题。
4. **保存** — 右上角 💾(`title="保存"` + `use[href="#oc-icon-save"]`)。**坑:下载/保存/关闭图标各有多个隐藏副本**(对应订阅/配置/覆写三种编辑器),必须 `filter` 出 `getBoundingClientRect().width>0` 的**可见**那个再点,否则点到隐藏的(坐标 `0,0`)无效。
5. **关闭 + 重启** — **按 `Esc` 关弹层**(实测可行,比找关闭图标省事,直接绕开上面那些隐藏图标副本;注:编辑器底部提示「Esc 退出全屏」,若处于**全屏态** `Esc` 会先退全屏、需再按一次。备选:点可见的 `#oc-icon-close`)→ 主页「重启」按钮(`title="重启"`,在「覆写模块」**左边**),**点击即重启、无二次确认**,代理短暂断几秒。
6. **验证运行配置** — 改完**让用户自主验证**。验证入口:面板 `#edit_config`(「编辑节点 / 运行配置预览」)看**保存重启后真正运行的 YAML**;或刷新 zashboard(`:9090/ui/zashboard`)看分组/节点数。配置能加载成功本身就说明没有空 `url-test` 组、YAML 合法。

**兜底**:`capture_screenshot` 对 zashboard / 状态页实时动画**偶发 `TimeoutError`**,用 `js()` 抓 DOM 状态代替(截图失败 ≠ 操作失败)。回滚 = 把核心区换回空/旧内容再保存重启(`rescue` 保证脚本出错时配置保持原样、不断网)。