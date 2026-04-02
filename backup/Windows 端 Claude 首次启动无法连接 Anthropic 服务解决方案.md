# 问题现象

在 Windows 终端 / 命令行中输入 `claude` 命令后, 出现以下错误提示, 无法正常使用 Claude 服务: 

```
Unable to connect to Anthropic services
Failed to connect to api.anthropic.com: ECONNREFUSED
Please check your internet connection and network settings.
Note: Claude Code might not be available in your country. Check supported countries at https://anthropic.com/supported-countries
```
> [!NOTE]
> Claude 首次启动的引导流程会检测所在国家地区, 不符合会导致 API 连接拦截.

# 解决方案(跳过引导流程)

> [!NOTE]
> 通过修改 Claude 配置文件 `.claude.json`, 新增 `hasCompletedOnboarding: true` 配置项, 直接跳过首次启动引导, 即可解决连接问题. 

文件路径一般是 `C:\Users\[你的用户名]\.claude.json`.

找到后对它进行编辑, 在里面任意新增一行 `hasCompletedOnboarding: true`, 同时 json 文件注意补写逗号即可.

保存配置文件后, 重新打开终端, 输入 `claude` 看看是否成功.