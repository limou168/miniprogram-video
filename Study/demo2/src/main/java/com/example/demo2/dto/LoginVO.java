package com.example.demo2.dto;

import lombok.Builder;
import lombok.Data;

/**
 * 登录成功后返回的用户信息
 */
@Data
@Builder
public class LoginVO {

    /** 用户 ID */
    private Long userId;

    /** 用户名 */
    private String username;

    /** 昵称 */
    private String nickname;
}
