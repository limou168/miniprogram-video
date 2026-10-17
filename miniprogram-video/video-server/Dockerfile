# ==============================
# 第一阶段：构建 (Maven + JDK 21)
# ==============================
FROM eclipse-temurin:21-jdk-alpine AS builder

WORKDIR /build

# 先复制 pom.xml 下载依赖（利用 Docker 缓存）
COPY pom.xml .
RUN apk add --no-cache maven && \
    mvn dependency:go-offline -B

# 复制源码并打包
COPY src ./src
RUN mvn clean package -DskipTests -B

# ==============================
# 第二阶段：运行 (最小 JRE 镜像)
# ==============================
FROM eclipse-temurin:21-jre-alpine

WORKDIR /app

# 设置时区
RUN apk add --no-cache tzdata && \
    cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && \
    echo "Asia/Shanghai" > /etc/timezone && \
    apk del tzdata && \
    rm -rf /var/cache/apk/*

# 从构建阶段复制 JAR
COPY --from=builder /build/target/video-server-1.0.0.jar app.jar

# 健康检查
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD wget -qO- http://localhost:${PORT:-80}/actuator/health || exit 1

# 微信云托管注入 PORT 环境变量，默认 80
EXPOSE 80

ENTRYPOINT ["sh", "-c", "java -jar app.jar --server.port=${PORT:-80} --spring.profiles.active=cloud"]
