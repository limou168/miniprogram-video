package com.video.entity;

import com.baomidou.mybatisplus.annotation.*;
import lombok.Data;

import java.time.LocalDateTime;

@Data
@TableName("sys_video_source")
public class VideoSource {

    @TableId(type = IdType.AUTO)
    private Long id;

    private Long videoId;
    private Integer episodeNumber;
    private String sourceName;
    private String sourceUrl;
    private Integer sortOrder;
    private Integer status;

    @TableField(fill = FieldFill.INSERT)
    private LocalDateTime createTime;
}
