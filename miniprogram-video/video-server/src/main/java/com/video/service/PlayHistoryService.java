package com.video.service;

import com.baomidou.mybatisplus.extension.service.IService;
import com.video.dto.HistoryVO;
import com.video.entity.PlayHistory;

import java.util.List;

public interface PlayHistoryService extends IService<PlayHistory> {

    /**
     * 保存/更新播放进度
     */
    void saveProgress(Long userId, Long videoId, Integer episodeNumber, Integer progress, Integer duration);

    /**
     * 获取用户播放历史
     */
    List<PlayHistory> getUserHistory(Long userId);

    /**
     * 获取播放历史（含视频详细信息 + 进度）
     */
    List<HistoryVO> getUserHistoryVOs(Long userId);

    /**
     * 删除播放记录
     */
    void removeHistory(Long userId, Long historyId);
}
