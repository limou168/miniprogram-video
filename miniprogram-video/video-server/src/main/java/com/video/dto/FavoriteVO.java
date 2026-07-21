package com.video.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.math.BigDecimal;
import java.time.LocalDateTime;

/**
 * 收藏列表返回 VO（含视频信息）
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class FavoriteVO {

    private Long id;
    private Long videoId;
    private String videoTitle;
    private String coverUrl;
    private BigDecimal score;
    private Integer year;
    private String duration;
    private String categoryName;
    private LocalDateTime createTime;
}
