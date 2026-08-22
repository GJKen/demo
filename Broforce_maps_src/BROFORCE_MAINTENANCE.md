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
│   ├── upload_to_serv00.py      # 多主机 SFTP 差异同步、备份和 SHA-256 校验
│   ├── upload_to_serv00.bat     # Windows 双击启动上传脚本
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
Windows PowerShell 可使用：
```powershell
Copy-Item -LiteralPath 'static\Broforce地图记录.html' -Destination 'docs\Broforce地图记录.html' -Force
```

---

## 四、后端 server.py 详解

Python 标准库实现，后端本身**零第三方依赖**，可在 Windows/FreeBSD 直接跑。仓库附带的 SFTP 上传工具使用第三方 `paramiko`，不属于后端运行依赖。

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
- `fetch_workshop_data(map_id)` — 抓取 Steam 页面，提取标题、描述、封面和 Steam 截图候选
- `workshop_image_candidates(page, meta_image)` — 合并 Steam 元数据图片、页面主图和截图数据，去重后返回最多 40 张候选图
- `clean_image_candidates()` / `clean_preview_urls()` — 校验候选图列表和保存的多图 URL
- `check_auth()` — Bearer Token 验证 + IP 封禁
- `save_map()` — 新增/更新（做了结构化校验）
- `do_GET` — 注意：静态文件（`/static/*`）不经过速率/并发限制，直接放行

`POST /api/maps/fetch` 返回的 `image_candidates` 是候选图片对象数组，每项包含 `url`、`label`、`type` 和 `is_default`。保存地图时，前端把用户选中的候选图 URL 或手动粘贴的 HTTP(S) 图片外链统一写入 `preview_urls` 数组；外链只保存 URL，不上传图片文件。`preview_url` 仍保留作为旧记录兼容字段。读取旧记录时，如果没有 `preview_urls`，前端会回退到 `preview_url`。

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

## 五、前端 `Broforce地图记录.html` 详解

原生 HTML + CSS + JS，无框架。页面主体全部在一个 IIFE 里；不要依赖固定行号定位代码。

### 5.1 配置读取（IIFE 开头的配置区）—— 最容易踩坑的地方

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

### 5.6 CSS 悬停提示

前端业务交互禁止使用浏览器原生提示和原生弹窗：不得添加 `title`，也不得调用 `window.alert()`、`window.confirm()` 或 `window.prompt()`。普通控件统一使用 `data-tooltip` + CSS `::after` 伪元素，长备注使用 `data-tip` + `overflow` 类；反馈使用 toast，确认操作使用页面内自定义弹窗：

- 后端设置、刷新后端数据
- 复制地图 ID
- 打开 Steam Workshop
- 点击选择本地图片
- 地图备注超出两行时显示完整内容

备注正文仍固定显示两行；`renderMaps()` 会根据 `scrollHeight > clientHeight` 自动给超长备注添加 `overflow` 类。修改提示内容时，必须同时检查 `static/` 与 `docs/`。

### 5.7 批量导入、删除和预览图

- 批量导入框自动识别 Workshop ID/URL，自动去重，单次最多处理 20 张地图；每张地图依次执行 Steam 抓取和保存，最后显示成功/失败汇总。
- 删除地图使用自定义确认弹窗，不再调用原生 `window.confirm()`；支持取消、点击遮罩关闭和 `Escape` 关闭。
- 预览图选择后只暂存在浏览器内，点击“保存地图”时才上传；单文件最大 8 MB。
- 地图预览图支持本地上传或手动图片外链；外链输入会自动识别空格、换行、逗号和分号分隔的多个 HTTP(S) URL，最多保存 40 个，图片本身不上传到服务器。
- Steam 候选图支持多选，地图记录用 `preview_urls` 保存多张图片；地图卡片支持半透明箭头、触摸横向滑动和鼠标横向拖动切换。
- 地图卡片操作区同时提供 Steam 客户端创意工坊跳转（`steam://url/CommunityFilePage/{map_id}`）和网页 Workshop 链接，Steam 图标使用内联 SVG。
- 候选图区域只显示缩略图网格；点击图片会打开半透明大图弹层，弹层支持左右箭头、触摸左右滑动、键盘左右方向键和 `Escape` 关闭。
- 候选图缩略图本身负责查看大图，缩略图下方的选择区域负责勾选/取消勾选，这样可以连续选择多张图片而不会误触预览。
- 页面切换到外部 Steam 客户端或失去焦点时会暂时隐藏 CSS tooltip，返回后移动鼠标离开原触发元素才恢复提示。
- 静态只读模式会同时禁用批量导入和预览图控件。

### 5.8 前端布局与交互硬约束

