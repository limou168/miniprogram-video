package com.video.controller;

import com.video.common.Result;
import com.video.dto.*;
import com.video.security.UserContext;
import com.video.service.UserService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/user")
@RequiredArgsConstructor
public class UserController {

    private final UserService userService;

    /**
     * 注册
     */
    @PostMapping("/register")
    public Result<?> register(@Valid @RequestBody RegisterDTO dto) {
        userService.register(dto);
        return Result.ok();
    }

    /**
     * 登录
     */
    @PostMapping("/login")
    public Result<LoginVO> login(@Valid @RequestBody LoginDTO dto) {
        LoginVO vo = userService.login(dto);
        return Result.ok(vo);
    }

    /**
     * 获取当前用户信息
     */
    @GetMapping("/info")
    public Result<UserVO> info() {
        Long userId = UserContext.getUserId();
        UserVO vo = userService.getUserInfo(userId);
        return Result.ok(vo);
    }

    /**
     * 修改个人信息
     */
    @PutMapping("/info")
    public Result<?> updateInfo(@RequestBody UserVO dto) {
        Long userId = UserContext.getUserId();
        userService.updateUserInfo(userId, dto);
        return Result.ok();
    }

    /**
     * 修改密码
     */
    @PutMapping("/password")
    public Result<?> changePassword(@Valid @RequestBody PasswordDTO dto) {
        Long userId = UserContext.getUserId();
        userService.changePassword(userId, dto);
        return Result.ok();
    }

    /**
     * Token 自动续期
     * 前端在检测到 401 时调用此接口尝试刷新
     */
    @PostMapping("/refresh")
    public Result<LoginVO> refresh() {
        Long userId = UserContext.getUserId();
        if (userId == null) {
            return Result.fail(401, "未登录");
        }
        LoginVO vo = userService.refreshToken(userId);
        return Result.ok(vo);
    }
}
