package com.video.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.video.dto.EpisodeVO;
import com.video.entity.VideoEpisode;
import com.video.mapper.VideoEpisodeMapper;
import com.video.service.VideoEpisodeService;
import lombok.RequiredArgsConstructor;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.concurrent.TimeUnit;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class VideoEpisodeServiceImpl extends ServiceImpl<VideoEpisodeMapper, VideoEpisode> implements VideoEpisodeService {

    private final RedisTemplate<String, Object> redisTemplate;

    private static final String EPISODES_CACHE_PREFIX = "video:episodes:";
    private static final long EPISODES_CACHE_TTL = 1; // 1小时

    @Override
    @SuppressWarnings("unchecked")
    public List<EpisodeVO> getEpisodesByVideoId(Long videoId) {
        // 先查 Redis 缓存
        String cacheKey = EPISODES_CACHE_PREFIX + videoId;
        Object cached = redisTemplate.opsForValue().get(cacheKey);
        if (cached instanceof List) {
            return (List<EpisodeVO>) cached;
        }

        // 查数据库
        List<EpisodeVO> list = list(new LambdaQueryWrapper<VideoEpisode>()
                .eq(VideoEpisode::getVideoId, videoId)
                .orderByAsc(VideoEpisode::getEpisodeNumber))
                .stream()
                .map(e -> EpisodeVO.builder()
                        .id(e.getId())
                        .episodeNumber(e.getEpisodeNumber())
                        .episodeTitle(e.getEpisodeTitle())
                        .videoUrl(e.getVideoUrl())
                        .duration(e.getDuration())
                        .build())
                .collect(Collectors.toList());

        // 写入 Redis 缓存
        redisTemplate.opsForValue().set(cacheKey, list, EPISODES_CACHE_TTL, TimeUnit.HOURS);

        return list;
    }
}
