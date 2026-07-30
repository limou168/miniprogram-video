package com.video.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;

/**
 * 分集返回 VO
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class EpisodeVO {

    private Long id;
    private Integer episodeNumber;
    private String episodeTitle;
    private String videoUrl;
    private String duration;
    private List<VideoSourceVO> sources;
}
