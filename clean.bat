@echo off
REM 清理不需要的临时文件和简化版本文件

echo 🧹 清理AI Agent项目...
echo =====================================

REM 删除不需要的简化版本文件
if exist "backend\app_simple.py" (
    del "backend\app_simple.py" /f /q
    echo ✅ 删除 backend\app_simple.py
)

if exist "frontend\src\App_simple.tsx" (
    del "frontend\src\App_simple.tsx" /f /q
    echo ✅ 删除 frontend\src\App_simple.tsx
)

REM 清理Python缓存
if exist "backend\__pycache__" (
    rmdir "backend\__pycache__" /s /q
    echo ✅ 清理Python缓存
)

REM 清理前端构建缓存
if exist "frontend\build" (
    rmdir "frontend\build" /s /q
    echo ✅ 清理前端构建缓存
)

if exist "frontend\.next" (
    rmdir "frontend\.next" /s /q
    echo ✅ 清理Next.js缓存
)

echo.
echo =====================================
echo ✅ 清理完成！
echo.
echo 📁 当前项目结构:
echo   backend/app.py      - 主后端应用
echo   frontend/src/App.tsx - 主前端应用
echo.
echo 🚀 启动项目:
echo   run.bat            - 开发模式
echo   run.bat prod       - 生产模式
echo.
pause