- 地图卡片正文中的 `.map-meta` 是标签区，必须通过 `margin-top: auto` 固定在正文底部；`.map-footer` 紧随标签区下方。不要把自动间距改回 `.map-footer`，否则标签会回到标题和备注下方的顶部位置。
- 修改卡片结构或 CSS 后，必须在 CDP 中检查 `#mapGrid > article:nth-child(1) > div.map-body > div.map-meta` 的 `getBoundingClientRect()`，确认它位于正文底部且 footer 仍在其下方。
- `.map-grid` 保持纵向内容可见，但横向使用 `overflow-x: clip`，并保留 `overflow-clip-margin` 让边缘 CSS tooltip 有显示空间，避免卡片图片区提示层的像素舍入产生横向滚动条；不要用全局横向裁剪替代这条局部规则。
- 地图表单使用 `novalidate`，必填项由 `saveMap()` 的自定义 toast 校验；不得恢复浏览器原生“请填写此字段”提示。
- 新增任何提示、错误反馈或确认流程时，先复用现有 CSS tooltip、toast 或自定义 modal；不得引入浏览器原生提示/弹窗。

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

仓库内的 `upload_to_serv00.py` 支持保存多套本地主机配置，并把前端、后端或地图数据单向同步到选中的远程主机。同步前后都会比较 SHA-256，只上传有差异的文件。

首次使用先安装上传工具依赖：`python -m pip install paramiko`

```powershell
python Broforce_maps_src/upload_to_serv00.py
```

也可以双击 `Broforce_maps_src/upload_to_serv00.bat`。首次运行会创建本地配置 `Broforce_maps_src/upload_hosts.local.json`，以后运行时可以选择不同主机。配置保存：

- 配置名称
- SSH 主机、端口、用户名和密码
- 远程项目根目录

SSH 密码按用户选择保存在本地配置中，选择主机后会自动使用；密码不会出现在主机列表或日志。该文件以明文存储凭据，仅适合受信任的个人电脑，并已加入 `.gitignore`，不会随 Git 提交。

可选同步范围：

- 前端页面：`static/Broforce地图记录.html`
- 后端程序：`Broforce_maps_src/server.py`
- 地图数据：`Broforce_maps_src/maps.json` 和 `previews/` 内已有文件
- 全部：以上三类一起同步

双击 BAT 并选择主机后，还可以选择“手动重启后端”，该操作只重启服务，不上传文件。

当同步范围包含地图数据时，会继续选择数据方式：

- 合并（默认）：按 `map_id` 合并，本地同 ID 记录优先，远程独有记录保留。
- 覆盖：使用本地 `maps.json` 完整替换远程版本。

这是**本地到远程的单向同步**：不会下载远程数据，也不会删除远程多余文件。远程旧文件在覆盖前备份到 `~/broforce_maps/.sync-backups/<时间>/`，再通过临时文件上传、SHA-256 校验和原子替换完成更新。合并后的 `maps.json` 也会先备份远程旧版本。

同步完成后脚本会根据变更内容自动判断是否需要重启：

- 只有实际上传的 `Broforce_maps_src/server.py` 需要重启后端；远程文件相同而被跳过时不会重启。
- 只更新前端、`maps.json` 或预览图：不重启后端。
- 使用单文件模式时，如果目标路径是项目内的 `Broforce_maps_src/server.py`，也会自动重启。
- 重启后会轮询 `/api/health` 验证服务已经恢复。
- 第一次自动重启时会隐藏输入后端 API Token，并保存到本地主机配置；以后自动复用。
- 未提供后端 API Token 时仍会完成文件同步，但会提示后端未重启。

双击运行时，脚本在一次操作结束后不会关闭窗口；按任意键会回到操作、主机选择和同步范围菜单，可以继续同步或手动重启另一台主机。带参数运行（例如 `--help`、`--plan` 或自动化调用）时仍只执行一次。

命令行直接选择已保存主机和同步范围：
```powershell
python Broforce_maps_src/upload_to_serv00.py --profile serv00-main --scope all
python Broforce_maps_src/upload_to_serv00.py --profile serv00-main --scope all --data-mode merge
python Broforce_maps_src/upload_to_serv00.py --profile serv00-main --scope data --data-mode overwrite
```

管理或查看配置：
```powershell
python Broforce_maps_src/upload_to_serv00.py --configure serv00-main
python Broforce_maps_src/upload_to_serv00.py --list-profiles
python Broforce_maps_src/upload_to_serv00.py --profile serv00-main --restart
```

只显示计划、不连接远程：
```powershell
python Broforce_maps_src/upload_to_serv00.py --profile serv00-main --scope data --plan
```

