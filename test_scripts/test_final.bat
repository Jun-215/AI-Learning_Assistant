@echo off
echo 🧪 AI Agent 系统最终测试
echo =======================================

echo [1/5] 检查项目文件...
if not exist "backend\app.py" (
    echo ❌ 缺少主要后端文件
    goto :error
)
if not exist "frontend\src\App.tsx" (
    echo ❌ 缺少主要前端文件
    goto :error
)
echo ✅ 主要文件存在

echo.
echo [2/5] 检查Python环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python不可用
    goto :error
)
echo ✅ Python环境正常

echo.
echo [3/5] 检查Node.js环境...
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js不可用
    goto :error
)
echo ✅ Node.js环境正常

echo.
echo [4/5] 检查Python依赖...
cd backend
python -c "import flask, dashscope, PyPDF2; print('依赖正常')" >nul 2>&1
if errorlevel 1 (
    echo ❌ Python依赖缺失
    cd ..
    goto :error
)
cd ..
echo ✅ Python依赖完整

echo.
echo [5/5] 检查前端依赖...
if not exist "frontend\node_modules" (
    echo ❌ 前端依赖缺失，请运行: cd frontend && npm install
    goto :error
)
echo ✅ 前端依赖完整

echo.
echo =======================================
echo 🎉 系统测试通过！
echo.
echo 🚀 启动方式:
echo   run.bat          - 开发模式启动
echo   run.bat prod     - 生产模式启动
echo.
echo 📱 访问地址:
echo   前端: http://localhost:3000
echo   后端: http://localhost:5000
echo.
goto :end

:error
echo.
echo =======================================
echo ❌ 系统测试失败
echo 请检查上述错误并修复后重试
echo.

:end
pause
