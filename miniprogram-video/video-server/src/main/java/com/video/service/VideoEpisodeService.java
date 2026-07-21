package com.video.service;

import com.baomidou.mybatisplus.extension.service.IService;
import com.video.dto.EpisodeVO;
import com.video.entity.VideoEpisode;

import java.util.List;

public interface VideoEpisodeService extends IService<VideoEpisode> {

    /**
     * 获取视频的分集列表
     */
    List<EpisodeVO> getEpisodesByVideoId(Long videoId);
}
