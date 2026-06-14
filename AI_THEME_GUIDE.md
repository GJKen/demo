# AI 主题生成 Playbook(awesome-design-md → 博客主题 CSS)

本文件是一份**可重复执行的操作手册**。目标:把 awesome-design-md 里任意一份 `DESIGN.md`
转成一份可直接挂到本博客练手页、用来替代 `primer.css` 的主题 CSS。

新会话的 AI:先读本文件 + `AI_PROJECT_GUIDE.md` 的「个人工作流提示」一节,再按下面流程做。

---

## 1. 输入在哪

- **DESIGN.md 素材库**(共 74 个品牌,每个子文件夹 = 一份主题):
  `D:\Study\html\awesome-design-md-main\design-md\<brand>\DESIGN.md`
  例:`...\design-md\airbnb\DESIGN.md`、`...\design-md\claude\DESIGN.md`
  - 在线兜底(库里没有时):`https://getdesign.md/design-md/<brand>/DESIGN.md`
    （注意:`getdesign.md/<brand>/design-md` 是 HTML 页;原始 md 在 `/design-md/<brand>/DESIGN.md`）

- **练手页**:`demo\docs-dev\post\*.html`
  - 这些页面已**注释掉 `primer.css`**,保留外链 `both.css`(只负责代码语法高亮 `.pl-*`)。
  - 当前 `9.html` 引用 `exercise_claude.css`,`8.html` 可作为第二个对比页。

---

## 2. 输出约定

- **新建文件**:`demo\static\exercise_<brand>.css`(全小写品牌名)。
  - 永远是**新建独立文件**,可整体删除。
- **挂载方式**:在练手 HTML 里**加且仅加一行**:
  ```html
  <link href="../../static/exercise_<brand>.css" rel="stylesheet" />
  ```
  位置:放在所有内联 `<style>` 块**之后**、`<body>` 标签**之前**(确保样式平局时本主题胜出)。
- **可直接互换**:所有 `exercise_*.css` 选择器结构一致,换一个 link 的文件名即可切主题。
- **参考实现(照抄结构,只换 token)**:`demo\static\exercise_claude.css`、`demo\static\exercise_airbnb.css`。

---

## 3. 硬性约束(绝对不能违反)

- ❌ 不改 `both.css`、`primer.css`、`primer*.css`、**任何 `.js`**(这些是用户自己要调试的外链文件)。
- ✅ 只允许:新建 `exercise_<brand>.css` + 给练手页加那**一行 link**。
- 整套主题必须做到「删 1 个文件 + 删 1 行」即可完全还原。
- 改任何 `.css`/HTML 前,先向用户说明位置/原因/改法并**等明确确认**(见 `AI_PROJECT_GUIDE.md`)。

---

## 4. 从 DESIGN.md 抽 token

关注这几类(grep `#[0-9a-fA-F]{6}`、`fontFamily`、`rounded`/`radius`、`shadow`、以及 `description:` 那段品牌气质描述):

- **颜色**:primary/accent、canvas/background、ink/heading、body、muted、hairline/border、success/warning/error。
- **字体**:`fontFamily`(标题 vs 正文是否不同;是否衬线)。
- **圆角**:`rounded.{sm,md,lg,full}` 决定卡片/按钮的"软硬"。
- **阴影**:多数品牌只有一层柔和阴影或纯平。
- **气质**:`description:` 一句话定调(冷/暖、极简/人文、亮底/暗底)。

> 专有字体(Airbnb Cereal、Geist、Copernicus、Styrene…)一律**不外链盗用**,用免费等价物兜底:
> 无衬线→ `Inter / -apple-system / PingFang SC / Microsoft YaHei`;衬线→ `Georgia / Songti SC / Noto Serif SC`。

---

## 5. 必须覆盖的清单(去掉 primer 后会塌的部分)

每份主题 CSS **都要包含**以下内容,缺一会导致页面残缺:

1. **两套 token**:`:root,[data-color-mode="light"]{…}` 与 `[data-color-mode="dark"]{…}`。
   - 明暗切换**复用页面原有 `modeSwitch()`(切 `data-color-mode`),JS 不动**。
   - 某些品牌无官方暗色(如 Airbnb)→ 基于品牌主色**合成**一套协调暗色,并在注释里说明。
