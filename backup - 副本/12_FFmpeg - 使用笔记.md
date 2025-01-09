# 前言

Github 地址: https://github.com/FFmpeg/FFmpeg

> [!NOTE]
> cmd 命令行使用如果没有写输出路径的话默认输出在:`C:\Users\Administrator`

# 视频转格式

如果只是容器改变, 编码没改,可以使用`-c copy`参数或`-c:a copy`参数或`-c:v copy`参数.

比如:

```
ffmpeg -i input.avi -q 1 -c copy output.mov
```

# 提取视频中的音频

## 提取 mp3 格式

```
ffmpeg -i input.mp4 -vn -c:a libmp3lame output.mp3
```

## 提取无损 wav 格式

```
ffmpeg -i input.mp4 -vn -acodec pcm_s16le -ar 44100 -ac 2 output.wav
```

# 去掉视频中的音频

```
ffmpeg -i [File] -c:v copy -an [File2]
```

# 音视频合并

```
ffmpeg -i [File] -c:v copy -c:a aac -strict experimental [File2]
```

如果视频中已经包含了音频,这个时候还可以替换视频中的音频,使用下面命令行.

```
ffmpeg -i [File] -c:v copy -c:a aac -strict experimental -map 0:v:0 -map 1:a:0 [File2]

```

# 视频裁切

```
ffmpeg -i [File] -ss 00:04:53 -c copy -t 00:00:03 -codec copy [File2]
```

> -ss 表示开始切割的时间
> -t 表示要切多少. 上面例子就是从头开始, 切3秒钟出来

注意一个问题, ffmpeg 在切割视频的时候无法做到时间绝对准确,因为视频编码中关键帧(I帧)和跟随它的B帧、P帧是无法分割开的, 否则就需要进行重新帧内编码, 会让视频体积增大.

所以, 如果切割的位置刚好在两个关键帧中间, 那么 ffmpeg 会向前/向后切割, 最后切割出的 chunk 长度总是会大于等于应有的长度.

达成相同效果,也可以用`-ss`和`-to`选项.

```
ffmpeg -i [File] -ss 30 -c copy -to 40 -codec copy [File2]
```

# 视频转码

```
ffmpeg -i [File] -vcodec h264 [File2]
```

> -vcodec 设定视频编解码器, 未设定时则使用与输入流相同的编解码器

当然了, 如果 ffmpeg 当时编译时, 添加了外部的 x265 或者 x264, 那也可以用外部的编码器来编码.(不知道什么是x265, 可以 [Google](https://www.google.com/search?q=%E4%BB%80%E4%B9%88%E6%98%AFx265) 一下, 简单的说, 就是它不包含在 ffmpeg 的源码里, 是独立的一个开源代码, 用于编码 HEVC, ffmpeg 编码时可以调用它. 当然, ffmpeg 也有自己的编码器)

```
ffmpeg -i [File] -c:v libx265 [File2]
```

```
ffmpeg -i [File] -c:v libx264 [File2]
```

# 视频转分辨率

```
ffmpeg -i [File] -vf scale=1280:720 [File2]
```

# 调整播放速度

加速四倍:

```
ffmpeg -i [File] -vf "setpts=0.25*PTS" [File2]
```