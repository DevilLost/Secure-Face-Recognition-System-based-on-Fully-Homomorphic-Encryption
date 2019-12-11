# Secure Face Recognize README

标签（空格分隔）： Secure Face Recognize

---
环境要求:
```
Windows10 v1809 or earlier
Python 3.6.8 X64 (add to PATH)
Mysql 5.7.X
```

快速开始:
```
将 SecureFaceRecognize.rar 解压至本地
将documents/face.sql中的数据库结构导入MySQL5.7数据库中
修改 config.py 中的数据库配置
当前目录打开CMD命令行窗口
输入 pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple 安装环境
输入 python main.py 开启服务环境
```

使用说明:

在较新版的谷歌浏览器中输入地址 http://127.0.0.1:500
点击开始体验进入录取页面，根据情况选择本地照片或者摄像头拍摄上传照片
上传成功后可在信息页进行比较、获取原始脸部数据和加密脸部数据
