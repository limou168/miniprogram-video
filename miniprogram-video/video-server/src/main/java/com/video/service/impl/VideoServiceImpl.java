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
import com.video.service.CosService;
import com.video.service.VideoEpisodeService;
import com.video.service.VideoService;
import com.video.service.VideoSourceService;
import lombok.RequiredArgsConstructor;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.stereotype.Service;
import org.springframework.util.StringUtils;

import java.util.Arrays;
import java.util.List;
import java.util.Map;
import java.util.concurrent.TimeUnit;
import java.util.regex.Pattern;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class VideoServiceImpl extends ServiceImpl<VideoMapper, Video> implements VideoService {

    private static final Logger log = LoggerFactory.getLogger(VideoServiceImpl.class);

    private final CategoryService categoryService;
    private final VideoEpisodeService videoEpisodeService;
    private final VideoSourceService videoSourceService;
    private final CosService cosService;
    private final VideoMapper videoMapper;
    @Autowired(required = false)
    private RedisTemplate<String, Object> redisTemplate;

    private static final String DETAIL_CACHE_PREFIX = "video:detail:";
    private static final String HOT_CACHE_KEY = "video:hot";
    private static final long DETAIL_CACHE_TTL = 1; // 1小时
    private static final long HOT_CACHE_TTL = 10; // 10分钟

    @Override
    public PageResult<VideoCardVO> getVideoList(Integer page, Integer size, Long categoryId,
                                                 String keyword, String tag, String excludeTag,
                                                 Integer year, String orderBy) {
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

        // 子分类标签筛选（模糊匹配 tags 字段，如 %动作% 可匹配 "动作,冒险"、"剧情,动作" 等）
        if (StringUtils.hasText(tag)) {
            wrapper.like(Video::getTags, tag);
        }

        // 排除含特定标签的内容（默认过滤情色类）
        if (StringUtils.hasText(excludeTag)) {
            wrapper.notLike(Video::getTags, excludeTag);
        }

        // 关键词搜索
        if (StringUtils.hasText(keyword)) {
            wrapper.and(w -> w.like(Video::getTitle, keyword)
                             .or(wr -> wr.like(Video::getTags, keyword)));
        }

        // 排序
        if ("score".equals(orderBy)) {
            wrapper.orderByDesc(Video::getScore);
        } else if ("time".equals(orderBy)) {
            wrapper.orderByDesc(Video::getCreateTime);
        } else if ("year".equals(orderBy)) {
            wrapper.orderByDesc(Video::getYear).orderByDesc(Video::getPlayCount);
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
                        .coverUrl(cosService.transformUrl(v.getCoverUrl()))
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
        if (redisTemplate != null) {
            Object cached = redisTemplate.opsForValue().get(cacheKey);
            if (cached instanceof VideoVO) {
                // 异步更新播放量
                Video video = getById(id);
                if (video != null) {
                    video.setPlayCount((video.getPlayCount() == null ? 0 : video.getPlayCount()) + 1);
                    updateById(video);
                }
                return (VideoVO) cached;
            }
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
                .coverUrl(cosService.transformUrl(video.getCoverUrl()))
                .videoUrl(cosService.transformUrl(video.getVideoUrl()))
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

        // 获取播放源（容错：表不存在时不阻塞详情页）
        try {
            vo.setSources(videoSourceService.getSources(id, 0));
        } catch (Exception e) {
            log.warn("获取播放源失败(可能sys_video_source表不存在): {}", e.getMessage());
        }

        // 若为电视剧，填充分集列表
        if (video.getCategoryId() != null && video.getCategoryId() == 2) {
            vo.setEpisodes(videoEpisodeService.getEpisodesByVideoId(id));
        }

        // 写入 Redis 缓存（仅当 Redis 可用时）
        if (redisTemplate != null) {
            redisTemplate.opsForValue().set(cacheKey, vo, DETAIL_CACHE_TTL, TimeUnit.HOURS);
        }

        return vo;
    }

    @Override
    @SuppressWarnings("unchecked")
    public PageResult<VideoCardVO> getHotVideos() {
        // 先查 Redis
        if (redisTemplate != null) {
            Object cached = redisTemplate.opsForValue().get(HOT_CACHE_KEY);
            if (cached instanceof List) {
                List<VideoCardVO> list = (List<VideoCardVO>) cached;
                return PageResult.of(list.size(), 1, list.size(), list);
            }
        }

        // 按播放量排序取前 20
        return getVideoList(1, 20, null, null, null, null, null, "play_count");
    }

    @Override
    public PageResult<VideoCardVO> search(String keyword, Integer page, Integer size) {
        if (!StringUtils.hasText(keyword)) {
            return PageResult.of(0, page, size, List.of());
        }

        // 清理关键词（移除特殊字符，避免 MATCH AGAINST 语法错误）
        String cleanKeyword = keyword.trim()
                .replace("'", "''")
                .replaceAll("[+\\-<>()~*\"@]", " ");

        // 对于太短的关键词（1-2个字符），直接走 LIKE 搜索
        if (cleanKeyword.length() <= 2) {
            LambdaQueryWrapper<Video> wrapper = new LambdaQueryWrapper<Video>()
                    .eq(Video::getStatus, 1)
                    .like(Video::getTitle, cleanKeyword);
            Page<Video> videoPage = page(new Page<>(page, size), wrapper);
            return buildSearchResult(videoPage, page, size);
        }

        // 构建 MATCH AGAINST 的布尔模式关键词
        // 每个词加 + 表示必须包含，用 * 支持前缀匹配
        String ftKeyword = Arrays.stream(cleanKeyword.split("\\s+"))
                .filter(w -> w.length() > 0)
                .map(w -> "+" + w + "*")
                .collect(Collectors.joining(" "));

        try {
            // 尝试全文搜索
            Page<Video> videoPage = new Page<>(page, size);
            videoMapper.searchFulltext(videoPage, ftKeyword);

            // 如果全文搜索没有结果，回退到 LIKE 搜索
            if (videoPage.getRecords() == null || videoPage.getRecords().isEmpty()) {
                log.debug("全文搜索无结果，回退到 LIKE 搜索: {}", cleanKeyword);
                Page<Video> likePage = new Page<>(page, size);
                videoMapper.searchLike(likePage, cleanKeyword);
                return buildSearchResult(likePage, page, size);
            }

            return buildSearchResult(videoPage, page, size);
        } catch (Exception e) {
            // FULLTEXT 搜索异常时回退到 LIKE
            log.warn("全文搜索异常 ({}), 回退到 LIKE 搜索", e.getMessage());
            Page<Video> likePage = new Page<>(page, size);
            videoMapper.searchLike(likePage, cleanKeyword);
            return buildSearchResult(likePage, page, size);
        }
    }

    @Override
    public List<String> searchSuggestions(String keyword, Integer limit) {
        if (!StringUtils.hasText(keyword)) {
            return List.of();
        }

        if (limit == null || limit <= 0) {
            limit = 10;
        }

        String cleanKeyword = keyword.trim()
                .replace("'", "''")
                .replaceAll("[+\\-<>()~*\"@]", " ");

        // 太短的词直接用 LIKE
        if (cleanKeyword.length() <= 2) {
            LambdaQueryWrapper<Video> wrapper = new LambdaQueryWrapper<Video>()
                    .eq(Video::getStatus, 1)
                    .like(Video::getTitle, cleanKeyword)
                    .orderByDesc(Video::getPlayCount)
                    .last("LIMIT " + limit);
            return list(wrapper).stream()
                    .map(Video::getTitle)
                    .distinct()
                    .collect(Collectors.toList());
        }

        try {
            String ftKeyword = Arrays.stream(cleanKeyword.split("\\s+"))
                    .filter(w -> w.length() > 0)
                    .map(w -> "+" + w + "*")
                    .collect(Collectors.joining(" "));
            return videoMapper.searchSuggestions(ftKeyword, limit);
        } catch (Exception e) {
            log.warn("搜索建议异常 ({}), 回退到 LIKE", e.getMessage());
            LambdaQueryWrapper<Video> wrapper = new LambdaQueryWrapper<Video>()
                    .eq(Video::getStatus, 1)
                    .like(Video::getTitle, cleanKeyword)
                    .orderByDesc(Video::getPlayCount)
                    .last("LIMIT " + limit);
            return list(wrapper).stream()
                    .map(Video::getTitle)
                    .distinct()
                    .collect(Collectors.toList());
        }
    }

    @Override
    public List<String> getTagsByCategory(Long categoryId) {
        String cacheKey = "video:tags:" + categoryId;
        if (redisTemplate != null) {
            Object cached = redisTemplate.opsForValue().get(cacheKey);
            if (cached instanceof List) {
                return (List<String>) cached;
            }
        }

        List<Video> videos = list(new LambdaQueryWrapper<Video>()
                .eq(Video::getCategoryId, categoryId)
                .eq(Video::getStatus, 1)
                .isNotNull(Video::getTags)
                .ne(Video::getTags, "")
                .select(Video::getTags));

        // 多分隔符拆分：逗号、中文逗号、斜杠/中文斜杠、顿号、空格
        // 然后过滤：去空、去英文、去超过2个字符长的残留、去重
        java.util.regex.Pattern separator = java.util.regex.Pattern.compile("[,\\/、，／\\s]+");
        java.util.regex.Pattern alphaOnly = java.util.regex.Pattern.compile("^[a-zA-Z\\s\\-0-9]+$");
        java.util.regex.Pattern tooShort = java.util.regex.Pattern.compile("^[a-zA-Z]{1,2}$"); // 只过滤1-2字母的英文残留

        List<String> tags = videos.stream()
                .map(Video::getTags)
                .filter(t -> t != null && !t.trim().isEmpty())
                .flatMap(t -> separator.splitAsStream(t))
                .map(String::trim)
                .filter(t -> !t.isEmpty())                 // 去空
                .filter(t -> !alphaOnly.matcher(t).matches())  // 去纯字母/数字
                .filter(t -> !tooShort.matcher(t).matches())   // 去1-2个字符的残留
                .filter(t -> t.length() < 15)               // 去超长脏数据
                .distinct()
                .sorted()
                .collect(Collectors.toList());

        if (redisTemplate != null) {
            redisTemplate.opsForValue().set(cacheKey, tags, 30, TimeUnit.MINUTES);
        }

        return tags;
    }

    // ==================== 私有方法 ====================

    /**
     * 构建搜索结果的 VO
     */
    private PageResult<VideoCardVO> buildSearchResult(Page<Video> videoPage, Integer page, Integer size) {
        Map<Long, String> categoryMap = getCategoryNameMap();

        List<VideoCardVO> records = videoPage.getRecords().stream()
                .map(v -> VideoCardVO.builder()
                        .id(v.getId())
                        .title(v.getTitle())
                        .coverUrl(cosService.transformUrl(v.getCoverUrl()))
                        .categoryName(categoryMap.getOrDefault(v.getCategoryId(), ""))
                        .year(v.getYear())
                        .duration(v.getDuration())
                        .score(v.getScore())
                        .playCount(v.getPlayCount())
                        .build())
                .collect(Collectors.toList());

        return PageResult.of(videoPage.getTotal(), page, size, records);
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
