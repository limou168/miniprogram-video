package com.video.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;
import java.math.BigDecimal;

/**
 * 影视卡片返回（列表用，字段精简）
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class VideoCardVO {

    private Long id;
    private String title;
    private String coverUrl;
    private String categoryName;
    private Integer year;
    private String duration;
    private BigDecimal score;
    private Long playCount;
}
