package com.example.demo2.dao;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.example.demo2.entity.User;
import org.apache.ibatis.annotations.Mapper;

/**
 * 用户 Mapper — 数据访问层（DAO）
 * 继承 MyBatis-Plus 的 BaseMapper，自动拥有 CRUD 方法
 */
@Mapper
public interface UserMapper extends BaseMapper<User> {
    // 常用的 CRUD 方法 BaseMapper 已经提供：
    // insert、deleteById、updateById、selectById、selectList 等
    // 复杂查询可以在这里自定义方法，并在 XML 中写 SQL
}
