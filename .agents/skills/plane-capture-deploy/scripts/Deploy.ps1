param(
 [ValidateSet('plan','install','verify')][string]$Action='install',
 [string]$Target='H:\Projects\飞机捕获_部署',
 [string]$Cache,
 [string]$OfflineAssets
)
$ErrorActionPreference='Stop'
$repositoryRoot=Split-Path -Parent (Split-Path -Parent (Split-Path -Parent (Split-Path -Parent $PSScriptRoot)))
$taskPython=Join-Path $repositoryRoot 'runtime\python\python.exe'
if (-not (Test-Path -LiteralPath $taskPython)) { throw '仓库自带Python缺失，请完整克隆仓库。' }
$arguments=@('-B','-X','utf8',(Join-Path $PSScriptRoot 'deploy.py'),$Action,'--target',$Target)
if ($Cache) { $arguments+=@('--cache',$Cache) }
if ($OfflineAssets) { $arguments+=@('--offline-assets',$OfflineAssets) }
& $taskPython @arguments
exit $LASTEXITCODE
