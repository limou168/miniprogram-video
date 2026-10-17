package com.video.service;

import com.baomidou.mybatisplus.extension.service.IService;
import com.video.dto.VideoSourceVO;
import com.video.entity.VideoSource;

import java.util.List;

public interface VideoSourceService extends IService<VideoSource> {

    /**
     * 获取视频的播放源列表
     * @param videoId 视频ID
     * @param episodeNumber 集数(0表示正片)
     */
    List<VideoSourceVO> getSources(Long videoId, Integer episodeNumber);
}
