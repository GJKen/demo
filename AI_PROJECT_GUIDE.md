# AI 项目指南：Gmeek + gjken.github.io

本说明面向需要快速理解这两个相关文件夹的 AI 助手或后续维护者。

## 文件夹角色

### `D:\Study\html\Gmeek`

这个文件夹是博客生成器/模板源码。

它包含：

- `Gmeek.py`：核心的 Python 静态站点生成器。
- `templates\`：用于首页、文章、标签/搜索、页脚和基础布局的 Jinja2 HTML 模板。
- `requirements.txt`：生成器所需的 Python 依赖。
- `.github\workflows\static.yml`：一个仅部署静态内容的简单 GitHub Pages 部署工作流。

这个文件夹不是实际的博客内容仓库。它目前不包含 `config.json`，因此除非先把某个博客仓库的配置和内容复制进来，否则直接在此运行 `Gmeek.py` 会失败。

### `D:\Study\html\gjken.github.io`

这个文件夹是实际的博客仓库。

它包含：

- `config.json`：真正的博客配置。
- `.github\workflows\Gmeek.yml`：负责克隆 `gjken/Gmeek`、运行 `Gmeek.py`、提交生成文件并部署 GitHub Pages 的工作流。
- `blogBase.json`：用于增量构建的生成/缓存元数据。
- `docs\`：用于 GitHub Pages 的生成静态站点输出。
- `docs\post\`：生成的文章 HTML 文件。
- `docs\postList.json`：供标签/搜索页使用的生成文章索引。
- `backup\`：issue 正文的生成 markdown 备份。
- `static\`：复制进生成站点的自定义静态资源。

博客内容源是 `gjken.github.io` 仓库中的 GitHub Issues。

## 二者如何协同

工作流程如下：

1. 在 `gjken.github.io` 中以 GitHub Issue 的形式创建或编辑一篇博客文章。
2. `.github\workflows\Gmeek.yml` 由 `issues` 事件、手动触发或定时计划触发。
3. 工作流从 `https://github.com/gjken/Gmeek.git` 克隆生成器到 `/opt/Gmeek`。
4. 工作流把博客仓库文件复制进 `/opt/Gmeek`。
5. `Gmeek.py` 读取 `config.json`，通过 GitHub API 拉取 GitHub Issues，并生成静态文件。
6. 生成的文件被复制回 `gjken.github.io`。
7. 工作流提交更新后的生成文件。
8. GitHub Pages 部署 `docs/` 目录。

简而言之：

```text
gjken.github.io Issues
  -> gjken.github.io/.github/workflows/Gmeek.yml
  -> clone gjken/Gmeek
  -> run Gmeek.py
  -> generate docs/
  -> deploy docs/ to GitHub Pages
```

## 重要文件

### 生成器侧：`Gmeek`

- `Gmeek.py`
  - 读取 `config.json`。
  - 拉取仓库的标签和 issues。
  - 使用 GitHub 的 Markdown API 把 issue 的 markdown 转成 HTML。
  - 生成文章页、首页、标签/搜索页、RSS、`blogBase.json` 和 `postList.json`。

- `templates\base.html`
  - 共享的 HTML 外壳。
  - 加载 Primer CSS、favicon、自定义 head 注入、主题脚本、页脚和共享脚本。

- `templates\plist.html`
  - 首页/索引页模板。
  - 渲染文章列表、标签、评论数、日期、RSS、自定义链接和主题按钮。

- `templates\post.html`
  - 文章页模板。
  - 渲染文章 HTML、utterances 评论、代码复制 UI、源 issue 链接和主题控件。

- `templates\tag.html`
  - 标签/搜索页模板。
  - 在浏览器中加载 `postList.json` 并执行客户端筛选/搜索。

### 博客侧：`gjken.github.io`

- `config.json`
  - 主博客配置。
  - 当前值得注意的设置：
    - `title`：`GJKen`
    - `displayTitle`：`GJKen`
    - `i18n`：`CN`
    - `urlMode`：`issue`
    - `GMEEK_VERSION`：`main`
  - 由于 `urlMode` 为 `issue`，生成的文章 URL 是稳定的数字 URL，例如 `post/15.html`。

- `.github\workflows\Gmeek.yml`
  - 真正的构建/部署工作流。
  - 它在以下情况下运行：
    - `workflow_dispatch`
    - issue opened/edited
    - 每周定时计划
  - 它克隆 `gjken/Gmeek`、安装依赖、运行 `Gmeek.py`、提交生成产物并部署 `docs/`。

- `docs\postList.json`
  - 供标签/搜索页使用的生成文章索引。
  - 适合快速查看文章数量、标题、标签、日期和生成的 URL。

