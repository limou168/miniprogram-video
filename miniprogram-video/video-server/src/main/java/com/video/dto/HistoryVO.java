package com.video.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.math.BigDecimal;
import java.time.LocalDateTime;

/**
 * 播放历史返回 VO（含视频信息 + 进度）
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class HistoryVO {

    private Long id;
    private Long videoId;
    private String videoTitle;
    private String coverUrl;
    private BigDecimal score;
    private String duration;
    private Integer episodeNumber;
    private Integer progress;
    private Integer totalDuration;
    private Integer progressPercent;
    private LocalDateTime playTime;
}
