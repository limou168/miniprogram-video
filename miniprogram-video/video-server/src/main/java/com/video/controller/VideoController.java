package com.video.controller;

import com.video.common.Result;
import com.video.dto.EpisodeVO;
import com.video.dto.PageResult;
import com.video.dto.VideoCardVO;
import com.video.dto.VideoVO;
import com.video.service.VideoEpisodeService;
import com.video.service.VideoService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/video")
@RequiredArgsConstructor
public class VideoController {

    private final VideoService videoService;
    private final VideoEpisodeService videoEpisodeService;

    /**
     * 分页获取影视列表
     */
    @GetMapping("/list")
    public Result<PageResult<VideoCardVO>> list(
            @RequestParam(defaultValue = "1") Integer page,
            @RequestParam(defaultValue = "20") Integer size,
            @RequestParam(required = false) Long categoryId,
            @RequestParam(required = false) String keyword,
            @RequestParam(required = false) Integer year,
            @RequestParam(required = false, defaultValue = "play_count") String orderBy) {
        return Result.ok(videoService.getVideoList(page, size, categoryId, keyword, year, orderBy));
    }

    /**
     * 影视详情
     */
    @GetMapping("/{id}")
    public Result<VideoVO> detail(@PathVariable Long id) {
        return Result.ok(videoService.getVideoDetail(id));
    }

    /**
     * 热门推荐
     */
    @GetMapping("/hot")
    public Result<PageResult<VideoCardVO>> hot() {
        return Result.ok(videoService.getHotVideos());
    }

    /**
     * 搜索
     */
    @GetMapping("/search")
    public Result<PageResult<VideoCardVO>> search(
            @RequestParam String keyword,
            @RequestParam(defaultValue = "1") Integer page,
            @RequestParam(defaultValue = "20") Integer size) {
        return Result.ok(videoService.search(keyword, page, size));
    }

    /**
     * 获取分集列表
     */
    @GetMapping("/{id}/episodes")
    public Result<List<EpisodeVO>> episodes(@PathVariable Long id) {
        return Result.ok(videoEpisodeService.getEpisodesByVideoId(id));
    }
}
