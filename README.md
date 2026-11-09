# 飞机捕获 · 私有交付与 AI 部署

本仓库提供可调用的部署 skill、校验清单和 Windows 引导运行环境。完整控制源码、机械原生文件、仿真和过程资料保存在同一私有仓库的 Release 附件中。

当前版本：v2026.11.09。完整下载约6.49 GiB；含下载缓存、分卷合并和解压，建议目标磁盘至少预留31 GiB。运行和安装过程不自动连接或驱动真实设备。

## 授权与获取

仓库和 Release 均为 private。先由所有者在仓库 Settings → Collaborators 中添加指定 GitHub 账号，再由接收者用自己的账号登录。没有授权时访问通常显示404；不要把它误认为公开下载地址失效。

    git clone https://github.com/SailTechnology/plane-capture.git
    cd plane-capture

Git Credential Manager 或 gh auth 的现有登录可用于下载。无需作者令牌，不要在聊天、脚本或提交中分享凭据。

## 让 AI 部署

在 Codex 或兼容 Agent Skills 的 AI 中打开克隆后的仓库，发送：

> 使用 $plane-capture-deploy，把完整工程部署到我指定的目录，并校验控制、机械、研究资料和全部仿真视频入口。只做软件部署。

仓库级 skill 位于 .agents/skills/plane-capture-deploy，SKILL.md 和脚本均随源码提供。其他 AI 可直接读取该文件执行同样流程。

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
- Codex仓库级skills：https://developers.openai.com/codex/skills
- GitHub私有仓库：https://docs.github.com/en/repositories/creating-and-managing-repositories/about-repositories
- GitHub发布附件：https://docs.github.com/en/repositories/releasing-projects-on-github/about-releases
