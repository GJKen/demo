[Gmeek](https://github.com/Meekdai/Gmeek) 博客完全依托 Github, 提供域名, 无需服务器, 比起传统的服务器建站更方便快捷.

# 搭建博客

**如何搭建博客我就不写了, 强烈建议看完[官方文档](https://blog.meekdai.com/tag.html#gmeek).**

**这里主要记录一些 js 和 CSS 的修改.记录的修改不一定准确, `Gmeek-spoilertxt="因为改动的地方太多了🥴"`.**

> [!WARNING]
> 利用 Github Page 搭建的网站内容是完全公开的, 请注意不要上传自己的隐私!!!

# Config.json 小妙用

## 引用顺序

官方虽然没说, 但是经过我后面测试得出:

`script`字段里面引用的 js 代码, **写在尾巴加载顺序越靠前!**

> 其它字段还未测试过, 不知道是不是一样的道理.

## subTitle - js插入

代码:

```json
"subTitle":"<script>document.getElementById('content').innerHTML = `<div style='text-align: center;'><p>CV工程师,</p><p>一个又菜又爱玩, 喜欢瞎折腾的流浪者.</p></div>`;</script>",
```

CSS 效果:

![2024-12-30-1-8b58a3c8283110590642d5aeb1f60ad0](https://github.com/user-attachments/assets/704ba114-c255-469e-ac71-61ccdffac962)

从图中可以看到, `subTitle`字段可用 js 插入 html 实现修改文字.

## subTitle - 隐藏

`"subTitle":" ",`

效果图:

![2024-12-30-1-77a044632caf5ccc0b0ec4f986b4435d](https://github.com/user-attachments/assets/92e2da59-1bb4-4c4c-a2ae-b58105ecc230)

可以用空白字符的方式, 隐藏`subTitle`这个必须字段, 无需使用 js 隐藏.

# 记录功能块代码

代码摘抄自网络, 有删改, 都存放在仓库, 使用 jsdelivr CDN 加速.

## [ArticleJs.js](https://github.com/GJKen/gjken.github.io/blob/main/static/ArticleJs.js) - 文章自定义 js 代码

### 图片图片浏览器+图片懒加载整合

[图片浏览器的代码](#fancybox.js---图片浏览器)

[图片懒加载的代码](#图片懒加载)

👇这里说明一下, 图片浏览器和图片懒加载的整合后的工作流程:

<details><summary>点击展开</summary>

`Gmeek-imgbox`首先匹配到关键字后转化标签.

`Gmeek.py`匹配转换的代码如下:

```python
        if '<code class="notranslate">Gmeek-imgbox' in post_body:
            post_body = re.sub(r'<p>\s*<code class="notranslate">Gmeek-imgbox="([^"]+)"</code>\s*</p>', lambda match: f'<div class="ImgLazyLoad-circle"></div>\n<img data-fancybox="gallery" img-src="{match.group(1)}">', post_body, flags=re.DOTALL)
```

markdown 输入:

```
`Gmeek-imgbox="https://example.com/image.jpg"`
```

实际转化后的标签如下:

```html
<div class="ImgLazyLoad-circle"></div>
<img data-fancybox="gallery" img-src="https://example.com/image.jpg">

<!--
一个图片未加载时的占位 CSS 动画 DIV, 类名为 .ImgLazyLoad-circle, 这个类名的 CSS 动画我写在了 primer.css 里面.
一个 img 标签, 包含 fancybox 所需的 data-fancybox="gallery" 值.
-->
```

当页面加载完成后, 使用 IntersectionObserver 监听图片是否进入视口, 图片会提前 500px 接近视口时加载

当图片即将进入视口时, 脚本会检测标签里面的`img-src="https://example.com/image.jpg"`内容,  给 img 标签增加`src`值, 这样图片就能显示了.

在 CSS 中 img 标签默认模糊并且透明图片, 脚本会等待图片加载完成后才会正常显示, 显示图片之前会隐藏掉占位转圈动画, 这样就实现了转圈动画消失并显示正常的图片.

图片加载失败则会创建指定的 SVG 图标以及文字提示, 同时隐藏加载失败的 img 标签和占位动画.

大概就是这样的一个流程.

</details>

## [ArticleToc.js](https://github.com/GJKen/gjken.github.io/blob/main/static/ArticleToc.js) - 文章增加目录列表+一键返回顶部按钮(v1.0)

> 摘抄来源: [Github](https://github.com/cao-gift/cao-gift.github.io?tab=readme-ov-file)
> 修改-创建`.toc`的位置为body里面.
> 修改-批量给 a 标签创建的类名为: `toc-h1` `toc-h2` ... `toc-h6`
> 修改-适配切换博客主题颜色.
> 修改-增加滚动页面同时滚动章节.
> 修改-动画和样式.
> 修改-滚动页面自动显示&隐藏返回顶部按钮.

图示:

![image](https://github.com/user-attachments/assets/2d12652a-ee57-44a7-bd41-17f618a0785b)

可以直接引用.

## 文章增加目录列表(集成到header)

这版把目录按钮集成到了文章的`#header`的按钮里面.

功能和[v.1.0版本](#articletoc.js---文章增加目录列表+一键返回顶部按钮(v1.0))差不多一致(小改动), 同时打算把按钮统统放入`#functionBtn`标签里面, 代码也统一放入 ArticleJs.js 里面.

> 修改-当滚动页面使`#functionBtn`按钮不可见时, 使其悬浮在顶部.
> 修改-文章目录增加顶部和底部跳转按钮.

图示:

![image](https://github.com/user-attachments/assets/cb85ad0f-0e19-42e0-bb3e-45399a5ca7f7)

![2024-12-30-1-b0ad706ab827b475640e589ff44a3e13](https://github.com/user-attachments/assets/3f84c22d-43cc-489f-9df0-d6ffa24feb42)

## Fancybox.js - 图片浏览器

> Fancybox [官网](https://www.fancyapps.com)

### config.json 里引用 Fancybox 所需的 CSS 和 JS

> 注意末尾的标点符号.

我这里用的是`5.0`版本, cdn 加速链接.

```json
"script":"<script src='https://fastly.jsdelivr.net/gh/gjken/gjkdemo.github.io@main/static/ArticleJs.js'></script><script src='https://fastly.jsdelivr.net/npm/@fancyapps/ui@5.0/dist/fancybox/fancybox.umd.js'></script>"
```

CSS写入到了👉[文章自定义 js 代码](#articlejs.js---文章自定义-js-代码)

内容如下:

意思是页面加载完成再加载 CSS, 同时增加 fancybox 必要的绑定函数.

```Javascript
document.addEventListener('DOMContentLoaded', () => {
    document.head.appendChild(
        Object.assign(document.createElement('link'), {
            rel: 'stylesheet',
            href: 'https://fastly.jsdelivr.net/npm/@fancyapps/ui@5.0/dist/fancybox/fancybox.css'
        })
    );
    Fancybox.bind('[data-fancybox="gallery"]', {});
});
```

### 增加自定义匹配 - Gmeek-imgbox

修改 Gmeek 仓库的 Gmeek.py

> 不知道怎么自定义 Gmeek 仓库的看这👉[通过 Gmeek 仓库 DIY 博客](#通过-gmeek-仓库-diy-博客)

打开`Gmeek.py`文件, 定位字符串`Gmeek-html`

然后在下面增加代码:

```python
        if '<code class="notranslate">Gmeek-imgbox' in post_body: 
            post_body = re.sub(r'<code class="notranslate">Gmeek-imgbox="([^"]+)"</code>',lambda match: f'<img data-fancybox="gallery" src="{match.group(1)}">',post_body, flags=re.DOTALL)
```

- **使用演示**

在 markdown 插入图片:

```html
`Gmeek-imgbox="https://i0.img2ipfs.com/ipfs/QmNiH2pdrA9Hb61EXgYbKtEssBAGemEjTQRBZbgutUCNx2"`
```

通过 Actions 转换后实际效果如下, html 里面图片标签会增加 fancybox 所需的`data-fancybox="gallery"`属性.

![image](https://github.com/user-attachments/assets/90439bbe-7ced-409b-a4c7-62f859c842ab)

## 图片懒加载

> 来源: [Github](https://github.com/liyifanniubi/liyifanniubi.github.io)

代码内容合并到👉[文章自定义 js 代码](#articlejs.js---文章自定义-js-代码)

关键内容如下:

<details><summary>Javascript Code</summary>

```Javascript
    // 懒加载图片
	const ob = new IntersectionObserver((entries) => {
		entries.forEach(entry => {
			if (entry.isIntersecting) {
				const img = entry.target;
				const imgContainer = img.previousElementSibling;
				const handleError = (isError = false) => {
					if (imgContainer && imgContainer.classList.contains('ImgLazyLoad')) {
						imgContainer.style.display = 'none';
					}
					if (isError) {
						const errorContainer = document.createElement('div');
						errorContainer.classList.add('Imgerror-container');
						errorContainer.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" style="height:60px;" class="Imgerror" viewBox="0 0 1024 1024"><path fill="#ff5b5b" d="M320 896h-77.833L515.92 622.253a21.333 21.333 0 0 0 3.16-26.133l-89.427-149.053 165.427-330.86A21.333 21.333 0 0 0 576 85.333H96a53.393 53.393 0 0 0-53.333 53.334v746.666A53.393 53.393 0 0 0 96 938.667h224A21.333 21.333 0 0 0 320 896zM96 128h445.48L386.253 438.46a21.333 21.333 0 0 0 .787 20.513L474 603.86l-69.333 69.333-89.62-89.653a53.333 53.333 0 0 0-75.427 0L85.333 737.827v-599.16A10.667 10.667 0 0 1 96 128zM85.333 885.333v-87.166l184.46-184.454a10.667 10.667 0 0 1 15.08 0l89.627 89.62L181.833 896H96a10.667 10.667 0 0 1-10.667-10.667zm192-458.666C336.147 426.667 384 378.813 384 320s-47.853-106.667-106.667-106.667S170.667 261.187 170.667 320s47.853 106.667 106.666 106.667zm0-170.667a64 64 0 1 1-64 64 64.073 64.073 0 0 1 64-64zM928 128H661.333a21.333 21.333 0 0 0-19.08 11.793l-.046.087c-.04.087-.087.173-.127.253L535.587 353.127a21.333 21.333 0 1 0 38.16 19.08l100.773-201.54H928a10.667 10.667 0 0 1 10.667 10.666V652.5L783.713 497.54a53.333 53.333 0 0 0-75.426 0L571.08 634.747a21.333 21.333 0 0 0-3.153 26.153l24.666 41.08-203.646 244.36a21.333 21.333 0 0 0 16.386 34.993H928A53.393 53.393 0 0 0 981.333 928V181.333A53.393 53.393 0 0 0 928 128zm0 810.667H450.88L635.053 717.66a21.333 21.333 0 0 0 1.907-24.667l-23.933-39.886L738.46 527.68a10.667 10.667 0 0 1 15.08 0l185.127 185.153V928A10.667 10.667 0 0 1 928 938.667z"/></svg><p class="Imgerror-message">图片错误</p>`;
						img.parentNode.insertBefore(errorContainer, img.nextSibling);
						img.style.display = 'none';
					} else {
						img.classList.remove('ImgLazyLoad');
						img.classList.add('ImgLoaded');
					}
				};

				img.src = img.getAttribute('img-src');
				ob.unobserve(img);

				img.onload = () => handleError(false);
				img.onerror = () => handleError(true);
			}
		});
	}, {
		rootMargin: '0px 0px 500px 0px',
	});

	document.querySelectorAll('[img-src]').forEach(img => ob.observe(img));
```

</details>

加载动画 CSS, 我把它写到了`primer.css`文件里面.

<details><summary>CSS Code</summary>

> 这个主要样式一定要写在`:root`选择器的前面!

```CSS
[data-color-mode=light][data-light-theme=dark],
[data-color-mode=light][data-light-theme=dark]::selection,
[data-color-mode=dark][data-dark-theme=dark],
[data-color-mode=dark][data-dark-theme=dark]::selection {
	--ImgLazyLoad-circle-shadowColor:#27272745;
	--ImgLazyLoad-circle-shadowColor2:#28dddf4a;
}

/* 图片懒加载占位css动画 */
.ImgLazyLoad-circle {
	width: 40px;
	height: 40px;
	border-radius: 50%;
	border: 6px #f3f3f3 solid;
	border-top: 6px #8aefff solid;
	transition: filter 0.5s ease, opacity 0.5s ease;
	animation: ImgLazyLoadAni 1.2s infinite;
	-webkit-animation: ImgLazyLoadAni 1.2s infinite;
	box-shadow: 6px 6px 14px 0 var(--ImgLazyLoad-circle-shadowColor), -7px -7px 16px 0 var(--ImgLazyLoad-circle-shadowColor2);
}

@keyframes ImgLazyLoadAni {
	0% {
		transform: rotate(0)
	}

	100% {
		transform: rotate(360deg)
	}
}

@-webkit-keyframes ImgLazyLoadAni {
	0% {
		-webkit-transform: rotate(0)
	}

	100% {
		-webkit-transform: rotate(360deg)
	}
}

/* 图片懒加载文字提示样式 */
.Imgerror-message {
	color: #ff5b5b;
	font-size: 100%;
	user-select: none;
}

/* 图片模糊渐显样式 */
[data-fancybox="gallery"]{
    opacity: 0;
    filter: blur(15px);
    transition: opacity 0.5s ease, filter 0.5s ease;
}
.ImgLoaded {
	opacity: 1;
    filter: blur(0);
}

:root {
	--ImgLazyLoad-circle-shadowColor:#0000;
	--ImgLazyLoad-circle-shadowColor2:#ebfffe
}
```

</details>

## [GmeekVercount_uv.js](https://github.com/GJKen/gjken.github.io/blob/main/static/GmeekVercount_uv.min.js) - 网站增加访客计数器

> Vercount [Github](https://github.com/EvanNotFound/vercount)
> pv 修改成 uv 计数.

建议放入`allHead`里全站添加 js.

```json
"allHead":"<script src='https://cdn.jsdelivr.net/gh/gjken/gjkdemo.github.io@main/static/GmeekVercount_uv.min.js'></script>"
```

## [NumPagination.js](https://github.com/GJKen/gjken.github.io/blob/main/static/NumPagination.js) - 主页添加数字分页条

> 来源 [Github](https://github.com/liyifanniubi/liyifanniubi.github.io)

未实际测试过.

# 通过 primer.css, 修改博客样式

[primer.css](https://github.com/GJKen/gjken.github.io/blob/main/static/primer.css), 这个文件用来控制网站的整体样式, 存放在我的 git 仓库, 使用 jsdelivr CDN 加速.

对应的选择器只张贴出关键 CSS 部分的修改, ~~不然代码太多了.~~

下面是修改笔记, 不一定实际使用.

> 已知bug: 给body增加`backdrop-filter: blur(30px);`样式时, 会出现页面异常, 待后续修复.

## \<html> 标签样式

`[data-color-mode]`

> [!NOTE]
> 优化 light & dark 主题下的背景色.
> 增加兼容性动画过渡.

<details><summary>修改前</summary>

```CSS
[data-color-mode] {
    color: var(--fgColor-default, var(--color-fg-default));
    background-color: var(--bgColor-default, var(--color-canvas-default))
}
```

</details>

<details><summary>修改后</summary>

```CSS
[data-color-mode=light][data-light-theme=dark],
[data-color-mode=light][data-light-theme=dark]::selection,
[data-color-mode=dark][data-dark-theme=dark],
[data-color-mode=dark][data-dark-theme=dark]::selection {
    --html-bgColor: #151c2f;/* 增加 */
}
:root {
    --html-bgColor: #fff;/* 增加 */
}
[data-color-mode] {
    color: var(--fgColor-default, var(--color-fg-default));
    background-color: var(--html-bgColor);
    -webkit-transition: background-color 0.5s ease;/* 增加 */
    -moz-transition: background-color 0.5s ease;/* 增加 */
    -o-transition: background-color 0.5s ease;/* 增加 */
    transition: background-color 0.5s ease;/* 增加 */
}
```

</details>

## \<body> 标签样式

`body`

> [!NOTE]
> 优化 light & dark 主题下的背景色.
> 增加宽高过渡动画.
> 增加 1080px 屏幕宽度响应

<details><summary>修改前</summary>

```CSS
body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Noto Sans", Helvetica, Arial, sans-serif, "Apple Color Emoji", "Segoe UI Emoji";
    font-size: var(--body-font-size, 14px);
    line-height: 1.5;
    color: var(--fgColor-default, var(--color-fg-default));
    background-color: var(--bgColor-default, var(--color-canvas-default))
}
```

</details>

<details><summary>修改后</summary>

```CSS
[data-color-mode=light][data-light-theme=dark],
[data-color-mode=light][data-light-theme=dark]::selection,
[data-color-mode=dark][data-dark-theme=dark],
[data-color-mode=dark][data-dark-theme=dark]::selection {
    --body-bgColor: #3b3b3bd9;/* 增加 */
    --body-shadow-color: #52afff3d;/* 增加 */
}
:root {
    --body-bgColor: #ffffffde;/* 增加 */
    --body-shadow-color: #50a8e726;/* 增加 */
}
body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Noto Sans", Helvetica, Arial, sans-serif, "Apple Color Emoji", "Segoe UI Emoji";
    font-size: var(--body-font-size, 14px);
    line-height: 1.5;
    color: var(--fgColor-default, var(--color-fg-default));
    background: var(--body-bgColor);
    box-shadow: 0 0 100px var(--body-shadow-color);/* 增加 */
    border-radius: 10px;/* 增加 */
    transition: max-width 1s ease;/* 增加 */
}
/* 增加 */
@media (min-width: 1080px) {
    body {
        max-width: 1000px !important;
    }
}
```

</details>

## 博客滚动条样式

直接增加下面代码.

<details><summary>CSS Code</summary>

```CSS
::-webkit-scrollbar {
    width: 8px;
    height: 8px;
}

::-webkit-scrollbar-thumb {
    border-radius: 10px;
    background: #97d3ffa1;
}
::-webkit-scrollbar-thumb:hover {
    background: #81b5daa1;
}

/* Firefox */
html {
    scrollbar-color: #97d3ffa1 transparent;
    scrollbar-width: thin;
}
```

</details>

## \#header 样式

`#header`

> [!NOTE]
> 修改顶部为 flex 居中布局, 更加美观.
> 修改头像 hover 样式.

<details><summary>CSS Code</summary>

```CSS
/* 优化header样式 */
#header {
    flex-direction: column !important;
    align-items: center !important;
    gap: 10px;
    padding-bottom: 0 !important;
    margin-bottom: 24px !important
}

/* 优化头像样式 */
#header h1 {
    display: flex;
    flex-direction: column !important;
    align-items: center !important;
    gap: 15px
}

#header h1 a {
    margin: unset !important;
}

.avatar:hover {
    transform: scale(1.5) rotate(720deg) !important;
    box-shadow: 0 0 10px rgb(45 250 255 / 74%);
}
```

</details>

## \#header 图标样式

`.btn-invisible:hover, .btn-invisible.zeroclipboard-is-hover`

> [!NOTE]
> 图标增加阴影.
> svg 暗黑模式下颜色.
> 修改图标 hover 样式.

<details><summary>修改前</summary>

```CSS
.btn-invisible {
	color: var(--fgColor-accent, var(--color-accent-fg));
	background-color: rgba(0, 0, 0, 0);
	border: 0;
	border-radius: 6px;
	box-shadow: none
}

.btn-invisible:active,
.btn-invisible.selected,
.btn-invisible[aria-selected=true],
.btn-invisible.zeroclipboard-is-active {
	color: var(--fgColor-accent, var(--color-accent-fg));
	background: none;
	border-color: var(--button-default-borderColor-active, var(--color-btn-active-border));
	outline: 2px solid var(--focus-outlineColor, var(--color-accent-fg));
	outline-offset: -2px;
	box-shadow: none
}

.btn-invisible:active .btn-invisible.zeroclipboard-is-active {
	background-color: var(--button-default-bgColor-selected, var(--color-btn-selected-bg))
}
```

</details>
<details><summary>修改后</summary>

```CSS
[data-color-mode=light][data-light-theme=dark],
[data-color-mode=light][data-light-theme=dark]::selection,
[data-color-mode=dark][data-dark-theme=dark],
[data-color-mode=dark][data-dark-theme=dark]::selection {
    /* 增加 */
	--SideNav-bgColor: #00f0ff;
	--title-right-svgHovercolor:#ff7150;
	--header-btn-shadowColor:#00000045;
	--header-btn-shadowColor2:#9bdfff14;
}
:root {
    /* 增加 */
	--title-right-svgColor:#000;
	--title-right-svgHovercolor: #ff7804;
	--header-btn-shadowColor:#fbfbfb26;
	--header-btn-shadowColor2:#5f5f5f26;
}
.btn-invisible {
	color: var(--fgColor-accent, var(--color-accent-fg));
	background-color: rgba(0, 0, 0, 0);
	border: 0;
	border-radius: 6px;
	box-shadow: 6px 6px 14px 0 var(--header-btn-shadowColor), -7px -7px 16px 0 var(--header-btn-shadowColor2);
	transition: box-shadow .4s ease-in-out,filter .4s ease-in-out;
}
/* 图标颜色 */
.btn-invisible svg path{
	fill: var(--title-right-svgColor);
}
/* 图标hover颜色 */
.btn-invisible:hover svg path,
.btn-invisible.zeroclipboard-is-hover svg path{
	fill: var(--title-right-svgHovercolor);
}

.btn-invisible:active,
.btn-invisible.selected,
.btn-invisible[aria-selected=true],
.btn-invisible.zeroclipboard-is-active {
	box-shadow: 6px 6px 14px 0 var(--header-btn-shadowColor) inset, -7px -7px 12px 0 var(--header-btn-shadowColor2) inset;
}

.btn-invisible:active .btn-invisible.zeroclipboard-is-active {
	box-shadow: 6px 6px 14px 0 var(--header-btn-shadowColor) inset, -7px -7px 12px 0 var(--header-btn-shadowColor2) inset;
}
```

</details>

## 修改文章主页, 文章的列表样式

> [!NOTE]
> 还没想好要怎么改.

<details><summary>修改前</summary>

```CSS
.border {
	border: var(--borderWidth-thin, 1px) solid var(--borderColor-default, var(--color-border-default)) !important
}
```

</details>

<details><summary>修改后</summary>

```CSS
.border {
	border: var(--borderWidth-thin, 1px) solid var(--borderColor-default, var(--color-border-default)) !important
}
```

</details>

## 文章 \<blockquote> 标签样式

`.markdown-body blockquote`

> [!NOTE]
> 修改文字颜色, 适配 light & dark 主题.

<details><summary>修改前</summary>

```CSS
.markdown-body blockquote {
    padding: 0 1em;
    color: var(--fgColor-muted, var(--color-fg-muted));
    border-left: .25em solid var(--borderColor-default, var(--color-border-default))
}
```

</details>

<details><summary>修改后</summary>

```CSS
[data-color-mode=light][data-light-theme=dark],
[data-color-mode=light][data-light-theme=dark]::selection,
[data-color-mode=dark][data-dark-theme=dark],
[data-color-mode=dark][data-dark-theme=dark]::selection {
    /* 增加 */
    --markdown-blockquote-color: #ffffff8c;
    --markdown-blockquote-borderLeft-color: #bbbbbb8c;
}
:root {
    /* 增加 */
    --markdown-blockquote-color: #656d76;
    --markdown-blockquote-borderLeft-color: #d0d7de;
}
.markdown-body blockquote {
    padding: 0 1em;
    color: var(--markdown-blockquote-color);
    border-left: .25em solid var(--markdown-blockquote-borderLeft-color)
}
```

</details>

## 主页文章列表样式

`.SideNav-item:last-child`

> [!NOTE]
> 直接移除这个选择器的所有样式.

## 文章文字通用样式

`.markdown-body p, .markdown-body blockquote, .markdown-body ul, .markdown-body ol, .markdown-body dl, .markdown-body table, .markdown-body pre, .markdown-body details`

> [!NOTE]
> 修改行高为 1.75

<details><summary>修改前</summary>

```CSS
.markdown-body p,
.markdown-body blockquote,
.markdown-body ul,
.markdown-body ol,
.markdown-body dl,
.markdown-body table,
.markdown-body pre,
.markdown-body details {
	margin-top: 0;
	margin-bottom: 16px;
}
```

</details>

<details><summary>修改后</summary>

```CSS
.markdown-body p,
.markdown-body blockquote,
.markdown-body ul,
.markdown-body ol,
.markdown-body dl,
.markdown-body table,
.markdown-body pre,
.markdown-body details {
	margin-top: 0;
	margin-bottom: 16px;
	line-height: 1.75;/* 增加 */
}
```

</details>

## 文章标题通用样式

`.markdown-body h1, .markdown-body h2, .markdown-body h3, .markdown-body h4, .markdown-body h5, .markdown-body h6`

> [!NOTE]
> 删除左右 padding.
> 修改 margin-top 30px.

<details><summary>修改前</summary>

```CSS
.markdown-body h1,
.markdown-body h2,
.markdown-body h3,
.markdown-body h4,
.markdown-body h5,
.markdown-body h6 {
    padding: .22em;
    margin-top: 24px;
    margin-bottom: 16px;
    font-weight: var(--base-text-weight-semibold, 600);
    line-height: 1.25
}
```

</details>

<details><summary>修改后</summary>

```CSS
.markdown-body h1,
.markdown-body h2,
.markdown-body h3,
.markdown-body h4,
.markdown-body h5,
.markdown-body h6 {
    padding: .22em 0;
    margin-top: 30px;
    margin-bottom: 16px;
    font-weight: var(--base-text-weight-semibold, 600);
    line-height: 1.25
}
```

</details>

## 文章 \<h1> 标签样式

`.markdown-body h1`

> [!NOTE]
> 修改字体大小1.85em.
> 删除下 padding, 增加左 padding .22em.
> 增加 margin-top.
> 优化 light & dark 主题下的背景色.

<details><summary>修改前</summary>

```CSS
.markdown-body h1 {
    padding-bottom: .3em;
    font-size: 2em;
    border-bottom: 1px solid var(--borderColor-muted, var(--color-border-muted))
}
```

</details>
<details><summary>修改后</summary>

```CSS
[data-color-mode=light][data-light-theme=dark],
[data-color-mode=light][data-light-theme=dark]::selection,
[data-color-mode=dark][data-dark-theme=dark],
[data-color-mode=dark][data-dark-theme=dark]::selection {
    --markdown-h1-bgColor: #7dc2ff7a;/* 增加 */
}
:root {
    --markdown-h1-bgColor: #c8e5ff7a;/* 增加 */
}
.markdown-body h1 {
    padding-left: .22em;
    background: var(--markdown-h1-bgColor);/* 增加 */
    border-radius: 6px;/* 增加 */
    font-size: 1.85em;
    border-left: .25em solid #32c7dd;/* 增加 */
    padding-left: .25em;/* 增加 */
    margin-top: 42px;/* 增加 */
}
```

</details>

## 文章 \<h2> 标签样式

`.markdown-body h2`

> [!NOTE]
> 删除 padding-bottom.
> 增加下划线动画.
> 增加阴影样式

<details><summary>修改前</summary>

```CSS
.markdown-body h2 {
    padding-bottom: .3em;
    font-size: 1.5em;
    border-bottom: 1px solid var(--borderColor-muted, var(--color-border-muted))
}
```

</details>

<details><summary>修改后</summary>

```CSS
.markdown-body h2 {
    padding-bottom: .3em;
    font-size: 1.5em;
	box-shadow: rgb(41, 150, 186) 0px 9px 18px -15px;/* 增加 */
	display: inline-block;/* 增加 */
	border-radius: 6px;/* 增加 */
}
```

</details>

## 文章 \<img> 标签样式

`.markdown-body img`

> [!NOTE]
> 优化 light & dark 主题下的背景色.
> 增加 hover 动画.

<details><summary>修改前</summary>

```CSS
.markdown-body img {
    max-width: 100%;
    box-sizing: content-box;
    background-color: var(--bgColor-default, var(--color-canvas-default))
}
```

</details>

<details><summary>修改后</summary>

```CSS
/* 增加 */
.markdown-body p {
    position: relative;
    overflow: visible;
    clip-path: inset(0);
    -webkit-clip-path: inset(0);
}
.markdown-body img {
    max-width: 100%;
    box-sizing: content-box;
    transition: transform 0.3s ease, clip-path 0.3s ease;/* 增加 */
    -webkit-transition: -webkit-transform 0.3s ease, -webkit-clip-path 0.3s ease;/* 增加 */
}
/* 增加 */
.markdown-body img:hover {
    transform: scale(1.01);
    clip-path: inset(-4%);
    cursor: zoom-in;
}
```

</details>

## 文章 \<code> 标签样式

`.markdown-body code, .markdown-body tt`

> [!NOTE]
> 优化 light & dark 主题下的背景色.

<details><summary>修改前</summary>

```CSS
.markdown-body code,
.markdown-body tt {
    background-color: var(--bgColor-neutral-muted, var(--color-neutral-muted));
}
```

</details>

<details><summary>修改后</summary>

```CSS
[data-color-mode=light][data-light-theme=dark],
[data-color-mode=light][data-light-theme=dark]::selection,
[data-color-mode=dark][data-dark-theme=dark],
[data-color-mode=dark][data-dark-theme=dark]::selection {
    --markdown-code-bgColor: #3bf6ff52;/* 增加 */
}
:root {
    --markdown-code-bgColor: #4d4d4d38;/* 增加 */
}
.markdown-body code,
.markdown-body tt {
    background-color: var(--markdown-code-bgColor);
}
```

</details>

## 文章代码块样式

`.markdown-body .highlight pre, .markdown-body pre`

> [!NOTE]
> 优化 light & dark 主题下的背景色.
> 增加内阴影

<details><summary>修改前</summary>

```CSS
.markdown-body .highlight pre,.markdown-body pre {
    padding: 16px;
    overflow: auto;
    font-size: 85%;
    line-height: 1.45;
    color: var(--fgColor-default, var(--color-fg-default));
    background-color: var(--bgColor-muted, var(--color-canvas-subtle));
    border-radius: 6px
}
```

</details>

<details><summary>修改后</summary>

```CSS
[data-color-mode=light][data-light-theme=dark],
[data-color-mode=light][data-light-theme=dark]::selection,
[data-color-mode=dark][data-dark-theme=dark],
[data-color-mode=dark][data-dark-theme=dark]::selection {
    --markdown-pre-bgColor: #27282d;/* 增加 */
	--markdown-pre-shadowColor: #00000026;/* 增加 */
}
:root {
    --markdown-pre-bgColor: #f6f8fa;/* 增加 */
	--markdown-pre-shadowColor: #5f5f5f26;/* 增加 */
}
.markdown-body .highlight pre, .markdown-body pre {
	padding: 16px;
	overflow: auto;
	font-size: 85%;
	line-height: 1.45;
	color: var(--fgColor-default, var(--color-fg-default));
	border-radius: 6px;
	background-color: var(--markdown-pre-bgColor);/* 增加 */
	box-shadow: 4px 5px 14px 0 var(--markdown-pre-shadowColor) inset;/* 增加 */
}
```

</details>

## 文章 diff 代码块样式

> [!NOTE]
> 默认的效果可以双击复制到+和-号, 通过 CSS 控制使其无法被选中复制.
> 直接增加下面代码.

<details><summary>CSS Code</summary>

```CSS
.pl-mi1 {
	user-select: text;
}

.pl-mi1>span {
	user-select: none;
}

.pl-md {
	user-select: text;
}

.pl-md>span {
	user-select: none;
}
```

</details>

效果图:

![image](https://github.com/user-attachments/assets/f3eb7940-ca2b-4952-8fb4-e05a7acc84bd)

## 文章一键复制代码按钮样式

> [!NOTE]
> 给按钮增加 hover 动画, 使其显示&隐藏一键复制按钮.
> 直接增加下面代码.

<details><summary>CSS Code</summary>

```CSS
/* 一键复制hover出入动画 */
.clipboard-container {
    opacity: 0;
    visibility: hidden;
    pointer-events: none;
    transition: opacity 0.3s ease, visibility 0s 0.3s;
    -webkit-transition: opacity 0.3s ease, visibility 0s 0.3s
}

.highlight:hover .clipboard-container {
    opacity: 1;
    visibility: visible;
    pointer-events: auto;
    transition: opacity 0.3s ease, visibility 0s 0s;
    -webkit-transition: opacity 0.3s ease, visibility 0s 0s
}
```

</details>

## 文章 \<a> 标签样式

`a`

> [!NOTE]
> 优化 light & dark 主题下的背景色.
> 去掉原下划线, 增加下划线动画.

<details><summary>修改前</summary>

```CSS
[data-color-mode=light][data-light-theme=dark],
[data-color-mode=light][data-light-theme=dark]::selection,
[data-color-mode=dark][data-dark-theme=dark],
[data-color-mode=dark][data-dark-theme=dark]::selection {
    --color-accent-fg: #2f81f7;
}
/* 这条在12345行左右出现 */
a {
    background-color: rgba(0, 0, 0, 0)
}
```

</details>

<details><summary>修改后</summary>

```CSS
[data-color-mode=light][data-light-theme=dark],
[data-color-mode=light][data-light-theme=dark]::selection,
[data-color-mode=dark][data-dark-theme=dark],
[data-color-mode=dark][data-dark-theme=dark]::selection {
    --color-accent-fg: #20d4ff;
}
/* 
这条在12345行左右出现
修改为下面内容
*/
a {
    background: linear-gradient(#90d1ff, #90d1ff) no-repeat left bottom;
    background-size: 0 2px;
    transition: all 0.25s ease;
    -webkit-transition: all 0.25s ease;
}
/* 增加 */
.markdown-body a:hover {
    background-size: 100% 2px;
}
```

</details>

## 文章 \<td> 最后的子元素样式

`.markdown-body table td>:last-child`

> [!NOTE]
> 修改下标基线对齐位置.

<details><summary>修改前</summary>

```CSS
.markdown-body table td>:last-child {
	margin-bottom: 0
}
```

</details>

<details><summary>修改后</summary>

```CSS
.markdown-body table td>:last-child {
	margin-bottom: 0;
	vertical-align: sub
}
```

</details>

效果图:

![image](https://github.com/user-attachments/assets/73cdc397-e4c8-45c8-8ecf-02f32af9fd63)

# 通过 Gmeek 仓库 DIY 博客

为什么这样做? `Gmeek-spoilertxt="自娱自乐.~~"`

## Fork Gmeek 仓库

仓库地址👉 https://github.com/Meekdai/Gmeek

![image](https://github.com/user-attachments/assets/8794d347-3524-4709-a6f1-fd74c607fc22)

fork 之后, 转到搭建博客的 github 源码,

打开`.github/workflows/Gmeek.yml`文件, 修改构建博客仓库的地址为你自己的仓库地址

![image](https://github.com/user-attachments/assets/20d1b3ac-c0fc-44ad-a937-3828b6875a8f)

打开`config.json`文件, 修改右边字段值为main`"GMEEK_VERSION":"main"`

> [!NOTE]
> 如果值是`last`的话, Actions 会失败, 因为默认值`last`是靠模板仓库的 tag 来构建的, 改成 main 就不会构建失败.
> ~~创建新的 tag 也可以, 但是挺麻烦.~~

## 修改 Actions 定时任务时间

原本为每天 UTC 时间 16 点定时 Actions.

```yaml
        - cron: "0 16 * * *"
```

改成每周 UTC 时间 18 点定时 Actions.

```yaml
        - cron: "0 18 * * 0"
```

## 修改网站下方的文字

打开`Gmeek.py`

下图文字直接修改即可, 不同语言的按需修改.

![image](https://github.com/user-attachments/assets/c0f4bca8-174d-4044-a654-12e6322cca9b)

## 修改默认 primer.css 链接

打开`Gmeek.py`

![image](https://github.com/user-attachments/assets/fd72d93f-5015-44d9-ac79-58dff7e3c116)

这里我直接写改成我存放的链接, 并使用 tag 控制版本.

## 修改页面头部样式

### 打开 base.html 文件

> [!Important]
> base 这个模板文件里增加的代码可以应用到所有页面, 优先级很高.

1. **增加所需的样式.**

> 文章头部背景色.
> 打字效果动画.
> 动画(已引用的地方:#header 打字机光标, #header 图标渐显).
> 分离图标的`#functionBtn`样式. 

```CSS
:root{--functionBtnFlex-bgColor:#ffffff61;}
[data-color-mode=light][data-light-theme=dark],[data-color-mode=light][data-light-theme=dark]::selection,[data-color-mode=dark][data-dark-theme=dark],[data-color-mode=dark][data-dark-theme=dark]::selection{--functionBtnFlex-bgColor:#ffffff00;}

@keyframes fadeIn{0%{opacity:0}100%{opacity:1}}@keyframes blink{50%{opacity:0}100%{opacity:1}}@-webkit-keyframes fadeIn{0%{opacity:0}100%{opacity:1}}@-webkit-keyframes blink{50%{opacity:0}100%{opacity:1}}

#functionBtn{display:flex;justify-content:center;margin:20px 0;gap:20px;transition: transform 0.3s ease-in-out;}
#functionBtn a, #functionBtn div{padding:14px 16px;animation:fadeIn .7s ease-in 0s forwards;}
#functionBtn.Btn-flex{position:fixed;margin:0;padding:20px 0;top:-100px;left:0;width:100%;min-width:500px;background-color:var(--functionBtnFlex-bgColor);backdrop-filter:blur(30px);box-shadow:#00000078 0 9px 18px -15px;z-index:100;animation:fadeIn.2s ease-in 0s forwards;transition:top 0.3s ease-in-out}
```

2. **定位`#header`, 修改样式.**

> 使用类名区分首页和文章页.

```Diff
+#header .homepage-header{display:flex;flex-direction:column;align-items:center;gap:10px;margin-bottom:24px;}
👆
-#header{display:flex;padding-bottom:8px;border-bottom: 1px solid var(--borderColor-muted, var(--color-border-muted));margin-bottom: 16px;}
```

3. **头部图标样式.**

> 增加 CSS, `fadeIn`动画已在上文第1步骤添加过.

```CSS
.title-right{display:flex;gap:25px;animation:fadeIn 1.2s ease-in 0s forwards;}
```

### 打开 post.html 文件

> [!Important]
> post 这个模板文件里增加的代码可以应用到所有文章页面.

1. **定位`.postTitle`, 修改样式**

> 修改标题文字居中显示.
> after 是光标, blink 是光标动画.

```Diff
+.postTitle{margin:0 auto;font-size:40px;font-weight:bold;}
+.postTitle::after{content:'|';animation:blink 1s infinite;font-family:fantasy;font-weight:normal;vertical-align:text-top;}
+.no-blink::after{animation:none;}
👆
-.postTitle{margin: auto 0;font-size:40px;font-weight:bold;}
```

3. **定位样式`#functionBtn .circle`, 删除`margin-right:8px;`**

```Diff
+#functionBtn .circle{padding: 14px 16px;}
👆
-#functionBtn .circle{padding: 14px 16px;margin-right:8px;}
```

4. **头部文字和图标样式.**

> 文章标题选择器增加淡入动画.
> 给`#functionBtn`增加子元素 DIV 的样式, 因为我增加了一个 DIV 元素显示文章目录按钮图标, 这里刚好需要 CSS 控制它.

```CSS
#header.article-header{animation:fadeIn .7s ease-in 0s forwards;}
#functionBtn a, #functionBtn div{padding:14px 16px;}
```

5. **body响应**

定位`@media (max-width:600px) {`, 给 body 增加最小宽度500px: `min-width:500px;`

6. **分离header文字以及图标**

> 需要把`.title-right`这个类名全部重命名为`#functionBtn`
> 增加文章目录按钮
> 增加文章浏览进度按钮

<details><summary>修改前</summary>

```html
{% block header %}
<h1 class="postTitle">{{ blogBase['postTitle'] }}</h1>
<div class="title-right">
    <a href="{{ blogBase['homeUrl'] }}" id="buttonHome" class="btn btn-invisible circle" title="{{ i18n['home'] }}">
        <svg class="octicon" width="16" height="16">
            <path id="pathHome" fill-rule="evenodd"></path>
        </svg>
    </a>
    {% if blogBase['showPostSource']==1 %}
    <a href="{{ blogBase['postSourceUrl'] }}" target="_blank" class="btn btn-invisible circle" title="Issue">
        <svg class="octicon" width="16" height="16">
            <path id="pathIssue" fill-rule="evenodd"></path>
        </svg>
    </a>
    {% endif %}

    <a class="btn btn-invisible circle" onclick="modeSwitch();" title="{{ i18n['switchTheme'] }}" {%- if blogBase['themeMode']=='fix' -%}style="display:none;"{%- endif -%}>
        <svg class="octicon" width="16" height="16" >
            <path id="themeSwitch" fill-rule="evenodd"></path>
        </svg>
    </a>

</div>
{% endblock %}
```
</details>

<details><summary>修改后</summary>

```html
{% block header %}
<h1 class="postTitle">{{ blogBase['postTitle'] }}</h1>
{% endblock %}

{% block functionBtn %}
<a href="{{ blogBase['homeUrl'] }}" id="buttonHome" class="btn btn-invisible circle" title="{{ i18n['home'] }}">
	<svg class="octicon" width="16" height="16"><path id="pathHome" fill-rule="evenodd"></path></svg>
</a>
{% if blogBase['showPostSource']==1 %}
<a href="{{ blogBase['postSourceUrl'] }}" target="_blank" class="btn btn-invisible circle" title="Issue">
	<svg class="octicon" width="16" height="16"><path id="pathIssue" fill-rule="evenodd"></path></svg>
</a>
{% endif %}

<a class="btn btn-invisible circle" onclick="modeSwitch();" title="{{ i18n['switchTheme'] }}" {%- if blogBase['themeMode']=='fix' -%}style="display:none;"{%- endif -%}>
	<svg class="octicon" width="16" height="16" ><path id="themeSwitch" fill-rule="evenodd"></path></svg>
</a>

<a class="ArticleTOC btn btn-invisible circle" title="文章目录">
	<svg class="octicon" width="16" height="16"><path></path></svg>
</a>
{% endblock %}
```

</details>

定位`document.getElementById("pathHome").setAttribute("d",IconList["home"]);`, 在下面一行增加js.

> 暂时还不知道如何通过变量增加 path 的路径信息, 只能直接模仿原先的增加方式上, 直接写路径.

```Javascript
document.getElementById("ArticleTOC").setAttribute("d","M1 2.75A.75.75 0 0 1 1.75 2h12.5a.75.75 0 0 1 0 1.5H1.75A.75.75 0 0 1 1 2.75Zm0 5A.75.75 0 0 1 1.75 7h12.5a.75.75 0 0 1 0 1.5H1.75A.75.75 0 0 1 1 7.75ZM1.75 12h12.5a.75.75 0 0 1 0 1.5H1.75a.75.75 0 0 1 0-1.5Z");
```

7. **添加自定义 JS 代码.**

> 添加打字效果.
> 添加滚动切换显示顶部按钮导航.

定位`<script>`标签, 在里面增加 JS 代码:

> [!NOTE]
> `document.addEventListener("DOMContentLoaded", () => {`这个监听不止可写当前功能, 还可写其它功能的代码进去.
> 实际应用场景我把这块的代码都压缩合并了.

<details><summary>JavaScript</summary>

```Javascript
// 获取 .postTitle 元素的文本内容存储后清空
const postTitle = document.querySelector('.postTitle');
const textContent = postTitle.textContent;
postTitle.textContent = '';

// 定义逐字显示文本的函数, 末尾的数值代表每次输入字符的速度(毫秒)
let idx = 0;
const writeTimer = setInterval(() => {
    postTitle.textContent = textContent.slice(0, idx++);
    if (idx > textContent.length) {
        clearInterval(writeTimer);
        postTitle.classList.remove('no-blink');
    }
}, 80);

postTitle.classList.add('no-blink');

document.addEventListener('DOMContentLoaded', () => {
    // 创建检查按钮, 插入到#functionBtn div的后面
    const checkBtn = document.createElement('div');
    checkBtn.id = 'checkBtn';
    const functionBtn = document.getElementById('functionBtn');
    functionBtn.insertAdjacentElement('afterend', checkBtn);

    // 用 IntersectionObserver 观察 checkBtn 这个div的可见性
    const observer = new IntersectionObserver(entries => {
        entries.forEach(entry => {
            const isIntersecting = entry.isIntersecting;
            functionBtn.classList.toggle('Btn-flex', !isIntersecting);
            functionBtn.style.top = isIntersecting ? '0' : '-100px';
        });
    }, { rootMargin: '300px 0px 0px 0px', threshold: 0 });
    observer.observe(checkBtn);

    let startY = 0;

    // 通用滚动处理函数
    const handleScroll = deltaY => {
        functionBtn.style.top = deltaY > 0 ? '-100px' : '0';
    };

// 监听触摸和滚轮事件
document.addEventListener('touchstart', e => startY = e.touches[0].clientY);
document.addEventListener('touchmove', e => handleScroll(e.touches[0].clientY - startY));
document.addEventListener('wheel', e => handleScroll(e.deltaY));
});
```

</details>


### 打开 plist.html 文件

> [!Important]
> plist 这个模板文件里增加的代码可以应用到博客首页.

1. **增加样式.**

```CSS
.title-left{display:flex;flex-direction:column;align-items:center;gap:20px;}
```

2. **定位样式`.title-left`, 直接删除相关的所有样式**

3. **定位`.avatar:hover`, 修改样式.**

```CSS
.avatar:hover{transform:scale(1.5) rotate(720deg);box-shadow:0 0 10px #2dfaffbd;}
```

4. **分离#header的文字以及图标.**

<details><summary>修改前</summary>

```html
{% block header %}
<div class="title-left">
    <img src="{{ blogBase['avatarUrl'] }}" class="avatar circle" id="avatarImg" alt="avatar">
    {%- if blogBase['displayTitle']=='Meekdai' -%}
    <a class="blogTitle" href="https://meekdai.com"><span style="font-size:0;">M</span>eekdai</a>
    {% else -%}
    <a class="blogTitle">{{ blogBase['displayTitle'] }}</a>
    {%- endif -%}
</div>
<div class="title-right">
    <a href="{{ blogBase['homeUrl'] }}/tag.html" id="buttonSearch" class="btn btn-invisible circle" title="{{ i18n['Search'] }}">
        <svg class="octicon" width="16" height="16" >
            <path id="pathSearch" fill-rule="evenodd"></path>
        </svg>
    </a>
    {% for key, value in blogBase['exlink'].items() -%}
    <a href="{{ value }}" class="btn btn-invisible circle" title="{{ key }}" target="_blank">
        <svg class="octicon" width="16" height="16" >
            <path id="{{ key }}" fill-rule="evenodd"></path>
        </svg>
    </a>
    {%- endfor %}
    {% for num in blogBase['singeListJson'] -%}
    <a href="{{ blogBase['homeUrl'] }}/{{ blogBase['singeListJson'][num]['labels'][0] }}.html" class="btn btn-invisible circle" title="{{ blogBase['singeListJson'][num]['postTitle'] }}">
        <svg class="octicon" width="16" height="16" >
            <path id="{{ blogBase['singeListJson'][num]['postTitle'] }}" fill-rule="evenodd"></path>
        </svg>
    </a>
    {%- endfor %}
    <a href="{{ blogBase['homeUrl'] }}/rss.xml" target="_blank" id="buttonRSS" class="btn btn-invisible circle" title="RSS">
        <svg class="octicon" width="16" height="16" >
            <path id="pathRSS" fill-rule="evenodd"></path>
        </svg>
    </a>
    <a class="btn btn-invisible circle" onclick="modeSwitch()" title="{{ i18n['switchTheme'] }}" {%- if blogBase['themeMode']=='fix' -%}style="display:none;"{%- endif -%}>
        <svg class="octicon" width="16" height="16" >
            <path id="themeSwitch" fill-rule="evenodd"></path>
        </svg>
    </a>
</div>
{% endblock %}
```

</details>

<details><summary>修改后</summary>

```html
{% block header %}
<div class="title-left">
    <img src="{{ blogBase['avatarUrl'] }}" class="avatar circle" id="avatarImg" alt="avatar">
    {%- if blogBase['displayTitle']=='Meekdai' -%}
    <a class="blogTitle" href="https://meekdai.com"><span style="font-size:0;">M</span>eekdai</a>
    {% else -%}
    <a class="blogTitle">{{ blogBase['displayTitle'] }}</a>
    {%- endif -%}
</div>
{% endblock %}

{% block functionBtn %}
<a href="{{ blogBase['homeUrl'] }}/tag.html" id="buttonSearch" class="btn btn-invisible circle" title="{{ i18n['Search'] }}">
	<svg class="octicon" width="16" height="16" >
		<path id="pathSearch" fill-rule="evenodd"></path>
	</svg>
</a>
{% for key, value in blogBase['exlink'].items() -%}
<a href="{{ value }}" class="btn btn-invisible circle" title="{{ key }}" target="_blank">
	<svg class="octicon" width="16" height="16" >
		<path id="{{ key }}" fill-rule="evenodd"></path>
	</svg>
</a>
{%- endfor %}
{% for num in blogBase['singeListJson'] -%}
<a href="{{ blogBase['homeUrl'] }}/{{ blogBase['singeListJson'][num]['labels'][0] }}.html" class="btn btn-invisible circle" title="{{ blogBase['singeListJson'][num]['postTitle'] }}">
	<svg class="octicon" width="16" height="16" >
		<path id="{{ blogBase['singeListJson'][num]['postTitle'] }}" fill-rule="evenodd"></path>
	</svg>
</a>
{%- endfor %}
<a href="{{ blogBase['homeUrl'] }}/rss.xml" target="_blank" id="buttonRSS" class="btn btn-invisible circle" title="RSS">
	<svg class="octicon" width="16" height="16" >
		<path id="pathRSS" fill-rule="evenodd"></path>
	</svg>
</a>
<a class="btn btn-invisible circle" onclick="modeSwitch()" title="{{ i18n['switchTheme'] }}" {%- if blogBase['themeMode']=='fix' -%}style="display:none;"{%- endif -%}>
	<svg class="octicon" width="16" height="16" >
		<path id="themeSwitch" fill-rule="evenodd"></path>
	</svg>
</a>
{% endblock %}
```

</details>

### 打开 tag.html 文件

> [!Important]
> tag 这个模板文件里增加的代码可以应用到搜索页.

1. **打开`tag.html`修改样式, 用了 Diff 代码块, 看着改吧.**

```Diff
+.title-right{display:flex;align-items:center;flex-direction:column;}
+.title-right .circle{padding:14px 16px;}
👆
-.title-right{display:flex;margin:auto 0 0 auto;}
-.title-right .circle{padding: 14px 16px;margin-right:8px;}
```

2. **分离搜索框以及图标.**

<details><summary>修改前</summary>

```html
{% block header %}
<span class="tagTitle"><span>Loading</span><span class="AnimatedEllipsis"></span></span>
<div class="title-right">
    <div class="subnav-search">
        <input type="search" class="form-control subnav-search-input float-left" aria-label="Search site" value="" style="height:32px;">
        <button class="btn float-left" type="submit" onclick="javascript:searchShow()">{{ i18n['Search'] }}</button>
        <svg class="subnav-search-icon octicon octicon-search" width="16" height="16" viewBox="0 0 16 16" aria-hidden="true">
            <path id="searchSVG" fill-rule="evenodd"></path>
        </svg>
    </div>
    <a href="{{ blogBase['homeUrl'] }}" id="buttonHome" class="btn btn-invisible circle" title="{{ i18n['home'] }}">
        <svg class="octicon" width="16" height="16">
            <path id="pathHome" fill-rule="evenodd"></path>
        </svg>
    </a>
    <a class="btn btn-invisible circle" onclick="modeSwitch()" title="{{ i18n['switchTheme'] }}" {%- if blogBase['themeMode']=='fix' -%}style="display:none;"{%- endif -%}>
        <svg class="octicon" width="16" height="16" >
            <path id="themeSwitch" fill-rule="evenodd"></path>
        </svg>
    </a>
</div>
{% endblock %}
```

</details>

<details><summary>修改后</summary>

```html
{% block header %}
<span class="tagTitle"><span>Loading</span><span class="AnimatedEllipsis"></span></span>
<div class="subnav-search">
	<input type="search" class="form-control subnav-search-input float-left" aria-label="Search site" value="" style="height:32px;">
	<button class="btn float-left" type="submit" onclick="javascript:searchShow()">{{ i18n['Search'] }}</button>
	<svg class="subnav-search-icon octicon octicon-search" width="16" height="16" viewBox="0 0 16 16" aria-hidden="true">
		<path id="searchSVG" fill-rule="evenodd"></path>
	</svg>
</div>
{% endblock %}

{% block functionBtn %}
<a href="{{ blogBase['homeUrl'] }}" id="buttonHome" class="btn btn-invisible circle" title="{{ i18n['home'] }}">
	<svg class="octicon" width="16" height="16">
		<path id="pathHome" fill-rule="evenodd"></path>
	</svg>
</a>
<a class="btn btn-invisible circle" onclick="modeSwitch()" title="{{ i18n['switchTheme'] }}" {%- if blogBase['themeMode']=='fix' -%}style="display:none;"{%- endif -%}>
	<svg class="octicon" width="16" height="16" >
		<path id="themeSwitch" fill-rule="evenodd"></path>
	</svg>
</a>
{% endblock %}
```

</details>

#### 修改搜索框样式

1. **定位`.subnav-search`类名. 直接删除这个样式**

2. **定位`.subnav-search-input`类名, 修改以下内容**

```Diff
+.subnav-search-input{width:160px;}
+.subnav-search button{padding:5px 8px;}
👆
-.subnav-search-input{width:160px;border-top-right-radius:0px;border-bottom-right-radius:0px;}
-.subnav-search button{padding:5px 8px;border-top-left-radius:0px;border-bottom-left-radius:0px;}
```

3. 打开`primer.css`, 修改样式

定位`.subnav-search {`, 删除了margin.

```Diff
+.subnav-search {position: relative;s}
👆
-.subnav-search {position: relative;margin-left: 12px}
```

> [!NOTE]
> 到这里我的自定义 header 就修改完成了, 其它的样式可到 primer.css 里修改.

## 修改[警报强调信息]样式

1. **增加圆角**

打开`Gmeek.py`

定位代码`<style>.markdown-alert{`, 增加圆角6px.

`border-radius:6px;`

`Gmeek-imgbox="https://i1.img2ipfs.com/ipfs/QmRCXZrjvmUajTL5odC4d5oJyJwx8mrNSwDzGgTs3yuDMw"`

2. **优化行高显示**

定位`line-height:1;`, 直接删除这个属性.

**效果图:**

![image](https://github.com/user-attachments/assets/db205027-0615-4456-bca3-b33856372283)

# 优化任务列表样式

具体问题看[#202](https://github.com/Meekdai/Gmeek/issues/202)

打开`Gmeek.py`, 定位`postBase=self.blogBase.copy()`, 在它的下面增加如下代码:

```python
        if '<ul class="contains-task-list">' in post_body:
            issue["style"]=issue["style"]+'<style>.contains-task-list{padding-left:0.9em !important;list-style:none}</style>'
```


## 页面底部文字增加图标动画

爱心图标动画.

打开`footer.html`

在`<span id="runday">`前面插入下面一行 SVG 图标.

```html
<svg viewBox="0 0 1024 1024" xmlns="http://www.w3.org/2000/svg" style="margin-right: 4px;height:18px;vertical-align: bottom;fill: #ff5a5a;"class="animate_heartBeatScale"><path d="M1017.152 426.592a263.296 263.296 0 0 0-502.304-133.92 263.328 263.328 0 0 0-502.304 133.92s5.152 259.264 505.536 520.096c500.32-260.832 499.072-520.096 499.072-520.096zM282.016 194.976a43.2 43.2 0 1 1 .096 86.4 43.2 43.2 0 0 1-.096-86.4zm-135.04 323.232a45.12 45.12 0 0 1-55.488-31.328 289.472 289.472 0 0 1-10.816-66.592C76.64 313.824 142.24 261.472 145.504 258.88a45.024 45.024 0 0 1 63.2 8.032c15.168 19.488 11.744 47.36-7.328 62.72-2.336 1.952-30.784 27.52-30.592 82.24.096 14.752 2.208 31.616 7.488 50.784a45.12 45.12 0 0 1-31.296 55.552z"/></svg>
```

打开`primer.css`, 直接增加动画 CSS 代码.

<details><summary>CSS Code</summary>

```CSS
@keyframes heartBeatScale  {
    0% {
        -webkit-transform: scale(1);
        transform: scale(1)
    }

    14% {
        -webkit-transform: scale(1.3);
        transform: scale(1.3)
    }

    28% {
        -webkit-transform: scale(1);
        transform: scale(1)
    }

    42% {
        -webkit-transform: scale(1.3);
        transform: scale(1.3)
    }

    70% {
        -webkit-transform: scale(1);
        transform: scale(1)
    }
}
@keyframes heartBeatColor {
    0%, 28%, 70%, 100% {
        fill: #ff5a5a; /* 初始颜色 */
    }
    14%, 42% {
        fill: red; /* 放大时颜色变化 */
    }
}

.animate_heartBeatScale {
    animation: heartBeatScale 1.3s infinite ease-in-out, heartBeatColor 1.3s infinite ease-in-out;
    -webkit-animation: heartBeatScale 1.3s infinite ease-in-out, heartBeatColor 1.3s infinite ease-in-out;
}
```

</details>

转到页脚查看实际效果👉 [点我](#footer2)

# 使用 Gmeek-html, 给博客插入图片, 防止链接自动转换

Github 在 issues 插入的图片也会自动转换为 Github 的地址.

为了文章的多样性, 在 Gmeek 的`v2.19`版本中添加了支持 html 标签的功能.

示例代码:

```html
`Gmeek-html<img src="https://i0.img2ipfs.com/ipfs/QmbAZqtwu2G9vXrJ8oC7ixvKh4tY8uL8NvPA9zAxDqWFPq">`
```

效果图:

`Gmeek-html<img src="https://i0.img2ipfs.com/ipfs/QmbAZqtwu2G9vXrJ8oC7ixvKh4tY8uL8NvPA9zAxDqWFPq">`

> [!Important]
> 如果在文章中含有代码块标签并且内容为 Gmeek-html, Action 那边会进行转换导致显示错误, 详情看[#201](https://github.com/Meekdai/Gmeek/issues/201)
> `gmeek-html`换成小写就不会被匹配到.

# 优化 Gmeek-html, 标签转换匹配

打开`Gmeek.py`, 定位字符串`gmeek-html`

替换成下面的代码:

```python
if '<code class="notranslate">Gmeek-html' in post_body:
            post_body = re.sub(r'<code class="notranslate">Gmeek-html(&lt;.*?&gt;)</code>', lambda match: html.unescape(match.group(1)), post_body, flags=re.DOTALL)
```

原先匹配的内容为:`<code class="notranslate">Gmeek-html(.*?)</code>`,

这种情况下, 如果在 html 中含有行内代码块标签并且内容含有 Gmeek-html, 会导致转换文章内容时出现显示错误,

更改后缩小了匹配范围, 可直接用行内代码块👉`Gmeek-html`让其在文章内正常显示.

# 增加图片转换, 并适配图片懒加载

打开`Gmeek.py`, 定位字符串`gmeek-html`

在附近任意行增加代码:

```python
        if '<a' in post_body:
            post_body = re.sub(r'<p>\s*<a[^>]*?href="([^"]+)"[^>]*?><img[^>]*?src="\1"[^>]*?></a>\s*</p>', lambda match: f'<div class="ImgLazyLoad-circle"></div>\n<img data-fancybox="gallery" img-src="{match.group(1)}">', post_body, flags=re.DOTALL)
```

- **使用演示**

在 markdown 上传图片

通过 Actions 转换后实际效果如下, html 里面图片标签会增加 fancybox 所需的`data-fancybox="gallery"`属性.

这样优化后可以在 Github issue 的 Preview 里面直接预览图片, 同时还能防备图床问题导致的图片丢失(`Gmeek-spoilerText="Github, 稳!"`)

# 添加 Gmeek-spoilertxt - 文字防剧透模糊效果

**默认模糊效果, 反复点击可反复显示或隐藏.**

## 打开 Gmeek.py

1. **增加匹配内容:**

```python
        if '<code class="notranslate">Gmeek-spoilertxt' in post_body: 
            post_body = re.sub(r'<code class="notranslate">Gmeek-spoilertxt="([^"]+)"</code>', lambda match: f'<span class="spoilerText">{match.group(1)}</span>', post_body, flags=re.DOTALL)
```

2. **实际转化后的标签如下:**

```html
<p>测试剧透 <span class="spoilerText">剧透内容</span></p>
```

## 打开 post.html

1. **增加 CSS 样式:**

```CSS
.spoilerText{filter:blur(5px);-webkit-filter:blur(5px);cursor:pointer;transition:filter .3s ease}
.spoilerText.clear{filter: none;}
```

2. **定位`<script>`标签, 在里面增加 JS 代码:**

> [!NOTE]
> `document.addEventListener('DOMContentLoaded', () => {`这个监听可以写其它功能的代码进去, 不止剧透效果.

<details><summary>Javascript Code</summary>

```Javascript
document.addEventListener('DOMContentLoaded', () => {
	const spoilers = document.querySelectorAll(".spoilerText");
	spoilers.length && spoilers.forEach(el => el.onclick = () => el.classList.toggle("clear"));
});
```

</details>

3. **markdown 输入:**

```
测试剧透👉`Gmeek-spoilertxt="666666"`
```

4. **实际展示:**

测试剧透👉`Gmeek-spoilertxt="666666"`.

# 添加自定义单篇文章代码

```html
<span id="busuanzi">
:heart:感谢第<span></span>小伙伴的<span></span>次访问关于页面.
</span>

<!-- ##{"script":"<script>document.getElementById('user-content-busuanzi').id='busuanzi_container_site_uv';busuanzi=document.getElementById('busuanzi_container_site_uv');busuanzi.style.display='none';busuanzi.childNodes[1].id='busuanzi_value_site_uv';busuanzi.childNodes[3].id='busuanzi_value_site_pv';</script><script async src='//busuanzi.ibruce.info/busuanzi/2.3/busuanzi.pure.mini.js'></script>","style":"<style>#busuanzi_value_site_uv{color:red}#busuanzi_value_site_pv{color:red}</style>"}## -->
```

# 自动展开评论区

打开 post.html,

1. **定位`onclick="openComments()"`, 在 html 结构里删除这个点击绑定.**

2. **定位`function openComments(){`这个函数, 在函数结束外边尾行增加`openComments();`**

# icon 图标

写着备用.

1. **打开 Gmeek.py**

[Primer svg](https://primer.style/foundations/icons/#16px)

定位`IconBase={`

在这个 json 格式里面增加图标路径数值.

```json

    "ThreeBars":"M1 2.75A.75.75 0 0 1 1.75 2h12.5a.75.75 0 0 1 0 1.5H1.75A.75.75 0 0 1 1 2.75Zm0 5A.75.75 0 0 1 1.75 7h12.5a.75.75 0 0 1 0 1.5H1.75A.75.75 0 0 1 1 7.75ZM1.75 12h12.5a.75.75 0 0 1 0 1.5H1.75a.75.75 0 0 1 0-1.5Z",
    "MoveTop":"M3 2.25a.75.75 0 0 1 .75-.75h8.5a.75.75 0 0 1 0 1.5h-8.5A.75.75 0 0 1 3 2.25Zm5.53 2.97 3.75 3.75a.749.749 0 1 1-1.06 1.06L8.75 7.561v6.689a.75.75 0 0 1-1.5 0V7.561L4.78 10.03a.749.749 0 1 1-1.06-1.06l3.75-3.75a.749.749 0 0 1 1.06 0Z",
    "MoveBottom":"M7.47 10.78a.749.749 0 0 0 1.06 0l3.75-3.75a.749.749 0 1 0-1.06-1.06L8.75 8.439V1.75a.75.75 0 0 0-1.5 0v6.689L4.78 5.97a.749.749 0 1 0-1.06 1.06l3.75 3.75ZM3.75 13a.75.75 0 0 0 0 1.5h8.5a.75.75 0 0 0 0-1.5h-8.5Z"
```

# Issues Label 备份

| Label Name | Color | 效果
|-|-|-
| 网站 | #218155 | `Gmeek-imgbox="https://img.shields.io/static/v1?label=&message=网站&color=218155"`
| 日常 | #008672 | `Gmeek-imgbox="https://img.shields.io/static/v1?label=&message=日常&color=008672"`
| 教程 | #0075ca | `Gmeek-imgbox="https://img.shields.io/static/v1?label=&message=教程&color=0075ca"`
| Anime | #E77AB1 | `Gmeek-imgbox="https://img.shields.io/static/v1?label=&message=Anime&color=E77AB1"`
| Win | #5AB3F3 | `Gmeek-imgbox="https://img.shields.io/static/v1?label=&message=Win&color=5AB3F3"`
| VPS | #5319e7 | `Gmeek-imgbox="https://img.shields.io/static/v1?label=&message=VPS&color=5319e7"`
| JS | #AD3152 | `Gmeek-imgbox="https://img.shields.io/static/v1?label=&message=JS&color=AD3152"`
| CSS | #218155 | `Gmeek-imgbox="https://img.shields.io/static/v1?label=&message=CSS&color=218155"`
| Github | #333333 | `Gmeek-imgbox="https://img.shields.io/static/v1?label=&message=Github&color=333333"`
| CDN | #cb222c | `Gmeek-imgbox="https://img.shields.io/static/v1?label=&message=CDN&color=cb222c"`
| Bug | #D73A4A | `Gmeek-imgbox="https://img.shields.io/static/v1?label=&message=Bug&color=D73A4A"`
| 软件 | #5da167 | `Gmeek-imgbox="https://img.shields.io/static/v1?label=&message=软件&color=5da167"`
| 翻墙 | #cb7b58 | `Gmeek-imgbox="https://img.shields.io/static/v1?label=&message=翻墙&color=cb7b58"`

# Readme.md

📄 > 文章总数.
💬 > 评论总数.
🌺 > 是统计的所有文章的字符数.
⏰ > 最后一次 Actions 的时间.