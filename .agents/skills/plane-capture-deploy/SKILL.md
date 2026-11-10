---
name: plane-capture-deploy
description: 在 Windows 上使用公开 Release 部署飞机捕获完整交付包，自动下载分卷、校验、合并、解压并定位控制、机械、研究资料和仿真视频；也支持完整性复核及离线仿真复现。
---

# 飞机捕获部署

适用于本仓库 SailTechnology/plane-capture 的固定版本交付。先读取仓库根目录的 delivery/manifest.json；它是附件名称、版本和 SHA256 的依据，不猜测“最新”附件或换用其他模型。

## 部署

1. 确认 Windows x64、GitHub 网络可用，并选定空部署目录，建议预留至少 32 GiB。本机工作默认写 H:；其他接收者以其指定目录为准，不把本机盘符约定强加给所有用户，不覆盖已有工程。
2. 使用仓库自带 Python 和本 skill 的 scripts/Deploy.ps1。先执行 -Action plan -Target <目标目录> 查看大小与位置，再执行 -Action install -Target <目标目录>。无需安装 pip、CAD 或 Python 到系统。
3. 这是公开仓库，下载不需要 GitHub 登录、token 或 gh 命令。不要向用户索取凭据；DSH 的模型服务配置与项目下载互不依赖。
4. 脚本通过公开 Release 附件链接下载，逐分卷和完整 ZIP 做 SHA256 校验，再按原分类解压。已完整下载的分卷复用；失败的未完成文件重新下载，最多3次。网络失败后报告具体阶段，可直接重跑原命令。
5. 安装结束检查 _deployment/completion.json 和离线回放入口检查结果。重新完整复核时执行 -Action verify；它检查归档哈希及全部解压文件 CRC，不连接设备。
6. 安装只把允许本地修改的 station/settings.json 中 data_directory 改到接收者部署目录的运行记录子目录；原归档不改，原值和新哈希记录在 _deployment/local_overrides.json。相机、串口、标定和关节参数不自动改写。后续用户主动修改标定导致校验差异时，先识别为本地配置变更，不以恢复原件覆盖测量。
7. 给用户交付 00_交付导航.html、三个分类位置及 03_原理算法与过程资料/00_全部仿真视频.html。安装不自动启动地面站、相机、CAN、串口或电机。

默认示例：

    & ./.agents/skills/plane-capture-deploy/scripts/Deploy.ps1 -Action install -Target 'H:/Projects/飞机捕获_部署'

若用户已下载全部附件，增加 -OfflineAssets <附件目录>，可以在无网络时完成本地校验与解压。附件目录应包含 manifest 中的原始 ASCII 附件名。DSH 使用方法见仓库 docs/DSH部署教程.md。

## 仿真与硬件边界

- 读取 [交付结构与复现](references/layout.md) 选择控制、机械、研究和仿真入口。
- 只有用户要求重新计算或渲染时，才使用 scripts/run_simulation.py。它允许接收者指定工作目录，不依赖作者机器的H盘路径；产生新工作副本，不修改已验证的交付文件。
- 部署成功不等于相机、机械臂已连接或捕获成功。已有内参、手眼、设备名和工厂零位属于作者设备，换机器需按项目说明复核。部署动作不能代替真实设备的启用、运动、回零或捕获授权。
- 当前18段仿真、2段实拍对照和65个历史视频按模型分组；旧V6捕获结论已撤销，R1-7a属于另一机械臂模型。保留标签，不把它们写成当前PiPER实机成功证据。
