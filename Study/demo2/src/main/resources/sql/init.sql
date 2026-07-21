-- ============================================
-- 数据库初始化脚本
-- 请在 SSMS (SQL Server Management Studio) 中执行
-- ============================================

-- 1. 创建数据库（如果不存在）
IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = N'demo2')
BEGIN
    CREATE DATABASE demo2;
END
GO

USE demo2;
GO

-- 2. 创建用户表
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='sys_user' AND xtype='U')
BEGIN
    CREATE TABLE sys_user (
        id          BIGINT IDENTITY(1,1) PRIMARY KEY,
        username    VARCHAR(50)  NOT NULL UNIQUE,
        password    VARCHAR(255) NOT NULL,
        nickname    VARCHAR(50),
        email       VARCHAR(100),
        phone       VARCHAR(20),
        status      INT          DEFAULT 1,        -- 1=启用, 0=禁用
        create_time DATETIME2    DEFAULT GETDATE(),
        update_time DATETIME2    DEFAULT GETDATE()
    );
    PRINT '表 sys_user 创建成功！';
END
GO

-- 3. 插入测试用户（密码 123456 的 BCrypt 加密值）
IF NOT EXISTS (SELECT 1 FROM sys_user WHERE username = 'admin')
BEGIN
    INSERT INTO sys_user (username, password, nickname, status)
    VALUES ('admin', '$2a$10$N.zmdr9k7uOCQb376NoUnuTJ8iAt6Z5EHsM8lE9lBOsl7iKTVKIUi', '管理员', 1);
    PRINT '测试用户 admin 插入成功！密码: 123456';
END
GO

PRINT '数据库初始化完成！';
GO
