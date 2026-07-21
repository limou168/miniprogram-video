package com.video.entity;

import com.baomidou.mybatisplus.annotation.*;
import lombok.Data;
import java.math.BigDecimal;
import java.time.LocalDateTime;

@Data
@TableName("sys_video")
public class Video {

    @TableId(type = IdType.AUTO)
    private Long id;

    private String title;
    private Long categoryId;
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
    private Integer status;
    private Integer isRecommend;

    @TableField(fill = FieldFill.INSERT)
    private LocalDateTime createTime;

    @TableField(fill = FieldFill.INSERT_UPDATE)
    private LocalDateTime updateTime;
}
