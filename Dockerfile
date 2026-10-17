# 微信云托管 - 跳转到子项目的 Dockerfile
FROM eclipse-temurin:21-jre-alpine

WORKDIR /app

# 复制子项目的打包产物
COPY miniprogram-video/video-server/target/video-server-1.0.0.jar app.jar

# 设置时区
RUN apk add --no-cache tzdata && \
    cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && \
    echo "Asia/Shanghai" > /etc/timezone && \
    apk del tzdata && \
    rm -rf /var/cache/apk/*

HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD wget -qO- http://localhost:${PORT:-80}/actuator/health || exit 1

EXPOSE 80

ENTRYPOINT ["sh", "-c", "java -jar app.jar --server.port=${PORT:-80} --spring.profiles.active=cloud"]
