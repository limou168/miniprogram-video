package com.video.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.video.dto.CategoryVO;
import com.video.entity.Category;
import com.video.mapper.CategoryMapper;
import com.video.service.CategoryService;
import lombok.RequiredArgsConstructor;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.concurrent.TimeUnit;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class CategoryServiceImpl extends ServiceImpl<CategoryMapper, Category> implements CategoryService {

    @Autowired(required = false)
    private RedisTemplate<String, Object> redisTemplate;
    private static final String CACHE_KEY = "category:list";
    private static final long CACHE_TTL = 30; // 30分钟

    @Override
    @SuppressWarnings("unchecked")
    public List<CategoryVO> listAll() {
        // 先从 Redis 获取
        if (redisTemplate != null) {
            Object cached = redisTemplate.opsForValue().get(CACHE_KEY);
            if (cached instanceof List) {
                return (List<CategoryVO>) cached;
            }
        }

        // 查数据库
        List<CategoryVO> list = list(new LambdaQueryWrapper<Category>()
                .eq(Category::getStatus, 1)
                .orderByAsc(Category::getSortOrder))
                .stream()
                .map(c -> CategoryVO.builder()
                        .id(c.getId())
                        .name(c.getName())
                        .icon(c.getIcon())
                        .build())
                .collect(Collectors.toList());

        // 写入 Redis 缓存（仅当 Redis 可用时）
        if (redisTemplate != null) {
            redisTemplate.opsForValue().set(CACHE_KEY, list, CACHE_TTL, TimeUnit.MINUTES);
        }

        return list;
    }
}
