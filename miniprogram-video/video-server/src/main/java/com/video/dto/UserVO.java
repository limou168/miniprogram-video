package com.video.dto;

import lombok.Builder;
import lombok.Data;
import java.time.LocalDateTime;

/**
 * 用户信息返回
 */
@Data
@Builder
public class UserVO {

    private Long id;
    private String username;
    private String nickname;
    private String avatarUrl;
    private String phone;
    private LocalDateTime createTime;
}
