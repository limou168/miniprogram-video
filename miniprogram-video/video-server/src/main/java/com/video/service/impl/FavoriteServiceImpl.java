package com.video.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.video.dto.FavoriteVO;
import com.video.entity.Category;
import com.video.entity.Favorite;
import com.video.entity.Video;
import com.video.mapper.FavoriteMapper;
import com.video.mapper.VideoMapper;
import com.video.service.CategoryService;
import com.video.service.FavoriteService;
import lombok.RequiredArgsConstructor;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.concurrent.TimeUnit;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class FavoriteServiceImpl extends ServiceImpl<FavoriteMapper, Favorite> implements FavoriteService {

    private final RedisTemplate<String, Object> redisTemplate;
    private final CategoryService categoryService;
    private final VideoMapper videoMapper;

    private static final String FAVORITE_LIST_CACHE_PREFIX = "favorite:list:";
    private static final String FAVORITE_CHECK_CACHE_PREFIX = "favorite:check:";
    private static final long FAVORITE_CACHE_TTL = 10; // 10分钟

    @Override
    @Transactional
    public boolean toggle(Long userId, Long videoId) {
        Favorite existing = getOne(new LambdaQueryWrapper<Favorite>()
                .eq(Favorite::getUserId, userId)
                .eq(Favorite::getVideoId, videoId));

        // 清除缓存
        clearFavoriteCache(userId, videoId);

        if (existing != null) {
            removeById(existing.getId());
            return false; // 取消收藏
        } else {
            Favorite favorite = new Favorite();
            favorite.setUserId(userId);
            favorite.setVideoId(videoId);
            save(favorite);
            return true; // 收藏成功
        }
    }

    @Override
    public boolean isFavorite(Long userId, Long videoId) {
        String cacheKey = FAVORITE_CHECK_CACHE_PREFIX + userId + ":" + videoId;
        Object cached = redisTemplate.opsForValue().get(cacheKey);
        if (cached instanceof Boolean) {
            return (Boolean) cached;
        }

        boolean result = count(new LambdaQueryWrapper<Favorite>()
                .eq(Favorite::getUserId, userId)
                .eq(Favorite::getVideoId, videoId)) > 0;

        // 写入缓存
        redisTemplate.opsForValue().set(cacheKey, result, FAVORITE_CACHE_TTL, TimeUnit.MINUTES);

        return result;
    }

    @Override
    public List<Favorite> getUserFavorites(Long userId) {
        return list(new LambdaQueryWrapper<Favorite>()
                .eq(Favorite::getUserId, userId)
                .orderByDesc(Favorite::getCreateTime));
    }

    @Override
    @SuppressWarnings("unchecked")
    public List<FavoriteVO> getUserFavoriteVOs(Long userId) {
        // 先查 Redis 缓存
        String cacheKey = FAVORITE_LIST_CACHE_PREFIX + userId;
        Object cached = redisTemplate.opsForValue().get(cacheKey);
        if (cached instanceof List) {
            return (List<FavoriteVO>) cached;
        }

        // 查数据库
        List<Favorite> favorites = getUserFavorites(userId);
        if (favorites.isEmpty()) {
            return Collections.emptyList();
        }

        // 批量查询视频信息
        List<Long> videoIds = favorites.stream()
                .map(Favorite::getVideoId)
                .collect(Collectors.toList());

        Map<Long, Video> videoMap = listVideoMap(videoIds);

        // 获取分类映射
        Map<Long, String> categoryMap = getCategoryNameMap();

        List<FavoriteVO> list = favorites.stream()
                .map(f -> {
                    Video v = videoMap.get(f.getVideoId());
                    if (v == null) return null;
                    return FavoriteVO.builder()
                            .id(f.getId())
                            .videoId(f.getVideoId())
                            .videoTitle(v.getTitle())
                            .coverUrl(v.getCoverUrl())
                            .score(v.getScore())
                            .year(v.getYear())
                            .duration(v.getDuration())
                            .categoryName(categoryMap.getOrDefault(v.getCategoryId(), ""))
                            .createTime(f.getCreateTime())
                            .build();
                })
                .filter(java.util.Objects::nonNull)
                .collect(Collectors.toList());

        // 写入 Redis 缓存
        redisTemplate.opsForValue().set(cacheKey, list, FAVORITE_CACHE_TTL, TimeUnit.MINUTES);

        return list;
    }

    /**
     * 清除收藏相关的所有缓存
     */
    private void clearFavoriteCache(Long userId, Long videoId) {
        redisTemplate.delete(FAVORITE_LIST_CACHE_PREFIX + userId);
        redisTemplate.delete(FAVORITE_CHECK_CACHE_PREFIX + userId + ":" + videoId);
    }

    /**
     * 批量查询视频
     */
    private Map<Long, Video> listVideoMap(List<Long> ids) {
        if (ids.isEmpty()) return Collections.emptyMap();
        List<Video> videos = videoMapper.selectBatchIds(ids);
        return videos.stream().collect(Collectors.toMap(Video::getId, v -> v, (a, b) -> a));
    }

    /**
     * 获取分类名称映射
     */
    private Map<Long, String> getCategoryNameMap() {
        return categoryService.listAll().stream()
                .collect(Collectors.toMap(
                        c -> c.getId(),
                        c -> c.getName(),
                        (a, b) -> a
                ));
    }
}
