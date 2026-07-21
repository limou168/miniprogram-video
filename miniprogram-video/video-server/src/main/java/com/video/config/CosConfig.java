package com.video.config;

import lombok.Data;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.context.annotation.Configuration;

/**
 * 腾讯云 COS 配置
 * 从环境变量读取：
 *   COS_BUCKET        — 存储桶名称
 *   COS_REGION        — 区域（如 ap-shanghai）
 *   COS_SECRET_ID     — API 密钥 ID（可选，不填则用 TCB 临时凭证）
 *   COS_SECRET_KEY    — API 密钥 Key（可选，不填则用 TCB 临时凭证）
 *   COS_CDN_DOMAIN    — CDN 加速域名（可选，为空则用 COS 默认域名）
 */
@Data
@Configuration
@ConfigurationProperties(prefix = "cos")
public class CosConfig {

    /** 存储桶名称 */
    private String bucket = "";

    /** 区域 */
    private String region = "";

    /** 长期密钥 ID（可选） */
    private String secretId = "";

    /** 长期密钥 Key（可选） */
    private String secretKey = "";

    /** 自定义 CDN 域名（可选） */
    private String cdnDomain = "";

    /** 预签名 URL 有效期（秒），默认 7 天 */
    private long urlExpireSeconds = 7 * 24 * 3600;
}
