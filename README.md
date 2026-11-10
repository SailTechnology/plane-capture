# 飞机捕获 · 公开交付与 DSH 部署

本仓库提供可调用的部署 skill、校验清单和 Windows 引导运行环境。完整控制源码、机械原生文件、仿真和过程资料保存在本仓库的公开 Release 附件中。

当前版本：v2026.11.09。完整下载约6.49 GiB；含下载缓存、分卷合并和解压，建议目标磁盘至少预留31 GiB。运行和安装过程不自动连接或驱动真实设备。

## 获取工程

仓库和 Release 已公开，无需 GitHub 账号或令牌。使用当前 main 分支获取部署工具：

    git clone https://github.com/SailTechnology/plane-capture.git
    cd plane-capture

没有 Git 时，可从仓库首页的 Code → Download ZIP 下载 main 分支，解压后在 DSH 中打开该目录。main 源码 ZIP 只包含部署工具，完整资料由安装脚本从 Release 下载。Release 页的 Source code 对应历史标签，请不要用它替代当前 main 部署工具。

## 让 AI 部署

在 DeepSeek Harness（DSH）中打开克隆或解压后的仓库，发送：

> 请读取 .agents/skills/plane-capture-deploy/SKILL.md，使用 plane-capture-deploy 将完整飞机捕获工程部署到我指定的空目录，并校验控制、机械、研究资料和仿真视频入口。只做软件部署，不连接机械臂或相机。

仓库级 skill 位于 .agents/skills/plane-capture-deploy，DSH 支持这一项目级目录。详细步骤、没有 Git 时的下载方式和故障处理见 [DSH部署教程](docs/DSH部署教程.md)。其他支持 Agent Skills 的 AI 也可读取该文件执行同样流程。

## 直接部署

使用 Windows PowerShell 5.1 或更新版本：

    powershell -NoProfile -ExecutionPolicy Bypass -File .agents/skills/plane-capture-deploy/scripts/Deploy.ps1 -Action install -Target "H:/Projects/飞机捕获_部署"

也可双击 00-一键部署.cmd，默认目标为 H:/Projects/飞机捕获_部署。其他电脑用 -Target 指定空目录；不要把盘符差异变成修改系统配置的理由。自带最小Python，不需要先装pip、CAD环境或第三方依赖。

附件采用不超过32 MiB的小分卷，脚本自动并行下载、按顺序合并。断网可以重跑同一命令，已经完整校验的分卷会复用；正在下载但未完成的单个附件会重下。已经取得全部 Release 附件时，增加 -OfflineAssets "附件目录" 可完全离线安装。

日志目录自动调整到本次部署目录的运行记录子目录，修改仅限明确允许本地配置的 data_directory，并记录原值与新哈希。设备标定和端口不自动改写。

安装后执行 -Action verify -Target "部署目录" 可检查全部归档 SHA256 和解压文件 CRC。

## 安装后的三个分类

- 01_控制地面站：v31.2完整程序、源码、运行环境、OSD录像、启动和回放入口、标定与调试说明。
- 02_机械设计：V8原生总装/零件、打印采购清单、35°导引板候选及CAD重建环境。
- 03_原理算法与过程资料：过程原件、索引和研究导读；78组当前工况结果、18段三维仿真、2段最后实拍对照；65个历史仿真视频文件的分类入口。

打开部署根目录的00_交付导航.html。视频总览在03_原理算法与过程资料/00_全部仿真视频.html，或双击05-打开全部仿真视频.cmd。

历史视频复用原件，不再复制65份素材。备用编码、循环片和早期渲染不等于新的独立试验。旧V6捕获结论已撤销；R1-7a回放属于另一机械臂模型，入口保留这些区别。

## 复现

在用户明确要求重算或重新渲染时，使用 skill 的 scripts/run_simulation.py；可指定工作盘，使用包内控制Python与机械CADPython，生成新工作副本。详见 skill 的 references/layout.md。

部署成功只说明下载、完整性与离线入口通过。独立位置真值、统一筒口安装标定、带载闭合、真实夹持和捕获验证仍有待实测项，详见 docs/方法结果与论文使用说明.md。

## 来源与第三方许可

delivery/manifest.json 固定 Release 和各附件的 SHA256。研究原件的逐文件来源清单位于过程资料包。Python引导环境的许可证在runtime/python/LICENSE.txt；完整第三方材料随各交付包保留，不授予超出原许可的权利。

官方说明：
- DSH项目级skills：https://github.com/deepseek-ai/deepseek-harness/blob/master/docs/subsystems/skills.md
- GitHub发布附件：https://docs.github.com/en/repositories/releasing-projects-on-github/about-releases
