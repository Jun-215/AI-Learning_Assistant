@echo off
echo 正在安装语义搜索依赖...
echo ==============================

echo 1. 安装基础依赖...
pip install torch --index-url https://download.pytorch.org/whl/cpu

echo 2. 安装sentence-transformers...
pip install sentence-transformers

echo 3. 安装faiss...
pip install faiss-cpu

echo 4. 验证安装...
python -c "import torch; import sentence_transformers; import faiss; print('所有依赖安装成功!')"

echo ==============================
echo 安装完成!
pause
