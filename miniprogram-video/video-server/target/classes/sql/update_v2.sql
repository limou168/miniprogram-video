-- ============================================
-- v2.0 版本迭代 - 数据库更新脚本
-- ============================================

USE video_platform;

-- 1. 新建视频分集表
DROP TABLE IF EXISTS sys_video_episode;
CREATE TABLE sys_video_episode (
    id              BIGINT          AUTO_INCREMENT PRIMARY KEY,
    video_id        BIGINT          NOT NULL             COMMENT '关联视频ID',
    episode_number  INT             NOT NULL             COMMENT '集数',
    episode_title   VARCHAR(200)    DEFAULT ''           COMMENT '分集标题',
    video_url       VARCHAR(1000)   NOT NULL             COMMENT '分集播放地址',
    duration        VARCHAR(20)     DEFAULT ''           COMMENT '分集时长',
    create_time     DATETIME        DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX idx_video_id (video_id),
    UNIQUE KEY uk_video_episode (video_id, episode_number)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='视频分集表';

-- 2. 播放记录表新增分集字段
ALTER TABLE sys_play_history
    ADD COLUMN episode_number INT DEFAULT 0 COMMENT '分集号' AFTER video_id;
