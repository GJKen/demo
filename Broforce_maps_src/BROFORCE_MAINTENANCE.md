# Broforce 地图存档 · 项目维护文档

> 给后续接手维护的 AI / 开发者看的完整说明。项目实际运行在 **serv00 远程服务器** + **GitHub Pages 静态页** 的混合架构上。

---

## 一、项目概述

这是一个 **Broforce (超杀行动) Steam 创意工坊地图收藏管理站**，核心功能：

- 收藏 / 编辑 / 删除 Steam Workshop 地图记录
- 自动从 Steam 抓取地图标题、描述、预览图 URL
- 支持本地和远程两种部署方式
- 带密码鉴权 + IP 封禁 + 速率限制 + 并发限制

**当前线上部署地址（用户实际在用的）：**
- 主站：`http://s13.serv00.com:13333/static/Broforce地图记录.html`
- GitHub Pages 静态页：`https://gjken.github.io/demo/Broforce地图记录.html`

> ⚠️ **重要**：`static/Broforce地图记录.html` 和 `docs/Broforce地图记录.html` 必须**保持完全一致**（手动改完要 `cp` 同步）。GitHub Pages 用的是 `docs/`，serv00 用的是 `static/`。

---

## 二、架构与数据流

```
┌─────────────────┐      ┌──────────────────┐      ┌──────────────────┐
│  浏览器 (用户)   │ ───▶ │  serv00 服务器    │ ───▶ │  maps.json        │
│  访问的两个页面  │      │  server.py 后端   │      │  (持久化存储)     │
└─────────────────┘      └──────────────────┘      └──────────────────┘
                              ▲
                              │ 同源 HTTP
                              │
                     http://s13.serv00.com:13333
                              ▲
                              │ 跨域 CORS (白名单)
                              │
                     https://gjken.github.io/demo/...
```

**两种部署模式：**

1. **serv00 同源模式**（推荐使用）
   - 前端和后端都在 `s13.serv00.com:13333`
   - 浏览器直接访问同一域名端口，无跨域问题
   - 页面在 `~/broforce_maps/static/`
   - 后端在 `~/broforce_maps/Broforce_maps_src/server.py`
   - 数据在 `~/broforce_maps/Broforce_maps_src/maps.json`

2. **GitHub Pages 模式**（静态备份/入口）
   - 页面在 `https://gjken.github.io/demo/`
   - GitHub Pages 是 HTTPS，serv00 后端是 HTTP → **浏览器会阻止混合内容**
   - 必须通过 URL 参数 `?backend=http://s13.serv00.com:13333&token=xxx` 指定后端
   - 即使带了参数，HTTPS 页面发 HTTP 请求仍可能被浏览器拦截，**功能受限**

---

## 三、文件结构

```
repo根目录/
├── static/
│   └── Broforce地图记录.html    # 前端页面 (serv00 用)
├── docs/
│   └── Broforce地图记录.html    # 前端页面 (GitHub Pages 用，与 static 同步)
├── Broforce_maps_src/
│   ├── server.py                # Python 后端 (标准库，零依赖)
│   ├── web.bat                  # Windows 本地启动脚本
│   ├── maps.json                # 地图数据 (serv00 远程存储)
│   ├── previews/                # (已废弃) 本地预览图目录
│   ├── BROFORCE_MAINTENANCE.md  # 本维护文档
│   └── README.md                # 旧版英文 README (过时，仅供参考)
└── .gitignore                   # 忽略 server.py、maps.json 等敏感文件
```

**`docs/` 与 `static/` 同步**：改 `static/` 后立即执行
```bash
cp static/Broforce地图记录.html docs/Broforce地图记录.html
```

---

## 四、后端 server.py 详解

Python 标准库实现，**零第三方依赖**，可在 Windows/FreeBSD 直接跑。

### 4.1 认证配置（第 39-46 行）

```python
API_TOKEN = "*xxx(脱敏密码)"          # 管理密码（读写）
MAX_FAILED_ATTEMPTS = 3                 # 失败超过此次数后封禁
BAN_WINDOW_SECONDS = 3600               # 封禁时长（1 小时）
BANNED_FILE = SOURCE_DIR / "banned_ips.json"  # 封禁持久化
```

