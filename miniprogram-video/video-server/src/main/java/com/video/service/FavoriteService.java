package com.video.service;

import com.baomidou.mybatisplus.extension.service.IService;
import com.video.dto.FavoriteVO;
import com.video.entity.Favorite;

import java.util.List;

public interface FavoriteService extends IService<Favorite> {

    /**
     * 收藏/取消收藏
     */
    boolean toggle(Long userId, Long videoId);

    /**
     * 判断是否已收藏
     */
    boolean isFavorite(Long userId, Long videoId);

    /**
     * 获取收藏列表
     */
    List<Favorite> getUserFavorites(Long userId);

    /**
     * 获取收藏列表（含视频详细信息）
     */
    List<FavoriteVO> getUserFavoriteVOs(Long userId);
}
