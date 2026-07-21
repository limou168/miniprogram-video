package com.example.demo2.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.example.demo2.common.Result;
import com.example.demo2.dao.UserMapper;
import com.example.demo2.dto.LoginRequest;
import com.example.demo2.dto.LoginVO;
import com.example.demo2.entity.User;
import com.example.demo2.service.UserService;
import lombok.RequiredArgsConstructor;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;

/**
 * 用户业务层实现
 */
@Service
@RequiredArgsConstructor
public class UserServiceImpl implements UserService {

    private final UserMapper userMapper;
    private final PasswordEncoder passwordEncoder;

    @Override
    public Result<LoginVO> login(LoginRequest request) {
        // 1. 根据用户名查询用户
        User user = userMapper.selectOne(
                new LambdaQueryWrapper<User>()
                        .eq(User::getUsername, request.getUsername())
        );

        // 2. 用户不存在
        if (user == null) {
            return Result.error("用户名或密码错误");
        }

        // 3. 检查账号是否被禁用（status = 0 表示禁用）
        if (user.getStatus() != null && user.getStatus() == 0) {
            return Result.error("账号已被禁用，请联系管理员");
        }

        // 4. 验证密码（将明文密码与数据库中 BCrypt 加密的密码比对）
        if (!passwordEncoder.matches(request.getPassword(), user.getPassword())) {
            return Result.error("用户名或密码错误");
        }

        // 5. 登录成功，构建返回数据
        LoginVO vo = LoginVO.builder()
                .userId(user.getId())
                .username(user.getUsername())
                .nickname(user.getNickname())
                .build();

        return Result.success("登录成功", vo);
    }
}
