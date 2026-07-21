package com.video.controller;

import com.video.common.Result;
import com.video.dto.FavoriteVO;
import com.video.security.UserContext;
import com.video.service.FavoriteService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/favorite")
@RequiredArgsConstructor
public class FavoriteController {

    private final FavoriteService favoriteService;

    /**
     * 收藏/取消收藏
     */
    @PostMapping("/toggle/{videoId}")
    public Result<Boolean> toggle(@PathVariable Long videoId) {
        Long userId = UserContext.getUserId();
        boolean isFav = favoriteService.toggle(userId, videoId);
        return Result.ok(isFav);
    }

    /**
     * 是否已收藏
     */
    @GetMapping("/check/{videoId}")
    public Result<Boolean> check(@PathVariable Long videoId) {
        Long userId = UserContext.getUserId();
        return Result.ok(favoriteService.isFavorite(userId, videoId));
    }

    /**
     * 获取收藏列表（含视频详细信息）
     */
    @GetMapping("/list")
    public Result<List<FavoriteVO>> list() {
        Long userId = UserContext.getUserId();
        return Result.ok(favoriteService.getUserFavoriteVOs(userId));
    }
}
