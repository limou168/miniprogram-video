package com.video.service;

import com.qcloud.cos.COSClient;
import com.qcloud.cos.ClientConfig;
import com.qcloud.cos.auth.BasicCOSCredentials;
import com.qcloud.cos.auth.BasicSessionCredentials;
import com.qcloud.cos.auth.COSCredentials;
import com.qcloud.cos.http.HttpMethodName;
import com.qcloud.cos.http.HttpProtocol;
import com.qcloud.cos.model.*;
import com.qcloud.cos.region.Region;
import com.video.config.CosConfig;
import jakarta.annotation.PostConstruct;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.util.StringUtils;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.net.URL;
import java.util.Date;

/**
 * 腾讯云 COS 对象存储服务
 * 支持两种认证方式：
 *   1. COS_SECRET_ID + COS_SECRET_KEY（长期密钥，优先使用）
 *   2. TCB_SECRETID + TCB_SECRETKEY + TCB_SESSIONTOKEN（微信云托管自动注入的临时凭证）
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class CosService {

    private final CosConfig cosConfig;

    /** COS 客户端（懒加载，首次使用时创建） */
    private COSClient cosClient;
    /** 凭证过期时间（临时凭证用） */
    private Date credentialsExpireAt;
    /** 认证方式是否为临时凭证 */
    private boolean useTempCredentials = false;

    @PostConstruct
    public void init() {
        log.info("COS 配置: bucket={}, region={}", cosConfig.getBucket(), cosConfig.getRegion());
        if (!StringUtils.hasText(cosConfig.getBucket()) || !StringUtils.hasText(cosConfig.getRegion())) {
            log.warn("COS_BUCKET 或 COS_REGION 未配置，COS 功能不可用");
            return;
        }
        try {
            // 创建 COS 客户端
            createCosClient();
            log.info("COS 客户端初始化成功");
        } catch (Exception e) {
            log.warn("COS 客户端初始化失败，COS 功能将不可用：{}", e.getMessage());
            log.warn("如需使用 COS，请在云托管环境变量中配置 COS_SECRET_ID 和 COS_SECRET_KEY");
            this.cosClient = null;
        }
    }

    /**
     * 获取 COS 客户端（若临时凭证过期则自动重建）
     */
    private COSClient getClient() {
        if (useTempCredentials && credentialsExpireAt != null
                && new Date().after(new Date(credentialsExpireAt.getTime() - 5 * 60 * 1000))) {
            // 临时凭证即将过期（提前5分钟），重建客户端
            log.info("COS 临时凭证即将过期，重新获取...");
            createCosClient();
        }
        return cosClient;
    }

    /**
     * 创建 COS 客户端
     */
    private void createCosClient() {
        ClientConfig clientConfig = new ClientConfig(new Region(cosConfig.getRegion()));
        clientConfig.setHttpProtocol(HttpProtocol.https);
        clientConfig.setConnectionTimeout(10000);
        clientConfig.setSocketTimeout(30000);

        COSCredentials credentials = resolveCredentials();
        this.cosClient = new COSClient(credentials, clientConfig);
    }

    /**
     * 解析凭证：优先用长期密钥，否则用 TCB 临时凭证
     */
    private COSCredentials resolveCredentials() {
        // 方式1：长期密钥（用户手动配置）
        if (StringUtils.hasText(cosConfig.getSecretId()) && StringUtils.hasText(cosConfig.getSecretKey())) {
            log.info("使用长期密钥认证 COS");
            this.useTempCredentials = false;
            return new BasicCOSCredentials(cosConfig.getSecretId(), cosConfig.getSecretKey());
        }

        // 方式2：微信云托管临时凭证（TCB 自动注入）
        String tcbSecretId = System.getenv("TCB_SECRETID");
        String tcbSecretKey = System.getenv("TCB_SECRETKEY");
        String tcbSessionToken = System.getenv("TCB_SESSIONTOKEN");
        String tcbEnvId = System.getenv("TCB_ENV_ID");

        if (StringUtils.hasText(tcbSecretId) && StringUtils.hasText(tcbSecretKey)
                && StringUtils.hasText(tcbSessionToken)) {
            log.info("使用微信云托管临时凭证认证 COS, envId={}", tcbEnvId);
            this.useTempCredentials = true;
            // 临时凭证通常有效期为 2 小时
            this.credentialsExpireAt = new Date(System.currentTimeMillis() + 2 * 3600 * 1000);
            return new BasicSessionCredentials(tcbSecretId, tcbSecretKey, tcbSessionToken);
        }

        // 都没有配置，抛出异常
        throw new IllegalStateException(
                "COS 凭证未配置！请在环境变量中设置 COS_SECRET_ID + COS_SECRET_KEY，"
                        + "或确认云托管已自动注入 TCB 临时凭证");
    }

    // ==================== 文件上传 ====================

    /**
     * 上传文件到 COS
     *
     * @param key       COS 中的文件路径，如 "videos/2024/01/filename.mp4"
     * @param file      要上传的文件
     * @return COS 中的文件 key
     */
    public String uploadFile(String key, MultipartFile file) throws IOException {
        COSClient client = getClient();
        ObjectMetadata metadata = new ObjectMetadata();
        metadata.setContentLength(file.getSize());
        metadata.setContentType(file.getContentType());

        PutObjectRequest request = new PutObjectRequest(
                cosConfig.getBucket(), key, file.getInputStream(), metadata);
        // 设置对象为私有读写
        request.setCannedAcl(CannedAccessControlList.Private);

        PutObjectResult result = client.putObject(request);
        log.info("COS 上传成功: bucket={}, key={}, etag={}",
                cosConfig.getBucket(), key, result.getETag());
        return key;
    }

    /**
     * 上传文件到 COS（指定 Content-Type）
     */
    public String uploadFile(String key, MultipartFile file, String contentType) throws IOException {
        COSClient client = getClient();
        ObjectMetadata metadata = new ObjectMetadata();
        metadata.setContentLength(file.getSize());
        metadata.setContentType(contentType);

        PutObjectRequest request = new PutObjectRequest(
                cosConfig.getBucket(), key, file.getInputStream(), metadata);
        request.setCannedAcl(CannedAccessControlList.Private);

        PutObjectResult result = client.putObject(request);
        log.info("COS 上传成功: key={}, etag={}", key, result.getETag());
        return key;
    }

    // ==================== 生成访问 URL ====================

    /**
     * 根据文件 key 生成预签名访问 URL
     * 如果配置了 CDN 域名，则返回 CDN URL
     *
     * @param key COS 中的文件路径
     * @return 可访问的文件 URL
     */
    public String getFileUrl(String key) {
        if (!StringUtils.hasText(key)) {
            return "";
        }

        // 如果已经是 HTTP URL，直接返回
        if (key.startsWith("http://") || key.startsWith("https://")) {
            return key;
        }

        // 如果配置了 CDN 域名，返回 CDN URL
        if (StringUtils.hasText(cosConfig.getCdnDomain())) {
            String cdnDomain = cosConfig.getCdnDomain();
            if (!cdnDomain.startsWith("http")) {
                cdnDomain = "https://" + cdnDomain;
            }
            return cdnDomain + "/" + key;
        }

        // 生成预签名 URL（带过期时间）
        return generatePresignedUrl(key);
    }

    /**
     * 智能转换 URL：
     * - 如果已经是 HTTP URL，原样返回
     * - 否则视为 COS 文件 key，生成可访问的 URL
     * - 如果 COS 不可用，原样返回
     */
    public String transformUrl(String url) {
        if (!StringUtils.hasText(url)) {
            return "";
        }
        // 已经是完整 URL，不处理
        if (url.startsWith("http://") || url.startsWith("https://")) {
            return url;
        }
        // COS 未配置时原样返回
        if (!isAvailable()) {
            return url;
        }
        return getFileUrl(url);
    }

    /**
     * 生成 COS 预签名 URL（带过期时间）
     */
    private String generatePresignedUrl(String key) {
        try {
            COSClient client = getClient();
            Date expiration = new Date(System.currentTimeMillis()
                    + cosConfig.getUrlExpireSeconds() * 1000);

            GeneratePresignedUrlRequest request = new GeneratePresignedUrlRequest(
                    cosConfig.getBucket(), key, HttpMethodName.GET);
            request.setExpiration(expiration);

            URL url = client.generatePresignedUrl(request);
            return url.toString();
        } catch (Exception e) {
            log.error("生成 COS 预签名 URL 失败: key={}", key, e);
            // 降级：返回原始 key
            return key;
        }
    }

    // ==================== 文件删除 ====================

    /**
     * 从 COS 删除文件
     */
    public void deleteFile(String key) {
        try {
            COSClient client = getClient();
            client.deleteObject(cosConfig.getBucket(), key);
            log.info("COS 删除成功: key={}", key);
        } catch (Exception e) {
            log.error("COS 删除失败: key={}", key, e);
        }
    }

    // ==================== 工具方法 ====================

    /**
     * 判断 COS 服务是否可用
     */
    public boolean isAvailable() {
        return cosClient != null
                && StringUtils.hasText(cosConfig.getBucket())
                && StringUtils.hasText(cosConfig.getRegion());
    }

    /**
     * 提取 COS 文件 key 中的文件名
     */
    public String getFileName(String key) {
        if (!StringUtils.hasText(key)) return "";
        int lastSlash = key.lastIndexOf('/');
        return lastSlash >= 0 ? key.substring(lastSlash + 1) : key;
    }
}
