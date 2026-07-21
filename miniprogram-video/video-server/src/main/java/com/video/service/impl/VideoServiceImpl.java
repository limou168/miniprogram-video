package com.video.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.video.common.BusinessException;
import com.video.dto.PageResult;
import com.video.dto.VideoCardVO;
import com.video.dto.VideoVO;
import com.video.entity.Category;
import com.video.entity.Video;
import com.video.mapper.VideoMapper;
import com.video.service.CategoryService;
import com.video.service.VideoEpisodeService;
import com.video.service.VideoService;
import lombok.RequiredArgsConstructor;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.stereotype.Service;
import org.springframework.util.StringUtils;

import java.util.List;
import java.util.Map;
import java.util.concurrent.TimeUnit;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class VideoServiceImpl extends ServiceImpl<VideoMapper, Video> implements VideoService {

    private final CategoryService categoryService;
    private final VideoEpisodeService videoEpisodeService;
    private final RedisTemplate<String, Object> redisTemplate;

    private static final String DETAIL_CACHE_PREFIX = "video:detail:";
    private static final String HOT_CACHE_KEY = "video:hot";
    private static final long DETAIL_CACHE_TTL = 1; // 1小时
    private static final long HOT_CACHE_TTL = 10; // 10分钟

    @Override
    public PageResult<VideoCardVO> getVideoList(Integer page, Integer size, Long categoryId,
                                                 String keyword, Integer year, String orderBy) {
        LambdaQueryWrapper<Video> wrapper = new LambdaQueryWrapper<Video>()
                .eq(Video::getStatus, 1);

        // 分类筛选
        if (categoryId != null && categoryId > 0) {
            wrapper.eq(Video::getCategoryId, categoryId);
        }

        // 年份筛选
        if (year != null && year > 0) {
            wrapper.eq(Video::getYear, year);
        }

        // 关键词搜索
        if (StringUtils.hasText(keyword)) {
            wrapper.like(Video::getTitle, keyword);
        }

        // 排序
        if ("score".equals(orderBy)) {
            wrapper.orderByDesc(Video::getScore);
        } else if ("time".equals(orderBy)) {
            wrapper.orderByDesc(Video::getCreateTime);
        } else {
            // 默认按播放量排序
            wrapper.orderByDesc(Video::getPlayCount);
        }

        Page<Video> videoPage = page(new Page<>(page, size), wrapper);

        // 获取分类名称映射
        Map<Long, String> categoryMap = getCategoryNameMap();

        List<VideoCardVO> records = videoPage.getRecords().stream()
                .map(v -> VideoCardVO.builder()
                        .id(v.getId())
                        .title(v.getTitle())
                        .coverUrl(v.getCoverUrl())
                        .categoryName(categoryMap.getOrDefault(v.getCategoryId(), ""))
                        .year(v.getYear())
                        .duration(v.getDuration())
                        .score(v.getScore())
                        .playCount(v.getPlayCount())
                        .build())
                .collect(Collectors.toList());

        return PageResult.of(videoPage.getTotal(), page, size, records);
    }

    @Override
    @SuppressWarnings("unchecked")
    public VideoVO getVideoDetail(Long id) {
        // 先查 Redis 缓存
        String cacheKey = DETAIL_CACHE_PREFIX + id;
        Object cached = redisTemplate.opsForValue().get(cacheKey);
        if (cached instanceof VideoVO) {
            // 异步更新播放量（简单实现：直接 DB +1）
            Video video = getById(id);
            if (video != null) {
                video.setPlayCount((video.getPlayCount() == null ? 0 : video.getPlayCount()) + 1);
                updateById(video);
            }
            return (VideoVO) cached;
        }

        Video video = getById(id);
        if (video == null || video.getStatus() == 0) {
            throw new BusinessException(404, "影视不存在或已下架");
        }

        // 更新播放量
        video.setPlayCount((video.getPlayCount() == null ? 0 : video.getPlayCount()) + 1);
        updateById(video);

        // 获取分类名称
        Map<Long, String> categoryMap = getCategoryNameMap();

        VideoVO vo = VideoVO.builder()
                .id(video.getId())
                .title(video.getTitle())
                .categoryId(video.getCategoryId())
                .categoryName(categoryMap.getOrDefault(video.getCategoryId(), ""))
                .coverUrl(video.getCoverUrl())
                .videoUrl(video.getVideoUrl())
                .description(video.getDescription())
                .director(video.getDirector())
                .actors(video.getActors())
                .year(video.getYear())
                .area(video.getArea())
                .duration(video.getDuration())
                .score(video.getScore())
                .tags(video.getTags())
                .playCount(video.getPlayCount())
                .isRecommend(video.getIsRecommend())
                .build();

        // 若为电视剧，填充分集列表
        if (video.getCategoryId() != null && video.getCategoryId() == 2) {
            vo.setEpisodes(videoEpisodeService.getEpisodesByVideoId(id));
        }

        // 写入 Redis 缓存
        redisTemplate.opsForValue().set(cacheKey, vo, DETAIL_CACHE_TTL, TimeUnit.HOURS);

        return vo;
    }

    @Override
    @SuppressWarnings("unchecked")
    public PageResult<VideoCardVO> getHotVideos() {
        // 先查 Redis
        Object cached = redisTemplate.opsForValue().get(HOT_CACHE_KEY);
        if (cached instanceof List) {
            List<VideoCardVO> list = (List<VideoCardVO>) cached;
            return PageResult.of(list.size(), 1, list.size(), list);
        }

        // 按播放量排序取前 20
        return getVideoList(1, 20, null, null, null, "play_count");
    }

    @Override
    public PageResult<VideoCardVO> search(String keyword, Integer page, Integer size) {
        if (!StringUtils.hasText(keyword)) {
            return PageResult.of(0, page, size, List.of());
        }
        return getVideoList(page, size, null, keyword, null, null);
    }

    /**
     * 获取分类 ID → 名称映射
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
