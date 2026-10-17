package com.video.dto;

import lombok.Builder;
import lombok.Data;

/**
 * 登录返回
 */
@Data
@Builder
public class LoginVO {

    private String token;
    private Long userId;
    private String nickname;
    private String avatarUrl;
}