2. **映射到 Primer 变量名**(这样页面内联样式 + 5 个 `markdown-alert` 不用改 HTML 就能变色):
   `--color-border-default`、`--color-fg-default`、`--color-fg-muted`、`--color-fg-on-emphasis`、
   以及 `--color-{accent,success,done,attention,danger}-{fg,emphasis,subtle}`。
   - 警告框语义映射:note→accent、tip→success、important→done(紫)、warning→attention(琥珀)、caution→danger(红)。
   - subtle 底色:亮色用浅色 tint,暗色用 `rgba(emphasis, .15)`。
3. **正文排版 `.markdown-body`**:h1–h6、p、ul/ol/li、strong/em、行内 `code`、`pre`/代码块、blockquote、table/th/td、hr、img、details/summary、`.highlight`。
   - **`summary` 必须加 `user-select:none`(易漏!)**:不然双击 `<summary>` 会选中其文字、移动端还会弹出复制/选择框,体验很差。
     ```css
     .markdown-body summary { cursor: pointer; -webkit-user-select: none; user-select: none; }
     ```
4. **按钮**:`.btn`、`.btn-invisible`、`.circle`、`.btn-block`;`.octicon{fill:currentColor}`。
   - **顶部圆形按钮新拟物阴影(易漏!)**:primer 给 `#functionBtn` 里的圆形按钮做了双层阴影——
     静止态外凸柔光、按下/选中态翻转为 `inset` 内凹。去掉 primer 后必须补回,否则按钮变"平"。
     做法:每套 token 里定义两个阴影变量,组件只引用变量(明暗/各品牌各自调色)。
     **变量名必须叫 `--header-btn-shadowColor` 和 `--header-btn-shadowColor2`(别自创名!)**:
     `ArticleJs.js` 给 TOC 目录按钮按下态、`.toc-btn div:active` 直接写死了 `var(--header-btn-shadowColor[2])`
     (见 `ArticleJs.js` 的 `toggleTOC()` 与注入的 toc 样式)。用这两个名 = 顶部圆按钮和 TOC 按钮共用一套阴影色、随主题联动;
     用别的名 JS 那边读不到、TOC 按钮阴影会失效。注意第一个**没有数字后缀**(不是 `...Color1`)。
     ```css
     /* token(light 举例) */
     --header-btn-shadowColor:  #ffffff66;   /* 高光(右下) */
     --header-btn-shadowColor2: #5f574d24;   /* 暗影(左上) */
     /* 组件 */
     #functionBtn .btn-invisible {
       color: var(--heading);  /* 默认:随主题正文/标题色,别用强调色 */
       box-shadow: 6px 6px 14px 0 var(--header-btn-shadowColor), -7px -7px 16px 0 var(--header-btn-shadowColor2);
       transition: box-shadow .4s ease-in-out, filter .4s ease-in-out, color .15s ease;
     }
     /* hover 才上强调色(对应 primer 的 --color-accent-fg) */
     #functionBtn .btn-invisible:hover { background-color: transparent; color: var(--accent); filter: brightness(1.05); }
     #functionBtn .btn-invisible:active,
     #functionBtn .btn-invisible.selected,
     #functionBtn .btn-invisible[aria-selected="true"],
     #functionBtn .btn-invisible.zeroclipboard-is-active {
       box-shadow: 6px 6px 14px 0 var(--header-btn-shadowColor) inset, -7px -7px 12px 0 var(--header-btn-shadowColor2) inset;
     }
     ```
     暗色一般用 `#00000055` 暗影 + 一抹品牌色微辉光(如珊瑚 `#d98a6e1f` / 品牌红 `#ff5a781f`),
     比 primer 原写死的蓝调 `#9bdfff14` 更贴合主题。
     - **按下态选择器要凑齐 4 个(易漏第 4 个)**:primer 的 inset 态作用于
       `:active, .selected, [aria-selected=true], .zeroclipboard-is-active` 四态,**别只写前三个**。
       第 4 个 `.zeroclipboard-is-active` 是 GitHub 复制按钮按下时 JS 加的类;本模板的复制按钮是
       `.ClipboardButton`(不带 `.btn-invisible`)所以当前不触发,但**照抄齐全 = 与 primer 选择器集一致 + 防未来踩坑**。
       注意 inset 态的左上阴影 blur 是 **12px**(静止外凸态是 16px),两者不要写成一样。
