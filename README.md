# Youtube视频下载器

​	Youtube视频下载器可以下载Youtube上面的视频，支持单个视频下载和播放列表批量下载，但需要注意的是，下载的时候需要挂上代理，保证本地可以访问Youtube。

> 本项目仅为学习之作，请勿用作商业用途，否则后果自负！

### 打赏

------

- 解决上面这些问题，需要花费很多时间与精力。支持项目继续完善下去，你也可以贡献一份力量！

- 有了打赏，也就会有更新的动力 : )

  ![](image/5.jpg)

### 更新日志

------

#### v1.0.0 `2019/7/28`

- 初始化项目，完成下载单个视频、批量下载播放列表中的视频

### 开发文档[待完善]

------

#### 使用方法

1、下载单个视频：在 ```YoutubeVideoDownloader/YoutubeVideoDownloader``` 目录下使用 ```scrapy crawl download -a target=play_url``` ，例如 ```scrapy crawl download -a target target=https://www.youtube.com/watch?v=O7KaDi_Po-g```

2、批量下载播放列表中的视频：在 ```YoutubeVideoDownloader/YoutubeVideoDownloader``` 目录下使用 ```scrapy crawl download -a target=playlist_url``` ，例如 ```scrapy crawl download -a target target=https://www.youtube.com/watch?v=O7KaDi_Po-g&list=PU2XZEtXCC8kXzN4RbFcMLFw```