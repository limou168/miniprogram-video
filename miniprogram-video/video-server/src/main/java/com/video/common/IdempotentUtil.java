package com.video.common;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.stereotype.Component;

import java.util.concurrent.TimeUnit;

/**
 * 幂等性工具（防止重复提交）
 */
@Component
public class IdempotentUtil {

    @Autowired(required = false)
    private RedisTemplate<String, Object> redisTemplate;

    private static final String IDEMPOTENT_PREFIX = "idempotent:";
    private static final long DEFAULT_TTL = 10; // 10秒内重复key视为重复

    /**
     * 检查是否重复请求
     * @param key 幂等键（如 userId + ":" + API path）
     * @return true 表示是重复请求，false 表示首次请求
     */
    public boolean isDuplicate(String key) {
        if (redisTemplate == null) {
            return false; // Redis不可用时不校验
        }
        String redisKey = IDEMPOTENT_PREFIX + key;
        Boolean exists = redisTemplate.hasKey(redisKey);
        if (Boolean.TRUE.equals(exists)) {
            return true;
        }
        // 标记已处理
        redisTemplate.opsForValue().set(redisKey, "1", DEFAULT_TTL, TimeUnit.SECONDS);
        return false;
    }

    /**
     * 检查并标记幂等
     */
    public boolean checkAndMark(String key, long ttlSeconds) {
        if (redisTemplate == null) {
            return false;
        }
        String redisKey = IDEMPOTENT_PREFIX + key;
        Boolean exists = redisTemplate.hasKey(redisKey);
        if (Boolean.TRUE.equals(exists)) {
            return true;
        }
        redisTemplate.opsForValue().set(redisKey, "1", ttlSeconds, TimeUnit.SECONDS);
        return false;
    }
}
