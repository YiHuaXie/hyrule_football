
``` shell
# 1. 停掉旧容器（可选，但干净一点）
docker compose down

# 2. 重新构建并后台启动
docker compose up -d --build

# 只启动 APP
docker compose up -d --build app

# 只重启不改变代码的情况
docker compose down
docker compose up -d
```