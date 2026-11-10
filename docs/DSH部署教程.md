# 飞机捕获工程：DSH 部署教程

工程公开地址：<https://github.com/SailTechnology/plane-capture>

完整资料下载地址：<https://github.com/SailTechnology/plane-capture/releases/tag/v2026.11.09>

部署工具不需要 GitHub 账号或令牌。完整资料约 6.49 GiB，建议在目标磁盘预留至少 32 GiB；需要 Windows x64 和能连接 GitHub 的网络。安装不会自动连接机械臂、相机、CAN 或串口。

## 已安装 DSH

1. 下载部署工具。可以在 PowerShell 运行以下命令，H 盘不存在时把路径换成自己的工作目录：

   ```powershell
   git clone https://github.com/SailTechnology/plane-capture.git H:\Projects\plane-capture
   ```

   没有 Git 时，打开[仓库首页](https://github.com/SailTechnology/plane-capture)，选择 **Code → Download ZIP**，解压得到 main 分支的部署工具。

2. 在 DSH 中把刚克隆或解压的 `plane-capture` 目录设为当前工作区。打开一个新会话，将下面这段话发给 DSH：

   > 请读取本目录的 `.agents/skills/plane-capture-deploy/SKILL.md`，使用 plane-capture-deploy 部署完整飞机捕获工程。先检查可用磁盘空间，询问或使用我指定的空目录；自动下载并校验 Release 分卷、合并和解压。完成后给我控制、机械、研究资料和全部仿真视频的入口。只做软件部署，不连接机械臂或相机。

3. 按 DSH 界面提示允许它读取项目、联网下载和向选定目录写入。等待下载、合并、解压与校验完成。

4. 打开目标目录中的 `00_交付导航.html`。控制地面站、机械设计、研究过程资料分别在 `01_控制地面站`、`02_机械设计`、`03_原理算法与过程资料`；全部仿真视频可从 `05-打开全部仿真视频.cmd` 进入。

## 还没有安装 DSH

已安装 DSH 桌面版的用户无需额外安装 Node.js。使用命令行启动 DSH Web 版时，请先安装 Node.js 和 Git；截至本教程更新，官方 `@deepseek-ai/dsh` 的 npm 版本要求 Node.js 24.9.0 或更高，具体以 [DSH 官方包信息](https://www.npmjs.com/package/@deepseek-ai/dsh)为准。然后在部署工具目录执行：

```powershell
cd H:\Projects\plane-capture
npx -y @deepseek-ai/dsh web
```

在 DSH 界面配置可用的模型服务，再发送上面的部署请求。模型服务可能需要使用者自己的账号或 API 凭据；项目下载本身不需要这些凭据。不要把凭据放进仓库或交付资料。

## 不通过 AI 的启动方式

在部署工具目录的 PowerShell 中运行：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\.agents\skills\plane-capture-deploy\scripts\Deploy.ps1 -Action install -Target "H:\Projects\飞机捕获_部署"
```

把 `-Target` 后的路径换成自己的空目录。也可双击 `00-一键部署.cmd`，其默认目标为 `H:\Projects\飞机捕获_部署`。

下载中断后重跑同一条命令；已校验的完整分卷会复用。重新完整校验时将 `-Action install` 改为 `-Action verify`。部署工具通过公开 Release 直链下载并逐项校验 SHA256，不使用需要登录的 GitHub API 下载 211 个数据分卷。

## 注意版本入口

请从仓库的 **main 分支**克隆或使用 Code → Download ZIP 获取最新版部署工具。Release 页中的 **Source code** 是对应历史标签的旧工具，可能仍要求私有仓库授权。Release 的数据附件仍是完整资料，最新版部署工具会自动选择并校验它们。

已有设备标定、相机名称和串口属于原设备。部署完成只证明软件和离线入口可用，不代表机械臂已通过实机联动、带载闭合或飞机捕获验证。
