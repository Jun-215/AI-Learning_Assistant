# AI Agent 对话系统 - PowerShell启动脚本
param(
    [string]$Mode = "dev",
    [switch]$Help
)

# 显示帮助信息
if ($Help) {
    Write-Host @"

AI Agent 对话系统 - PowerShell启动脚本

用法: .\run.ps1 [-Mode <模式>] [-Help]

参数:
  -Mode <模式>    指定启动模式
    dev           开发模式 (默认)
    backend       仅启动后端
    frontend      仅启动前端
    prod          生产模式
  -Help           显示此帮助信息

示例:
  .\run.ps1                    # 开发模式启动
  .\run.ps1 -Mode backend      # 仅启动后端
  .\run.ps1 -Mode frontend     # 仅启动前端
  .\run.ps1 -Mode prod         # 生产模式启动

"@
    exit 0
}

# 设置项目路径
$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$BackendDir = Join-Path $ProjectRoot "backend"
$FrontendDir = Join-Path $ProjectRoot "frontend"

Write-Host "===========================================" -ForegroundColor Cyan
Write-Host "   AI Agent 对话系统 - PowerShell启动" -ForegroundColor Cyan
Write-Host "===========================================" -ForegroundColor Cyan
Write-Host ""

# 检查必要文件
if (-not (Test-Path (Join-Path $BackendDir "app.py"))) {
    Write-Host "❌ 错误: 找不到后端文件 app.py" -ForegroundColor Red
    exit 1
}

if (-not (Test-Path (Join-Path $FrontendDir "package.json"))) {
    Write-Host "❌ 错误: 找不到前端文件 package.json" -ForegroundColor Red
    exit 1
}

# 启动函数
function Start-Backend {
    Write-Host "🔧 启动后端服务..." -ForegroundColor Yellow
    Set-Location $BackendDir
    python app.py
}

function Start-Frontend {
    Write-Host "🌐 启动前端服务..." -ForegroundColor Yellow
    Set-Location $FrontendDir
    npm start
}

function Start-DevMode {
    Write-Host "📡 启动后端服务 (后台运行)..." -ForegroundColor Yellow
    
    # 启动后端 (新窗口)
    $backendJob = Start-Process -FilePath "cmd" -ArgumentList "/k", "cd /d `"$BackendDir`" && python app.py" -WindowStyle Minimized -PassThru
    
    Write-Host "⏳ 等待后端启动..." -ForegroundColor Yellow
    Start-Sleep -Seconds 3
    
    Write-Host "🌐 启动前端服务..." -ForegroundColor Yellow
    Set-Location $FrontendDir
    npm start
}

function Start-ProdMode {
    Write-Host "🚀 生产模式启动..." -ForegroundColor Green
    
    # 启动后端 (后台)
    Write-Host "📡 启动后端服务 (后台运行)..." -ForegroundColor Yellow
    $backendJob = Start-Process -FilePath "cmd" -ArgumentList "/k", "cd /d `"$BackendDir`" && python app.py" -WindowStyle Minimized -PassThru
    
    Start-Sleep -Seconds 3
    
    # 启动前端 (后台)
    Write-Host "🌐 启动前端服务 (后台运行)..." -ForegroundColor Yellow
    $frontendJob = Start-Process -FilePath "cmd" -ArgumentList "/k", "cd /d `"$FrontendDir`" && npm start" -WindowStyle Minimized -PassThru
    
    Start-Sleep -Seconds 2
    
    Write-Host "✅ 服务启动完成！" -ForegroundColor Green
    Write-Host "📱 前端地址: http://localhost:3000" -ForegroundColor Cyan
    Write-Host "🔧 后端地址: http://localhost:5000" -ForegroundColor Cyan
}

# 根据模式启动
switch ($Mode.ToLower()) {
    "backend" { Start-Backend }
    "frontend" { Start-Frontend }
    "dev" { Start-DevMode }
    "prod" { Start-ProdMode }
    default { 
        Write-Host "🚀 启动模式: 开发模式" -ForegroundColor Green
        Start-DevMode 
    }
}

Write-Host ""
Write-Host "===========================================" -ForegroundColor Cyan
