package com.video.dto;

import lombok.Data;

/**
 * 保存播放进度请求 DTO
 */
@Data
public class ProgressSaveDTO {

    private Long videoId;
    private Integer episodeNumber;
    private Integer progress;
    private Integer duration;
}
