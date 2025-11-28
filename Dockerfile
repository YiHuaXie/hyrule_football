FROM python:3.12-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量

# PYTHONFAULTHANDLER=1 当 python 崩溃会打印详细的堆栈跟踪
# PYTHONUNBUFFERED=1 日志立即输出
# PYTHONHASHSEED=random 控制 python 哈希随机化
# PIP_NO_CACHE_DIR=off 使用 PIP 缓存
# PIP_DISABLE_PIP_VERSION_CHECK=on 禁止 pip 在安装包时检查 pip 自身版本
# POETRY_VERSION=2.2.1 poetry 版本
ENV PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    POETRY_VERSION=2.2.1

# 安装 poetry
RUN pip install "poetry==$POETRY_VERSION"

# 配置 poetry 不创建虚拟环境
RUN poetry config virtualenvs.create false

# 安装 ping 和 curl 命令
RUN apt-get update && apt-get install -y iputils-ping curl

# 复制项目文件
COPY pyproject.toml README.md poetry.lock* /app/

# 只复制真正运行需要的代码：hyrule_football 包
COPY hyrule_football /app/hyrule_football

# 安装依赖RUN poetry install --no-interaction
RUN poetry install

# 暴露需要的端口（如果有Web服务的话）
# EXPOSE 8000

# 启动命令
CMD ["python", "-m", "hyrule_football.main"]