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
| 10–214 | `<style>` | GitHub 深色风主题、滚动容器、textarea resize handle、modal 样式 |
| 217–303 | HTML 骨架 | 三栏布局 + 全屏弹层 + 节点列表 modal |
| 305–494 | 硬编码常量 | `FIXED_HEADER`(端口/DNS)、`RULE_PROVIDERS`(规则集)、`RULES`(分流规则) |
| 497–537 | 配置数据 | `DEFAULT_GROUPS`(代理组定义)、`COUNTRY_RULES`(国家分类关键词) |
| 603–637 | `generateConfig()` | **核心**:拼接最终 YAML |
| 807–1128 | 解析器 | Clash YAML 块/单行节点、vless URI、hysteria2 URI、base64 |
| 1130–1277 | 交互逻辑 | 输入解析、复制/下载/清空、全屏、节点弹窗、Esc/遮罩关闭 |

## 核心数据流

```
输入(URL/粘贴) → processContent() → 探测格式
   ├─ base64? → atob 解码
   ├─ vless://、hysteria2:// → parseUriLinks()
   └─ Clash YAML → parseSubscription()
        ↓
parsedProxies[] + parsedNodeNames[]  (两个全局数组)
        ↓
classifyNodes() 按 COUNTRY_RULES 关键词归类到国家组
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
- URI 输入支持 `hysteria2://` 和 `vless://`,最终节点池统一输出为分块 YAML,不再输出旧的单行 `{ ... }` 节点。
- 国家自动组按需输出,当前包含香港、台湾、新加坡、日本、美国、欧洲、韩国、印度、加拿大、巴西、阿联酋、南非、墨西哥。
- 输出代码区和全屏代码区都需要保留 `overflow:auto; min-height:0`,否则 flex 布局下鼠标滚轮可能无法滚动。
- 节点列表 modal 支持关闭按钮、Esc、点击外部遮罩关闭;点击弹窗内容区不会误关。

## 关键约定 / 设计

- **YAML 仍然主要是字符串拼接生成的,不是完整序列化器**。已有 `formatYamlScalar()` / `parseYamlScalar()` 只覆盖当前节点名、URI 输出和常见标量场景,不是通用 YAML parser。
- **读入节点时尽量保留原始字段结构**:分块 YAML 会经 `normalizeProxyBlock()` 统一缩进后进入 `parsedProxies[]`;单行 map 会经 `blockMapToYaml()` 转成分块输出。
- **代理组名带 emoji 前缀**(如 `🚀手动选择`),`STRIP_EMOJI` 正则用于 UI 显示时剥离,但配置里保留完整名。
- **国家组按需输出**:`COUNTRY_RULES` 用国旗 emoji + 中文 + IATA/英文地名匹配节点;无匹配节点的国家组不会出现在最终配置里。
- **CORS 代理轮询**:`fetchFromUrl()` 依次尝试 5 个公共代理(gjken→allorigins→corsproxy→codetabs→cors-anywhere),各 15s 超时降级。
- **状态全局变量**:`parsedNodeNames` / `parsedProxies` / `selectedGroups` / `activeCountryGroups` / `_lastRenderedConfig`(高亮缓存,清空时要置 null)。

## 已知坑(改之前先看)

1. **不是完整 YAML 解析器**:复杂锚点、跨行字符串、数组对象混排等高级 YAML 语法仍可能解析不完整。
2. **特殊字符 YAML 注入**:节点名/密码含极端字符时,字符串拼接仍可能生成非法 YAML。彻底修复需改用真正的 YAML 序列化。
3. **隐私**:订阅链接(含 token)会发给第三方 CORS 代理。
4. vless 解析手拼 `ws_opts`/`reality-opts` 对象,下划线 vs 连字符字段名转换还不是完整统一。
5. `RULE_PROVIDERS` 各条目的 `url` 行末尾不要带逗号。它是字符串模板,逗号会原样进入最终 URL 导致规则集下载失败。

## 修改须知

- 改样式优先复用已有 CSS 变量(`--chip-*`、`--btn-*`、`--bg*`、`--border*`),不要新增重复声明。
- 改输出区域时注意 `.output-code` / `.fs-code` 的滚动规则,尤其是 `min-height:0`。
- 加新协议解析:仿照 `parseVlessUri` / `parseHysteria2Uri`,在 `processContent` 里加分支,并在 `nodeToYamlLine` 加字段输出。
- 加新国家/地区:同时改 `DEFAULT_GROUPS`、`COUNTRY_RULES`、`STRIP_EMOJI`,保持名字一致。
- 加新规则集/代理组:同时改 `RULE_PROVIDERS`、`RULES`、`DEFAULT_GROUPS` 三处,保持名字一致。
- 没有测试 / 没有 lint,改完直接浏览器打开验证;浏览器若限制 `file://`,至少用脚本级样例验证 `processContent()` 和 `generateConfig()`。