- 写操作（POST/PUT/DELETE）需 `Authorization: Bearer xxx(脱敏密码)`
- **读操作不验证**（任何人都可查看地图目录）
- 连续 3 次密码错误 → 该 IP 封禁 1 小时，封禁记录写入 `banned_ips.json`
- 换密码 = 改 `API_TOKEN` 变量，然后重启服务

### 4.2 CORS 白名单（第 48-55 行）

```python
ALLOWED_ORIGINS = {
    "https://gjken.github.io",
    "http://s13.serv00.com:13333",
    "http://31.186.87.211:13333",
    "http://127.0.0.1:13333",
    "http://localhost:13333",
}
```

只有这些来源的跨域请求被放行。**新增域名时记得添加。**

### 4.3 速率限制 & 并发限制

- 每 IP 每分钟最多 60 次请求（`RATE_LIMIT = 60`）
- 同时最多处理 10 个请求（`MAX_CONCURRENT = 10`）
- 都是内存字典实现，重启后清零

### 4.4 API 端点

| 方法 | 路径 | 鉴权 | 说明 |
|------|------|------|------|
| GET | `/api/maps` | ❌ | 获取地图列表 |
| GET | `/api/maps/{id}` | ❌ | 获取单张地图 |
| GET | `/api/health` | ❌ | 健康检查 |
| GET | `/api/previews/{file}` | ❌ | 预览图（已废弃） |
| POST | `/api/maps/fetch` | ✅ | 从 Steam 抓取地图信息 |
| POST | `/api/maps` | ✅ | 添加地图 |
| PUT | `/api/maps/{id}` | ✅ | 更新地图 |
| DELETE | `/api/maps/{id}` | ✅ | 删除地图 |
| 任意 | `/static/*` | ❌ | 静态文件 |

### 4.5 关键函数

- `read_maps()` / `write_maps()` — 读写 `maps.json`（带写锁）
- `fetch_workshop_data(map_id)` — 抓取 Steam 页面，提取 og:title、og:description、og:image
- `check_auth()` — Bearer Token 验证 + IP 封禁
- `save_map()` — 新增/更新（做了结构化校验）
- `do_GET` — 注意：静态文件（`/static/*`）不经过速率/并发限制，直接放行

### 4.6 启动

```bash
# serv00 (FreeBSD) 远程启动
cd ~/broforce_maps && nohup python3 Broforce_maps_src/server.py > server.log 2>&1 &

# Windows 本地启动
cd Broforce_maps_src && python server.py
# 或双击 web.bat

# 重启
pkill -f server.py
cd ~/broforce_maps && nohup python3 Broforce_maps_src/server.py > server.log 2>&1 &
```

---

## 五、前端 前端.html 详解

原生 HTML + CSS + JS，无框架。单个文件 950 行，全部在一个 IIFE 里。

### 5.1 配置读取（第 497-511 行）—— 最容易踩坑的地方

```javascript
const urlParams = new URLSearchParams(window.location.search);
const urlBackend = urlParams.get("backend") || "";   // URL ?backend=xxx
const urlToken = urlParams.get("token") || "";       // URL &token=xxx
const savedBackend = localStorage.getItem("broforce_backend_url") || "";
const savedToken = localStorage.getItem("broforce_auth_token") || "";

const API_BASE = urlBackend || savedBackend || (本地 ? "http://127.0.0.1:8785" : "");
// 同源访问时不应用 localStorage 的 token
const isSameOriginAccess = !urlBackend && !savedBackend && !本地;
const AUTH_TOKEN = urlToken || (isSameOriginAccess ? "" : savedToken) || "";
const canWrite = AUTH_TOKEN.length > 0;   // 有 token 才能编辑
```

**优先级**：URL 参数 > localStorage > 默认值

**注意**：同源访问（`s13.serv00.com:13333/static/...`）时，即便 localStorage 有 token 也不用——只有 URL 带 `?token=` 或主动设置后端地址才进入写模式。

