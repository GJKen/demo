# 前言
OoenClash 是一个运行在 OpenWrt 上的 Mihomo(Clash) 客户端, 兼容 Shadowsocks(R)、Vmess、Trojan、Snell 等协议, 根据灵活的规则配置实现策略代理

官网 [Github](https://github.com/vernesong/OpenClash)

# Geo配置相关

|文件名|来源|
|-|-
| GeoIP MMDB | Oenclash自带(Alecthw-lite-Version(全部国家且仅写入 iso_code 和 geoname_id))
| GeoIP Dat | Oenclash自带 fastly
| GeoSite | Oenclash自带 fastly
| Geo ASN | Oenclash自带 fastly

# Yaml 配置相关

## Clash 节点自动生成分流规则
AI 写的功能, 自用, 部分配置摘抄自 [Github](https://github.com/HenryChiao/MIHOMO_YAMLS/blob/main/THEYAMLS/General_Config/666OS/MihomoPro_Config.yaml)

在线地址 [link](https://gjken.github.io/demo/%E8%AE%A2%E9%98%85%E8%BD%AC%E6%8D%A2.html)

### 功能简介

<details><summary>点击展开</summary>

## 概述

纯前端工具页面，用于将机场订阅节点提取出来，套上预设的分流规则和代理组模板，生成一份可直接导入 OpenClash 的完整 Clash 配置文件。

---

## 一、订阅输入（左面板）

### 1.1 远程获取
- 输入订阅链接，点击"获取"
- 内置 5 个 CORS 代理（gjken workers、allorigins、corsproxy、codetabs、cors-anywhere）依次尝试
- 每个代理 15 秒超时，自动切换下一个

### 1.2 手动粘贴
- 直接在文本框粘贴订阅内容，点击"使用此内容"

### 1.3 格式自动识别
支持三种输入格式，自动判断：

| 格式 | 说明 |
|------|------|
| Clash YAML | 标准 Clash 订阅，解析 `proxies:` 段 |
| URI 链接 | `hysteria2://` 和 `vless://` 协议，逐行解析 |
| Base64 编码 | 自动检测并解码后再按上述两种格式处理 |

### 1.4 节点分类
- 按关键词自动归类到 7 个国家/地区：

| 标签 | 地区 | 匹配关键词示例 |
|------|------|----------------|
| HK | 香港 | 香港、🇭🇰、HK、HKG、HongKong |
| TW | 台湾 | 台湾、🇹🇼、TW、KHH、Taiwan |
| SG | 新加坡 | 新加坡、🇸🇬、SG、Singapore |
| JP | 日本 | 日本、🇯🇵、JP、Tokyo、东京 |
| US | 美国 | 美国、🇺🇸、US、LAX、SJC 等 |
| EU | 欧洲 | 法国、德国、英国、🇫🇷、FRA、AMS 等 |
| KR | 韩国 | 韩国、🇰🇷、Seoul、KOR |

- 自动过滤信息节点（包含"剩余流量""套餐到期"等关键词的条目）

### 1.5 统计展示
解析成功后显示：
- 总节点数
- 覆盖国家数
- 代理组数量
- 可弹窗查看完整节点列表（带国家标签着色）

---

## 二、代理组配置（中间面板）

### 2.1 预设代理组（17 个）

#### 功能组

| 组名 | 类型 | 说明 |
|------|------|------|
| 🚀手动选择 | select | 包含所有节点 + DIRECT，可附加子组 |
| ♻️自动选择 | url-test | 全部节点自动测速 |
| AIGC | select | AI 服务（Claude、OpenAI、Bard 等） |
| PikPak | select | PikPak 网盘 |
| PicHub | select | 图片站 |
| Telegram | select | Telegram 相关 |
| Google | select | Google 服务 |
| 🛑ADblock | select | 固定 REJECT / DIRECT |
| Adobe | select | 固定 REJECT / DIRECT |
| 🐟漏网之鱼 | select | 兜底规则 |

#### 国家自动测速组

| 组名 | 说明 |
|------|------|
| 🇭🇰香港 Auto | 仅含匹配到的香港节点，url-test |
| 🇹🇼台湾 Auto | 同上，台湾节点 |
| 🇸🇬新加坡 Auto | 同上，新加坡节点 |
| 🇯🇵日本 Auto | 同上，日本节点 |
| 🇺🇸美国 Auto | 同上，美国节点 |
| 🇪🇺欧洲 Auto | 同上，欧洲节点 |
| 🇰🇷韩国 Auto | 同上，韩国节点 |

> 国家组仅在实际存在对应节点时才会出现在配置中。

### 2.2 子组附加
- 对 `canSelect` 类型的组（手动选择、AIGC、Google 等），可展开勾选要附加的 url-test 子组
- 支持全选/取消全选
- 解析节点后默认自动全选所有匹配到节点的国家组

---

## 三、配置输出（右面板）

### 3.1 生成内容
点击"生成配置"后，拼接完整的 Clash YAML，包含四个部分：

1. **基础设置** — 端口（7890-7895）、DNS（fake-ip 模式、国内外分流）、认证跳过等
2. **proxies** — 从订阅解析出的全部节点
3. **proxy-groups** — 根据用户勾选动态生成
4. **rule-providers + rules** — 内置分流规则

### 3.2 内置规则集

| 规则集 | 指向代理组 | 来源 |
|--------|-----------|------|
| private | DIRECT | MetaCubeX |
| cn_domain / cn_ip | DIRECT | MetaCubeX |
| adobe | Adobe | GJKen |
| pic_hub | PicHub | GJKen |
| steam | 🚀手动选择 | blackmatrix7 |
| google | Google | GJKen |
| claude | AIGC | GJKen |
| ai_GC | AIGC | GJKen |
| openai / bard / bing / copilot | AIGC | blackmatrix7 |
| pikpakdomain | PikPak | GJKen |
| telegram | Telegram | GJKen |
| geolocation-!cn | 🚀手动选择 | MetaCubeX |
| MATCH（兜底） | 🐟漏网之鱼 | — |

### 3.3 操作按钮

| 按钮 | 功能 |
|------|------|
| ⚡ 生成配置 | 根据当前节点和勾选生成 YAML |
| 📋 复制 | 复制到剪贴板 |
| 💾 下载 | 下载为 `config.yaml` |
| 🗑 清空 | 重置所有状态 |
| ⛶ 全屏 | 全屏查看生成的配置（带语法高亮） |

---

## 四、技术细节

- 纯前端，无后端依赖，单 HTML 文件即可运行
- YAML 语法高亮使用 highlight.js（vs2015 主题）
- 脏检查机制避免重复渲染
- 响应式布局：三栏 → 两栏 → 单栏（900px / 600px 断点）
- ESC 键关闭所有弹层

</details>

