package com.example.demo2.controller;

import com.example.demo2.common.Result;
import com.example.demo2.dto.LoginRequest;
import com.example.demo2.dto.LoginVO;
import com.example.demo2.service.UserService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

/**
 * 用户控制器 — 处理用户相关的 HTTP 请求
 */
@RestController
@RequestMapping("/api/user")
@RequiredArgsConstructor
public class UserController {

    private final UserService userService;

    /**
     * 登录接口
     * POST /api/user/login
     *
     * 请求体示例：
     * {
     *     "username": "admin",
     *     "password": "123456"
     * }
     */
    @PostMapping("/login")
    public Result<LoginVO> login(@Valid @RequestBody LoginRequest request) {
        return userService.login(request);
    }
}