仍可直接指定单个文件和远程路径：
```powershell
python Broforce_maps_src/upload_to_serv00.py --profile serv00-main --local static\Broforce地图记录.html --remote ~/broforce_maps/static/Broforce地图记录.html
```

**只有实际改动 `server.py` 后同步工具才会自动重启服务（需要已保存或临时输入后端 API Token）；改 HTML、地图数据和预览图不用重启。**

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
- 当前 `.github/workflows/Gmeek.yml` **没有监听 `push` 事件**；普通推送后不会自动触发 Pages 部署
- 推送后必须在 GitHub 的 `Actions → build Gmeek → Run workflow` 手动触发工作流，等待 `build` 和 `deploy` 两个任务成功
- 验证发布时先检查 `raw.githubusercontent.com/GJKen/demo/main/docs/...`，再检查 Pages 页面；Pages 可能有 CDN 缓存延迟

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

### 9.6 CSS 提示不显示

- 确认 HTML 已上传/发布为最新版，并用强制刷新绕过浏览器缓存
- 检查对应元素是否有 `data-tooltip` 属性；备注提示还需要 `data-tip` 和 `map-description-wrap.overflow` 类
- 不要重新添加原生 `title`，统一维护 CSS tooltip 规则

### 9.7 Steam 页面提示“没有找到可选图片”

- 先对页面执行 `Ctrl+F5`，确认浏览器没有继续使用旧 HTML；前端改动不会通过重启后端自动更新。
- 确认页面设置中的后端地址指向当前 Serv00 服务，并打开 `/api/health` 检查服务是否在线。
- 使用同一个 Workshop ID 请求 `/api/maps/fetch`，检查返回 JSON 是否包含 `image_candidates`；这个字段为空时才是 Steam 页面解析没有提取到截图。
- 只更新 HTML 不需要重启后端；如果 `server.py` 发生更新，必须同步后端并重启。

---

## 十、改动清单（开发历史速查）

- 端口从 8785 → **13333**（serv00 分配）
- `HOST` 从 127.0.0.1 → **0.0.0.0**（允许远程访问）
- 后端添加：Token 鉴权、IP 封禁、CORS 白名单、速率限制、并发限制
- 前端添加：URL 参数读取、设置弹窗、只读模式、刷新按钮、HTTP 复制兼容
- 前端添加：批量导入（单次最多 20 张）、删除确认弹窗、备注超长提示
- 前端提示统一改为 CSS `data-tooltip` + `::after`，替代原生 `title`
- 预览图改为选择后在保存时上传
- 预览图支持自动识别多个 HTTP(S) 外链，外链直接保存到 `preview_urls`，不上传图片文件
- 预览图从本地文件 → **Steam CDN URL**（`source_preview_url` 优先）
- Steam 候选图支持多选，并通过 `preview_urls` 保存多张预览图
- 候选图改为缩略图网格 + 半透明大图弹层，支持箭头、触摸滑动和键盘切换
- 地图卡片 `.map-meta` 标签区固定在正文底部，`.map-footer` 紧随其后
- 前端业务提示/弹窗统一使用 CSS tooltip、toast 和自定义 modal，禁止原生 `title`、`alert`、`confirm`、`prompt`
- `web.bat` 移到了 `Broforce_maps_src/` 目录
- 新增 `upload_to_serv00.py` / `upload_to_serv00.bat`：保存多主机配置，同步前端、后端或数据并做备份和 SHA-256 校验
- 敏感文件加入 `.gitignore`，git 历史已清理旧密码

---

## 十一、给接手的 AI 的实用提示

1. **先读 `server.py` 顶部配置区**和前端 IIFE 开头的配置读取区，这是理解系统的最快路径
2. **改前端两个文件必须同步**：`static/` 和 `docs/`
3. **同步 `server.py` 后工具会自动重启 serv00 服务；如果未配置后端 Token，则需手动重启**
4. **测试用 CDP**：参考 `/twinkstar-harness`，用 `browser-harness` 打开 `http://s13.serv00.com:13333/static/Broforce地图记录.html?xxx` 模拟操作, 密码需要向用户获取
5. **不要提交敏感文件**：`server.py`、`maps.json`、`web.bat` 都在 `.gitignore`
6. **调试先看日志**：`cat ~/broforce_maps/server.log | tail -20`
7. **本地测试**：`cd Broforce_maps_src && python server.py`，访问 `http://127.0.0.1:13333/static/Broforce地图记录.html`
8. **同步到远程**：运行 `python Broforce_maps_src/upload_to_serv00.py`，选择主机和同步范围；只改前端时无需重启服务
9. **发布 Pages**：推送后手动运行 `Actions → build Gmeek → Run workflow`；不要只等待 `git push`
