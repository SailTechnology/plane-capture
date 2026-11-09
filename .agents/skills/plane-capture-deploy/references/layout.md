# 交付结构与复现

五个附件组件合成三个分类，保持原桌面交付布局：

| 组件 | 安装位置 | 内容 |
|---|---|---|
| control | 01_控制地面站 | v31.2、OSD保存、Python及锁定依赖、源码、标定与启动工具 |
| mechanical | 02_机械设计 | V8原生装配/零件、打印采购、CAD源码及重建运行环境 |
| research | 03_原理算法与过程资料/过程资料包_20261109 | 完整过程原件、无损压缩日志、原理、算法、调试和失败过程与来源索引 |
| simulation | 03_原理算法与过程资料/仿真Demo与SimToReal对照_20261109 | 78组工况数据、18段三维演示、2段最后实拍对照、生产算法快照与复现代码 |
| navigation | 分类根目录及控制包补充目录 | 统一导航、65个历史视频的聚合入口及其他主ZIP外的交付资料 |

实拍媒体只保留最后两次左右拼接成片及从这两次制作的对照。65个历史视频均为仿真；备用编码和循环片不等于新增独立试验。

## 控制

总目录的01-启动控制地面站.cmd是用户主动启动入口。部署验收仅执行程序tools/station_cli.py replay --no-browser，确认离线回放路径；不打开摄像头或驱动机械臂。实时录像默认保存带OSD的MP4，原AVI和日志按既有策略保留。

## 仿真

作者原包Start-Demo.ps1遵循本机H盘约定。其他接收者使用仓库提供的run_simulation.py，不改写原包。在仓库根目录执行：

    runtime/python/python.exe -B -X utf8 .agents/skills/plane-capture-deploy/scripts/run_simulation.py --target "H:/Projects/飞机捕获_部署" --mode render --work-root "H:/Projects/飞机捕获_仿真复现"

mode=render 从已保存轨迹生成18段模拟和2段对照；mode=all 先重算基准与78组，再统计并生成视频。工作目录和日志写到指定的新目录。使用部署包的控制Python、机械CADPython运行，不连接真实设备。

观看和查阅不依赖重新仿真。没有把接触与夹持模型、未实测参数或旧模型结果当作实机验收。
