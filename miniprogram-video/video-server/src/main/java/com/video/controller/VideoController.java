package com.video.controller;

import com.video.common.Result;
import com.video.dto.EpisodeVO;
import com.video.dto.PageResult;
import com.video.dto.VideoCardVO;
import com.video.dto.VideoSourceVO;
import com.video.dto.VideoVO;
import com.video.service.VideoEpisodeService;
import com.video.service.VideoService;
import com.video.service.VideoSourceService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/video")
@RequiredArgsConstructor
public class VideoController {

    private final VideoService videoService;
    private final VideoEpisodeService videoEpisodeService;
    private final VideoSourceService videoSourceService;

    /**
     * 分页获取影视列表
     */
    @GetMapping("/list")
    public Result<PageResult<VideoCardVO>> list(
            @RequestParam(defaultValue = "1") Integer page,
            @RequestParam(defaultValue = "20") Integer size,
            @RequestParam(required = false) Long categoryId,
            @RequestParam(required = false) String keyword,
            @RequestParam(required = false) String tag,
            @RequestParam(required = false) String excludeTag,
            @RequestParam(required = false) Integer year,
            @RequestParam(required = false, defaultValue = "play_count") String orderBy) {
        return Result.ok(videoService.getVideoList(page, size, categoryId, keyword, tag, excludeTag, year, orderBy));
    }

    /**
     * 影视详情
     */
    @GetMapping("/{id}")
    public Result<VideoVO> detail(@PathVariable Long id) {
        
        return Result.ok(videoService.getVideoDetail(id)
        );
    }

    /**
     * 热门推荐
     */
    @GetMapping("/hot")
    public Result<PageResult<VideoCardVO>> hot() {
        return Result.ok(videoService.getHotVideos());
    }

    /**
     * 搜索（使用 MySQL FULLTEXT 中文分词，搜索标题/导演/演员/标签/简介）
     */
    @GetMapping("/search")
    public Result<PageResult<VideoCardVO>> search(
            @RequestParam String keyword,
            @RequestParam(defaultValue = "1") Integer page,
            @RequestParam(defaultValue = "20") Integer size) {
        return Result.ok(videoService.search(keyword, page, size));
    }

    /**
     * 搜索建议（输入时下拉提示，仅匹配标题）
     */
    @GetMapping("/search/suggest")
    public Result<List<String>> suggest(
            @RequestParam String keyword,
            @RequestParam(defaultValue = "10") Integer limit) {
        return Result.ok(videoService.searchSuggestions(keyword, limit));
    }

    /**
     * 获取分集列表
     */
    @GetMapping("/{id}/episodes")
    public Result<List<EpisodeVO>> episodes(@PathVariable Long id) {
        return Result.ok(videoEpisodeService.getEpisodesByVideoId(id));
    }

    /**
     * 获取视频播放源列表（支持多线路）
     */
    @GetMapping("/{id}/sources")
    public Result<List<VideoSourceVO>> sources(
            @PathVariable Long id,
            @RequestParam(defaultValue = "0") Integer episodeNumber) {
        return Result.ok(videoSourceService.getSources(id, episodeNumber));
    }

    /**
     * 获取指定分类下的标签列表（用作二级分类）
     */
    @GetMapping("/tags")
    public Result<List<String>> tags(@RequestParam Long categoryId) {
        return Result.ok(videoService.getTagsByCategory(categoryId));
    }
}
