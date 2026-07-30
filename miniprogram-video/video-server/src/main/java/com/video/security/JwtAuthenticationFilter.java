package com.video.security;

import com.video.common.JwtUtil;
import jakarta.servlet.*;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.stereotype.Component;
import org.springframework.util.StringUtils;

import java.io.IOException;
import java.util.List;

/**
 * JWT 认证过滤器
 */
@Slf4j
@Component
@RequiredArgsConstructor
public class JwtAuthenticationFilter implements Filter {

    private final JwtUtil jwtUtil;
    @Autowired(required = false)
    private RedisTemplate<String, Object> redisTemplate;

    // 不需要认证的路径
    private static final List<String> EXCLUDE_PATHS = List.of(
            "/api/user/login",
            "/api/user/register",
            "/api/category/",
            "/api/video/list"
    );

    private static final String TOKEN_PREFIX = "token:";
    private static final String AUTH_HEADER = "Authorization";
    private static final String BEARER_PREFIX = "Bearer ";

    @Override
    public void doFilter(ServletRequest request, ServletResponse response, FilterChain chain)
            throws IOException, ServletException {

        HttpServletRequest httpRequest = (HttpServletRequest) request;
        String path = httpRequest.getRequestURI();

        // 检查是否在白名单中
        if (isExcluded(path)) {
            chain.doFilter(request, response);
            return;
        }

        // 处理 OPTIONS 预检请求
        if ("OPTIONS".equalsIgnoreCase(httpRequest.getMethod())) {
            chain.doFilter(request, response);
            return;
        }

        // 从 Header 中获取 token
        String token = extractToken(httpRequest);
        if (token == null) {
            sendUnauthorized(response, "未登录，请先登录");
            return;
        }

        // 验证 token
        if (!jwtUtil.validateToken(token)) {
            sendUnauthorized(response, "登录已过期，请重新登录");
            return;
        }

        // 从 token 解析用户 ID
        Long userId = jwtUtil.getUserIdFromToken(token);

        // 检查 Redis 中 token 是否还存在（Redis 不可用时仅验证 JWT 本身）
        if (redisTemplate != null) {
            String redisToken = (String) redisTemplate.opsForValue().get(TOKEN_PREFIX + userId);
            if (redisToken == null || !redisToken.equals(token)) {
                sendUnauthorized(response, "登录已过期，请重新登录");
                return;
            }
        }

        // 设置用户上下文
        UserContext.setUserId(userId);

        try {
            chain.doFilter(request, response);
        } finally {
            // 清理 ThreadLocal
            UserContext.remove();
        }
    }

    private boolean isExcluded(String path) {
        return EXCLUDE_PATHS.stream().anyMatch(path::startsWith);
    }

    private String extractToken(HttpServletRequest request) {
        String header = request.getHeader(AUTH_HEADER);
        if (StringUtils.hasText(header) && header.startsWith(BEARER_PREFIX)) {
            return header.substring(BEARER_PREFIX.length());
        }
        return null;
    }

    private void sendUnauthorized(ServletResponse response, String message) throws IOException {
        HttpServletResponse httpResponse = (HttpServletResponse) response;
        httpResponse.setStatus(HttpServletResponse.SC_UNAUTHORIZED);
        httpResponse.setContentType("application/json;charset=UTF-8");
        httpResponse.getWriter().write("{\"code\":401,\"message\":\"" + message + "\",\"data\":null}");
    }
}