5. **复制按钮 + 被 JS 注入用到的工具类**:`.snippet-clipboard-content`、`.ClipboardButton`、
   `.position-relative/.position-absolute`、`.top-0`、`.right-0`、`.overflow-auto`、`.d-none`、`.m-2`、`.mr-2`、`.p-0`、`.color-fg-success`。
6. `#footer`、`.AnimatedEllipsis`、移动端 `@media (max-width:600px)`。
7. **body / html 必须分两层底色(易漏!)**:练手页的 `body` 是 `max-width:900px; margin:auto` 的居中容器,
   `html` 是它背后铺满视口的底。若 body 和 html 同色,正文卡片的边界会"糊"在背景里、毫无层次。
   - 做法:给 `html` 一个比 body **深一档**的底色,body 保持 canvas 色并加柔光晕浮起来:
     ```css
     /* token:两套各调 */
     --bg:            #ffffff;            /* body 纸面(canvas) */
     --body-bg:       #f0f0f0;            /* html 视口底,比 body 深一档 */
     --body-shadow-color: rgba(0,0,0,.10);/* body 周围柔光晕 */
     /* 组件 */
     html { background-color: var(--body-bg); transition: background-color .5s ease; }
     body {
       background-color: var(--bg);
       box-shadow: 0 0 100px var(--body-shadow-color);  /* 正文浮于 html 之上 */
       border-radius: var(--radius-lg);  /* 纸面圆角(易漏!)——按品牌圆角档取,16~20px */
       transition: background-color .5s ease, color .5s ease, box-shadow .5s ease;
     }
     ```
     暗色:html 用比 body **更深**的近黑(如 body `#1c1c1e` → html `#0e0e0f`),光晕换成更重的 `rgba(0,0,0,.55)`。
   - **主题切换过渡统一 `.5s ease`**,且 `html` 也要带 transition,否则只有 body 渐变、视口底瞬切会很跳。
8. **滚动条主题化(易漏!)**:去掉 primer 后滚动条回退成系统默认丑样式。每份主题补:
   ```css
   * { scrollbar-width: thin; scrollbar-color: var(--border) transparent; }  /* Firefox 兜底 */
   ::-webkit-scrollbar { width: 8px; height: 8px; }
   ::-webkit-scrollbar-track { background: transparent; }
   ::-webkit-scrollbar-thumb { background: var(--border); border-radius: var(--radius-pill, 9999px); }
   ::-webkit-scrollbar-thumb:hover { background: var(--muted); }
   ```
   thumb 用 `--border`、hover 用 `--muted`,自动跟随明暗主题;圆角加 `9999px` fallback(有的主题没定义 `--radius-pill`)。

> 语法高亮 `.pl-*` 已由 `both.css` 提供,**不要重复定义**。

---

## 6. 新会话快速通道(TL;DR)

1. 读本文件 +「个人工作流提示」。
2. 与用户确认品牌名。
3. 读 `awesome-design-md-main\design-md\<brand>\DESIGN.md`,抽 token(第 4 节)。
4. 复制 `exercise_claude.css` 的结构,替换 token 值 + 体现该品牌的字体/圆角/气质差异(第 5 节清单逐项过)。
5. 报备方案 → 经确认后:新建 `exercise_<brand>.css` + 给练手页加一行 link。

---

## 7. 已完成的样例

| 主题 | 文件 | 气质 |
|---|---|---|
| Claude | `static/exercise_claude.css` | 奶油米白 + 珊瑚 `#cc785c`,衬线标题,中等圆角 |
| Airbnb | `static/exercise_airbnb.css` | 纯白 + 品牌红 `#ff385c`,无衬线克制字重,足量圆角 + 药丸 CTA |
