package com.video.entity;

import com.baomidou.mybatisplus.annotation.*;
import lombok.Data;

import java.time.LocalDateTime;

@Data
@TableName("sys_video_episode")
public class VideoEpisode {

    @TableId(type = IdType.AUTO)
    private Long id;

    private Long videoId;
    private Integer episodeNumber;
    private String episodeTitle;
    private String videoUrl;
    private String duration;

    @TableField(fill = FieldFill.INSERT)
    private LocalDateTime createTime;
}
