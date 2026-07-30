package com.video.controller;

import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.*;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.client.RestTemplate;

import java.net.URLDecoder;
import java.nio.charset.StandardCharsets;
import java.util.Arrays;
import java.util.List;
import java.util.stream.Collectors;

/**
 * 视频代理转发 - 解决第三方CDN防盗链问题
 * 同时重写 m3u8 内的 ts 片段地址，使其也经过代理
 */
@Slf4j
@RestController
@RequestMapping("/api/proxy")
public class ProxyController {

    private final RestTemplate restTemplate = new RestTemplate();

    private static final List<String> TS_EXT = Arrays.asList(".ts", ".m3u8", ".aac", ".mp4", ".vtt");

    @GetMapping("/video")
    public void proxyVideo(@RequestParam String url,
                           HttpServletRequest request,
                           HttpServletResponse response) {
        try {
            String decodedUrl = URLDecoder.decode(url, StandardCharsets.UTF_8);
            log.debug("代理视频: {}", decodedUrl);

            HttpHeaders headers = buildHeaders(decodedUrl);
            org.springframework.http.HttpEntity<Void> entity = new org.springframework.http.HttpEntity<>(headers);

            ResponseEntity<byte[]> proxyResponse = restTemplate.exchange(
                    decodedUrl, HttpMethod.GET, entity, byte[].class);

            HttpHeaders respHeaders = proxyResponse.getHeaders();
            MediaType contentType = respHeaders.getContentType();
            byte[] body = proxyResponse.getBody();

            if (body == null) {
                response.setStatus(HttpServletResponse.SC_NO_CONTENT);
                return;
            }

            // 如果返回的是 m3u8 内容，重写内部的 ts 路径
            if (contentType != null && contentType.toString().contains("m3u8")) {
                String m3u8Content = new String(body, StandardCharsets.UTF_8);
                String rewritten = rewriteM3u8(m3u8Content, decodedUrl);
                body = rewritten.getBytes(StandardCharsets.UTF_8);
                response.setContentType("application/vnd.apple.mpegurl;charset=utf-8");
            } else if (contentType != null) {
                response.setContentType(contentType.toString());
            }

            if (respHeaders.getContentLength() > 0) {
                response.setContentLengthLong(body.length);
            }
            response.setHeader("Access-Control-Allow-Origin", "*");
            response.setHeader("Access-Control-Allow-Methods", "GET, OPTIONS");
            response.setHeader("Cache-Control", "public, max-age=600");
            response.getOutputStream().write(body);
            response.getOutputStream().flush();
        } catch (Exception e) {
            log.warn("代理视频失败: {}", e.getMessage());
            response.setStatus(HttpServletResponse.SC_BAD_GATEWAY);
        }
    }

    /**
     * 重写 m3u8 内容，将 ts 片段地址改为代理地址
     */
    private String rewriteM3u8(String content, String baseUrl) {
        String baseDir = baseUrl.substring(0, baseUrl.lastIndexOf('/') + 1);
        String proxyBase = "/api/proxy/video?url=";

        return Arrays.stream(content.split("\n"))
                .map(line -> {
                    String trimmed = line.trim();
                    // 跳过注释和空行和 EXT 标签
                    if (trimmed.isEmpty() || trimmed.startsWith("#") || trimmed.startsWith("http")) {
                        return line;
                    }
                    // 是 ts / m3u8 片段路径 -> 重写为代理地址
                    if (TS_EXT.stream().anyMatch(trimmed::endsWith) || trimmed.contains(".")) {
                        String fullUrl = trimmed.startsWith("http") ? trimmed : baseDir + trimmed;
                        return proxyBase + java.net.URLEncoder.encode(fullUrl, StandardCharsets.UTF_8);
                    }
                    return line;
                })
                .collect(Collectors.joining("\n"));
    }

    /**
     * 构建请求头 - 模拟浏览器绕过防盗链
     */
    private HttpHeaders buildHeaders(String url) {
        HttpHeaders headers = new HttpHeaders();
        String domain = extractDomain(url);
        headers.set("Referer", domain + "/");
        headers.set("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36");
        headers.set("Accept", "*/*");
        headers.set("Accept-Language", "zh-CN,zh;q=0.9");
        headers.set("Origin", domain);
        return headers;
    }

    private String extractDomain(String url) {
        try {
            int start = url.indexOf("://") + 3;
            int end = url.indexOf("/", start);
            return end > start ? url.substring(0, end) : url;
        } catch (Exception e) {
            return "https://lzizy8.com";
        }
    }
}
