package com.video.controller;

import com.video.common.Result;
import com.video.dto.HistoryVO;
import com.video.dto.ProgressSaveDTO;
import com.video.security.UserContext;
import com.video.service.PlayHistoryService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/history")
@RequiredArgsConstructor
public class PlayHistoryController {

    private final PlayHistoryService playHistoryService;

    /**
     * 保存播放进度
     */
    @PostMapping("/save")
    public Result<?> save(@RequestBody ProgressSaveDTO dto) {
        Long userId = UserContext.getUserId();
        playHistoryService.saveProgress(userId, dto.getVideoId(),
                dto.getEpisodeNumber(), dto.getProgress(), dto.getDuration());
        return Result.ok();
    }

    /**
     * 获取播放历史（含视频详细信息 + 进度）
     */
    @GetMapping("/list")
    public Result<List<HistoryVO>> list() {
        Long userId = UserContext.getUserId();
        return Result.ok(playHistoryService.getUserHistoryVOs(userId));
    }

    /**
     * 删除播放记录
     */
    @DeleteMapping("/{id}")
    public Result<?> remove(@PathVariable Long id) {
        Long userId = UserContext.getUserId();
        playHistoryService.removeHistory(userId, id);
        return Result.ok();
    }
}
