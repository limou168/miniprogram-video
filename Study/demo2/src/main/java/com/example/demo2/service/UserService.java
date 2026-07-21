package com.example.demo2.service;

import com.example.demo2.common.Result;
import com.example.demo2.dto.LoginRequest;
import com.example.demo2.dto.LoginVO;

/**
 * 用户业务层接口
 */
public interface UserService {

    /**
     * 用户登录
     *
     * @param request 登录请求（用户名 + 密码）
     * @return 登录结果（成功返回用户信息，失败返回错误提示）
     */
    Result<LoginVO> login(LoginRequest request);
}