### 5.2 读写模式（core bug 高发区）

| 状态 | 表现 |
|------|------|
| `canWrite = true` | 显示编辑/删除按钮、表单可填写、`formTitle="收录一张地图"` |
| `canWrite = false` | 隐藏编辑/删除、表单禁用、`formTitle="浏览地图目录"`、显示只读提示 |
| 后端连不上 | 表单隐藏，显示"后端未连接..." |

- `setLocalMode()` — 后端连接成功后，根据 `canWrite` 设置 UI
- `setStaticMode()` — 静态只读模式（GitHub Pages 兜底）
- `resetForm()` — 重置表单，**必须清空 `editHint` 文本并移除 `visible` 类**
- `renderMaps()` — 渲染地图卡片；**若正在编辑的地图不在搜索结果中，自动 `resetForm()`**

### 5.3 复制地图 ID（HTTP 兼容）

`navigator.clipboard.writeText()` 需要 HTTPS。HTTP 环境下用 `execCommand("copy")` 兜底：

```javascript
const ta = document.createElement("textarea");
ta.value = id;
document.body.appendChild(ta);
ta.select();
document.execCommand("copy");
document.body.removeChild(ta);
```

### 5.4 刷新按钮

顶栏服务器状态左侧的刷新按钮，点击后：
1. 图标旋转动画（`spinning` 类）
2. 清空卡片 + 显示"正在刷新…"
3. 加载完成后弹出"数据已刷新" toast

### 5.5 设置弹窗

- 顶栏齿轮按钮打开
- 支持 `?backend=xxx` URL 参数自动填充
- **不回显密码**（`type="password"`，防肩窥）
- 回车键触发保存
- 点遮罩关闭用 `mousedown`（防止拖拽时误关）

---

## 六、服务器运维（serv00）

### 6.1 SSH 连接

```bash
# 用户信息（敏感，勿提交 git）
host: panel13.serv00.com  (或 s13.serv00.com)
user: fcolor3dn
port: 22
```

**认证方式**：密码认证（非 SSH 密钥）。密码是项目创建时由用户提供的，不记录在文档中。如果接手的 AI 需要 SSH 连接，**请向用户询问密码**，或使用 `paramiko` 的 `password` 参数直接连接。

### 6.2 服务器目录结构

```
~/broforce_maps/
├── static/Broforce地图记录.html    # 前端
├── Broforce_maps_src/server.py     # 后端
├── Broforce_maps_src/maps.json     # 数据
├── Broforce_maps_src/banned_ips.json # 封禁记录（自动生成）
├── server.log                       # 运行日志
└── start.sh                         # 自动启动脚本
```

### 6.3 常用运维命令

```bash
# 查看服务状态
sockstat -l | grep 13333
cat ~/broforce_maps/server.log | tail -20

# 重启服务（源码更新后必须重启）
pkill -f server.py
sleep 1
cd ~/broforce_maps && nohup python3 Broforce_maps_src/server.py > server.log 2>&1 &

# 解除某个 IP 封禁（本地 IP 可能被封）
rm -f ~/broforce_maps/Broforce_maps_src/banned_ips.json
pkill -f server.py && sleep 1 && cd ~/broforce_maps && nohup python3 Broforce_maps_src/server.py > server.log 2>&1 &
```

### 6.4 上传更新文件

通过 SFTP（paramiko 脚本）将 `server.py` 和 `Broforce地图记录.html` 上传到：
- `~/broforce_maps/Broforce_maps_src/server.py`
- `~/broforce_maps/static/Broforce地图记录.html`

**改 server.py 后必须重启服务；改 HTML 不用重启。**

### 6.5 保活

serv00 空闲进程可能被回收。建议在 serv00 面板的 Cron jobs 添加：
```
*/10 * * * * curl -s http://127.0.0.1:13333/api/health > /dev/null 2>&1
```

---

## 七、GitHub Pages 维护

### 7.1 发布方式

- 仓库 `GJKen/demo`，GitHub Pages 从 `docs/` 目录发布
- 每次改 `static/Broforce地图记录.html` 后，`cp` 到 `docs/`
- 提交推送 `git push origin main`

