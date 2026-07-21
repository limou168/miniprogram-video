package com.video.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.video.common.BusinessException;
import com.video.dto.HistoryVO;
import com.video.entity.PlayHistory;
import com.video.entity.Video;
import com.video.mapper.PlayHistoryMapper;
import com.video.mapper.VideoMapper;
import com.video.service.PlayHistoryService;
import lombok.RequiredArgsConstructor;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.concurrent.TimeUnit;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class PlayHistoryServiceImpl extends ServiceImpl<PlayHistoryMapper, PlayHistory> implements PlayHistoryService {

    private final RedisTemplate<String, Object> redisTemplate;
    private final VideoMapper videoMapper;

    private static final String HISTORY_LIST_CACHE_PREFIX = "history:list:";
    private static final long HISTORY_CACHE_TTL = 10; // 10分钟

    @Override
    @Transactional
    public void saveProgress(Long userId, Long videoId, Integer episodeNumber, Integer progress, Integer duration) {
        // 查找是否已有记录（同一用户+同一视频+同一分集）
        LambdaQueryWrapper<PlayHistory> wrapper = new LambdaQueryWrapper<PlayHistory>()
                .eq(PlayHistory::getUserId, userId)
                .eq(PlayHistory::getVideoId, videoId)
                .eq(PlayHistory::getEpisodeNumber, episodeNumber != null ? episodeNumber : 0);

        PlayHistory existing = getOne(wrapper);

        if (existing != null) {
            existing.setProgress(progress);
            existing.setDuration(duration);
            existing.setPlayTime(LocalDateTime.now());
            updateById(existing);
        } else {
            PlayHistory history = new PlayHistory();
            history.setUserId(userId);
            history.setVideoId(videoId);
            history.setEpisodeNumber(episodeNumber != null ? episodeNumber : 0);
            history.setProgress(progress);
            history.setDuration(duration);
            history.setPlayTime(LocalDateTime.now());
            save(history);
        }

        // 清除缓存
        redisTemplate.delete(HISTORY_LIST_CACHE_PREFIX + userId);
    }

    @Override
    public List<PlayHistory> getUserHistory(Long userId) {
        return list(new LambdaQueryWrapper<PlayHistory>()
                .eq(PlayHistory::getUserId, userId)
                .orderByDesc(PlayHistory::getPlayTime));
    }

    @Override
    @SuppressWarnings("unchecked")
    public List<HistoryVO> getUserHistoryVOs(Long userId) {
        // 先查 Redis 缓存
        String cacheKey = HISTORY_LIST_CACHE_PREFIX + userId;
        Object cached = redisTemplate.opsForValue().get(cacheKey);
        if (cached instanceof List) {
            return (List<HistoryVO>) cached;
        }

        // 查数据库
        List<PlayHistory> historyList = getUserHistory(userId);
        if (historyList.isEmpty()) {
            return Collections.emptyList();
        }

        // 批量查询视频信息
        List<Long> videoIds = historyList.stream()
                .map(PlayHistory::getVideoId)
                .distinct()
                .collect(Collectors.toList());

        Map<Long, Video> videoMap = getVideoMap(videoIds);

        List<HistoryVO> list = historyList.stream()
                .map(h -> {
                    Video v = videoMap.get(h.getVideoId());
                    if (v == null) return null;
                    int totalDuration = h.getDuration() != null && h.getDuration() > 0 ? h.getDuration() : 1;
                    int progressPercent = Math.min(100, (h.getProgress() != null ? h.getProgress() : 0) * 100 / totalDuration);
                    return HistoryVO.builder()
                            .id(h.getId())
                            .videoId(h.getVideoId())
                            .videoTitle(v.getTitle())
                            .coverUrl(v.getCoverUrl())
                            .score(v.getScore())
                            .duration(v.getDuration())
                            .episodeNumber(h.getEpisodeNumber())
                            .progress(h.getProgress())
                            .totalDuration(h.getDuration())
                            .progressPercent(progressPercent)
                            .playTime(h.getPlayTime())
                            .build();
                })
                .filter(java.util.Objects::nonNull)
                .collect(Collectors.toList());

        // 写入 Redis 缓存
        redisTemplate.opsForValue().set(cacheKey, list, HISTORY_CACHE_TTL, TimeUnit.MINUTES);

        return list;
    }

    @Override
    @Transactional
    public void removeHistory(Long userId, Long historyId) {
        PlayHistory history = getById(historyId);
        if (history == null || !history.getUserId().equals(userId)) {
            throw new BusinessException("记录不存在");
        }
        removeById(historyId);

        // 清除缓存
        redisTemplate.delete(HISTORY_LIST_CACHE_PREFIX + userId);
    }

    /**
     * 批量查询视频映射
     */
    private Map<Long, Video> getVideoMap(List<Long> ids) {
        if (ids.isEmpty()) return Collections.emptyMap();
        List<Video> videos = videoMapper.selectBatchIds(ids);
        return videos.stream().collect(Collectors.toMap(Video::getId, v -> v, (a, b) -> a));
    }
}