- `blogBase.json`
  - 生成的元数据/缓存。
  - 被 `Gmeek.py` 用于单 issue 增量重建。

## 当前已知状态

截至上次检查：

- `gjken.github.io` 有 14 篇生成的文章。
- 生成的文章 URL 使用 issue 编号，例如 `post/15.html`。
- `singeListJson` 中未配置单页文章。
- 标签包含的分类有：`教程`、`网站`、`CDN`、`Github`、`软件`、`Game`、`Anime`、`日常`、`VPS`、`Win`、`图片处理`、`翻墙`、`3D`、`JS`、`CSS` 和 `Bug`。

## 实用实现细节

### Issue 要求

一个 issue 必须至少有一个标签才会成为生成页面。

第一个标签具有特殊含义：

- 如果第一个标签在 `singlePage` 中列出，该 issue 会成为根级页面，例如 `about.html`。
- 否则它会成为 `docs\post\` 下的普通博客文章。

### 每篇文章的自定义配置

`Gmeek.py` 会尝试从 issue 正文中 `##` 之后的最后一行解析自定义 JSON。

支持的每篇文章字段包括：

- `timestamp`
- `style`
- `script`
- `head`
- `ogImage`

### URL 模式

在 `config.json` 中配置：

- `issue`：使用 issue 编号，URL 稳定。
- `pinyin`：把标题转为拼音。
- `ru_translit`：转写俄语标题。

实际博客当前使用 `issue`。

## 维护提示

- 要修改生成逻辑，编辑 `D:\Study\html\Gmeek\Gmeek.py` 或模板。
- 要修改博客身份信息、链接、注入脚本或视觉配置，编辑 `D:\Study\html\gjken.github.io\config.json`。
- 要修改生成的站点内容，编辑 `gjken.github.io` 中的 GitHub Issues；除非调试，否则不要手动编辑 `docs\post\*.html`。
- 除非必要，不要读取整个 `docs\post\`、`static\` 或 `backup\`；它们可能是体量大/噪声多的生成目录或资源目录。
- 要快速查看文章元数据，检查 `docs\postList.json`，而不是生成的文章 HTML。

## 主题生成任务

- 如果要根据 awesome-design-md 的 `DESIGN.md` 生成博客主题 CSS(如 `exercise_claude.css`、`exercise_airbnb.css`），
  先读 `AI_THEME_GUIDE.md`，里面是完整的可重复操作手册(素材路径、输出约定、必须覆盖的清单、硬性约束)。

## 个人工作流提示

- `D:\Study\html\demo` 是主要的本地修改仓库。所有代码和文件修改都优先在 `demo` 中进行。
- 每次修改 `.js` 或 `.css` 文件之前，必须先向用户说明计划修改的位置、原因和大致改法，并等待用户明确确认后再执行修改。
- 默认不要直接修改 `D:\Study\html\gjken.github.io`，除非用户明确要求。用户确认后，会自行把代码或文件从 `demo` 复制到 `gjken.github.io` 并推送更新。
- `docs-dev` 是用户自己创建的测试代码目录。
- `static` 是博客项目的资源目录。放在里面的文件可以通过发布后的 GitHub Pages 页面访问，方便测试外联文件。
- `docs\post` 是博客生成文章的目录，内容很多。不要轻易读取，确实需要读取时先向用户确认。
- `primer.css` 有 3 万多行代码。不要轻易读取，只在必要时查找具体选择器或小片段。
- 对于简单文本修改，优先采用「一次定位、一次最小补丁、一次简短验证」的流程，避免为了小改动反复尝试大量命令。若 `apply_patch` 在 Windows/PowerShell 下出现管道或编码问题，优先使用已经验证可行的底层 `codex.exe --codex-run-as-apply-patch` 方式传入补丁。
- `docs\` 目录下的所有 HTML 文件是 GitHub Actions 的生成产物，不要直接修改。AI 需要修改的是模板层代码（`templates\`、CSS、JS 等基础代码）。每次用户发布 git 后，Action 会重新生成文章，`docs\` 里的 CSS 和 JS 会被覆盖。

## 潜在改进

- 在 `gjken.github.io\config.json` 中添加 `email` 字段，因为工作流会读取 `.email` 用于 `git config user.email`。
- 考虑在 `Gmeek.yml` 中扩展 issue 触发器，加入 `labeled`、`unlabeled`、`reopened` 和 `closed`，以便标签或状态变更时立即重新生成站点。
- 考虑在两个仓库中都保留这份指南的副本，方便后续 AI 助手能从任一文件夹发现二者的关系。