### 7.2 访问方式

```html
<!-- GitHub Pages 访问（需带参数才能连后端） -->
https://gjken.github.io/demo/Broforce地图记录.html?backend=http://s13.serv00.com:13333&token=xxx(脱敏密码)

<!-- 只读访问（不带 token） -->
https://gjken.github.io/demo/Broforce地图记录.html?backend=http://s13.serv00.com:13333
```

### 7.3 已知限制

- GitHub Pages 是 HTTPS，后端是 HTTP → **混合内容被浏览器默认阻止**
- 实际可用性受浏览器限制，最好直接用 serv00 地址
- GitHub Pages 上的页面优先同源本地 `maps.json`（static 模式兜底）

---

## 八、安全策略

1. **密码不提交 git**：`server.py`、`maps.json`、`web.bat` 已被 `.gitignore` 忽略
2. **读操作公开，写操作需密码**：密码 = `xxx(脱敏密码)`
3. **IP 封禁**：3 次错误密码封 1 小时，持久化到 `banned_ips.json`
4. **CORS 白名单**：只允许指定域名跨域
5. **速率限制**：每分钟 60 次/IP
6. **并发限制**：同时最多 10 个请求
7. **预览图不再存本地**：直接引用 Steam CDN 图片 URL（节省磁盘和带宽）

---

## 九、常见问题排查

### 9.1 前端显示"后端未连接"

- 确认 serv00 服务在跑：`sockstat -l | grep 13333`
- 确认 URL 带 `?backend=http://s13.serv00.com:13333`
- GitHub Pages 模式可能被浏览器混合内容阻止 → 用 serv00 地址

### 9.2 显示"IP 已被封禁"

- 输错密码 3 次导致封禁
- 清 `banned_ips.json` 并重启服务（见 6.3）

### 9.3 编辑提示不消失 / 取消按钮行为异常

- `resetForm()` 必须：清空 `editHint.textContent` + `remove("visible")` + `cancelButton.hidden = true`
- 检查 `renderMaps()` 里的搜索取消编辑逻辑

### 9.4 添加地图不成功

- 写操作需要 `Authorization: Bearer xxx(脱敏密码)`
- 同源访问若无 token，是只读模式（编辑按钮不出现）
- 先在设置里填密码，或 URL 带 `&token=xxx`

### 9.5 刷新按钮无效

- 确认 HTML 是最新版（`Ctrl+F5`）
- 事件绑定在 `els.refreshBtn.addEventListener`

---

## 十、改动清单（开发历史速查）

- 端口从 8785 → **13333**（serv00 分配）
- `HOST` 从 127.0.0.1 → **0.0.0.0**（允许远程访问）
- 后端添加：Token 鉴权、IP 封禁、CORS 白名单、速率限制、并发限制
- 前端添加：URL 参数读取、设置弹窗、只读模式、刷新按钮、HTTP 复制兼容
- 预览图从本地文件 → **Steam CDN URL**（`source_preview_url` 优先）
- `web.bat` 移到了 `Broforce_maps_src/` 目录
- 敏感文件加入 `.gitignore`，git 历史已清理旧密码

---

## 十一、给接手的 AI 的实用提示

1. **先读 `server.py` 顶部配置区**（第 24-64 行）和前端第 497-526 行（配置读取），这是理解系统的最快路径
2. **改前端两个文件必须同步**：`static/` 和 `docs/`
3. **改 server.py 必须重启 serv00 服务**
4. **测试用 CDP**：参考 `/twinkstar-harness`，用 `browser-harness` 打开 `http://s13.serv00.com:13333/static/Broforce地图记录.html?xxx` 模拟操作, 密码需要向用户获取
5. **不要提交敏感文件**：`server.py`、`maps.json`、`web.bat` 都在 `.gitignore`
6. **调试先看日志**：`cat ~/broforce_maps/server.log | tail -20`
7. **本地测试**：`cd Broforce_maps_src && python server.py`，访问 `http://127.0.0.1:13333/static/Broforce地图记录.html`