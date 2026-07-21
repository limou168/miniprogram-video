package com.video.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;
import java.math.BigDecimal;
import java.util.List;

/**
 * 影视详情返回
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class VideoVO {

    private Long id;
    private String title;
    private Long categoryId;
    private String categoryName;
    private String coverUrl;
    private String videoUrl;
    private String description;
    private String director;
    private String actors;
    private Integer year;
    private String area;
    private String duration;
    private BigDecimal score;
    private String tags;
    private Long playCount;
    private Integer isRecommend;
    private List<EpisodeVO> episodes;
}
