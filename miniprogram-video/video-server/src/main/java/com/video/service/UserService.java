package com.video.service;

import com.baomidou.mybatisplus.extension.service.IService;
import com.video.dto.*;
import com.video.entity.User;

public interface UserService extends IService<User> {

    /**
     * 注册
     */
    void register(RegisterDTO dto);

    /**
     * 登录，返回 token 和用户信息
     */
    LoginVO login(LoginDTO dto);

    /**
     * 修改密码
     */
    void changePassword(Long userId, PasswordDTO dto);

    /**
     * 获取用户信息
     */
    UserVO getUserInfo(Long userId);

    /**
     * 修改个人信息
     */
    void updateUserInfo(Long userId, UserVO dto);
}
