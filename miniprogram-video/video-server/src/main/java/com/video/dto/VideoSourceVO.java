package com.video.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * 视频播放源 VO
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class VideoSourceVO {
    private Long id;
    private String sourceName;
    private String sourceUrl;
    private Integer episodeNumber;
}
