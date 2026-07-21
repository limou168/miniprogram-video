-- ============================================
-- 影视播放平台 - 数据库初始化脚本
-- 数据库: video_platform
-- ============================================

CREATE DATABASE IF NOT EXISTS video_platform DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE video_platform;

-- ==================== 用户表 ====================
DROP TABLE IF EXISTS sys_user;
CREATE TABLE sys_user (
    id              BIGINT          AUTO_INCREMENT PRIMARY KEY,
    username        VARCHAR(50)     NOT NULL UNIQUE      COMMENT '用户名',
    password        VARCHAR(255)    NOT NULL             COMMENT '密码(BCrypt加密)',
    nickname        VARCHAR(50)     DEFAULT ''           COMMENT '昵称',
    avatar_url      VARCHAR(500)    DEFAULT ''           COMMENT '头像地址',
    phone           VARCHAR(20)     DEFAULT ''           COMMENT '手机号',
    status          TINYINT         DEFAULT 1            COMMENT '状态: 0-禁用, 1-正常',
    create_time     DATETIME        DEFAULT CURRENT_TIMESTAMP COMMENT '注册时间',
    update_time     DATETIME        DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户表';

-- ==================== 分类表 ====================
DROP TABLE IF EXISTS sys_category;
CREATE TABLE sys_category (
    id              BIGINT          AUTO_INCREMENT PRIMARY KEY,
    name            VARCHAR(30)     NOT NULL UNIQUE      COMMENT '分类名',
    icon            VARCHAR(255)    DEFAULT ''           COMMENT '分类图标',
    sort_order      INT             DEFAULT 0            COMMENT '排序序号',
    status          TINYINT         DEFAULT 1            COMMENT '状态: 0-隐藏, 1-显示',
    create_time     DATETIME        DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='分类表';

-- ==================== 影视表 ====================
DROP TABLE IF EXISTS sys_video;
CREATE TABLE sys_video (
    id              BIGINT          AUTO_INCREMENT PRIMARY KEY,
    title           VARCHAR(200)    NOT NULL             COMMENT '影视标题',
    category_id     BIGINT          NOT NULL             COMMENT '所属分类ID',
    cover_url       VARCHAR(500)    DEFAULT ''           COMMENT '封面图URL',
    video_url       VARCHAR(1000)   DEFAULT ''           COMMENT '播放地址',
    description     TEXT                                 COMMENT '简介/剧情介绍',
    director        VARCHAR(100)    DEFAULT ''           COMMENT '导演',
    actors          VARCHAR(500)    DEFAULT ''           COMMENT '主演(逗号分隔)',
    year            INT             DEFAULT 0            COMMENT '年份',
    area            VARCHAR(50)     DEFAULT ''           COMMENT '地区',
    duration        VARCHAR(20)     DEFAULT ''           COMMENT '时长',
    score           DECIMAL(3,1)    DEFAULT 0.0          COMMENT '评分(0-10)',
    tags            VARCHAR(500)    DEFAULT ''           COMMENT '标签(逗号分隔)',
    play_count      BIGINT          DEFAULT 0            COMMENT '播放次数',
    status          TINYINT         DEFAULT 1            COMMENT '状态: 0-下架, 1-上架',
    is_recommend    TINYINT         DEFAULT 0            COMMENT '是否推荐: 0-否, 1-是',
    create_time     DATETIME        DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_time     DATETIME        DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_category_id (category_id),
    INDEX idx_title (title),
    INDEX idx_score (score),
    INDEX idx_play_count (play_count)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='影视表';

-- ==================== 播放记录表 ====================
DROP TABLE IF EXISTS sys_play_history;
CREATE TABLE sys_play_history (
    id              BIGINT          AUTO_INCREMENT PRIMARY KEY,
    user_id         BIGINT          NOT NULL             COMMENT '用户ID',
    video_id        BIGINT          NOT NULL             COMMENT '影视ID',
    progress        INT             DEFAULT 0            COMMENT '播放进度(秒)',
    duration        INT             DEFAULT 0            COMMENT '总时长(秒)',
    play_time       DATETIME        DEFAULT CURRENT_TIMESTAMP COMMENT '最近播放时间',
    INDEX idx_user_id (user_id),
    INDEX idx_user_video (user_id, video_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='播放记录表';

-- ==================== 收藏表 ====================
DROP TABLE IF EXISTS sys_favorite;
CREATE TABLE sys_favorite (
    id              BIGINT          AUTO_INCREMENT PRIMARY KEY,
    user_id         BIGINT          NOT NULL COMMENT '用户ID',
    video_id        BIGINT          NOT NULL COMMENT '影视ID',
    create_time     DATETIME        DEFAULT CURRENT_TIMESTAMP COMMENT '收藏时间',
    UNIQUE KEY uk_user_video (user_id, video_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户收藏表';

-- ==================== 初始化数据 ====================

-- 分类数据
INSERT INTO sys_category (name, sort_order) VALUES
('电影', 1),
('电视剧', 2),
('动漫', 3),
('综艺', 4),
('纪录片', 5);

-- 示例影视数据
INSERT INTO sys_video (title, category_id, cover_url, video_url, description, director, actors, year, area, duration, score, tags, is_recommend, play_count) VALUES
-- 电影 (category_id=1)
('流浪地球2', 1, 'https://picsum.photos/seed/movie1/400/600', 'https://www.w3schools.com/html/mov_bbb.mp4',
 '太阳即将毁灭，人类在地球表面建造出巨大的推进器，寻找新的家园。然而宇宙之路危机四伏，为了拯救地球，流浪地球时代的年轻人再次挺身而出，展开争分夺秒的生死之战。',
 '郭帆', '吴京,刘德华,李雪健,沙溢,宁理', 2023, '中国大陆', '173分钟', 8.3, '科幻,灾难,冒险', 1, 1500000),
('独行月球', 1, 'https://picsum.photos/seed/movie2/400/600', 'https://www.w3schools.com/html/mov_bbb.mp4',
 '人类为抵御小行星的撞击，在月球部署了月盾计划。陨石提前来袭，全员紧急撤离时，维修工独孤月因意外错过撤离通知，一个人落在了月球上，开始了他在月球上的生活。',
 '张吃鱼', '沈腾,马丽,黄才伦,常远', 2022, '中国大陆', '122分钟', 7.8, '喜剧,科幻', 1, 1200000),
('封神第一部：朝歌风云', 1, 'https://picsum.photos/seed/movie3/400/600', 'https://www.w3schools.com/html/mov_bbb.mp4',
 '商王殷寿与狐妖妲己勾结，暴虐无道，引发天谴。昆仑仙人姜子牙携"封神榜"下山，寻找天下共主，以救苍生。',
 '乌尔善', '费翔,李雪健,黄渤,于适,陈牧驰', 2023, '中国大陆', '148分钟', 7.9, '奇幻,史诗,动作', 1, 1800000),
('孤注一掷', 1, 'https://picsum.photos/seed/movie4/400/600', 'https://www.w3schools.com/html/mov_bbb.mp4',
 '程序员潘生、模特安娜被海外高薪招聘吸引，出国淘金，却意外落入境外诈骗工厂的陷阱。',
 '宁浩', '张艺兴,王传君,金晨,咏梅', 2023, '中国大陆', '130分钟', 7.5, '犯罪,剧情', 0, 2000000),

-- 电视剧 (category_id=2)
('庆余年2', 2, 'https://picsum.photos/seed/tv1/400/600', 'https://www.w3schools.com/html/mov_bbb.mp4',
 '范闲在经历生死后，重返京都，面对更加复杂的朝堂局势和更强大的敌人，他凭借智谋和勇气继续周旋。',
 '孙皓', '张若昀,李沁,陈道明,吴刚,辛芷蕾', 2024, '中国大陆', '45分钟/集', 8.8, '古装,权谋,轻喜剧', 1, 3000000),
('唐朝诡事录之西行', 2, 'https://picsum.photos/seed/tv2/400/600', 'https://www.w3schools.com/html/mov_bbb.mp4',
 '苏无名和卢凌风西行赴任途中，遭遇一系列诡异案件，两人联手侦破，揭开背后惊天秘密。',
 '郭靖宇', '杨旭文,杨志刚,郜思雯,孙雪宁', 2024, '中国大陆', '45分钟/集', 8.5, '悬疑,古装,探案', 1, 800000),
('狂飙', 2, 'https://picsum.photos/seed/tv3/400/600', 'https://www.w3schools.com/html/mov_bbb.mp4',
 '京海市一线刑警安欣，在与黑恶势力的斗争中，不断遭到保护伞的打击。在指导组的支持下，他与黑恶势力展开了一场跨越二十年的较量。',
 '徐纪周', '张译,张颂文,李一桐,吴刚', 2023, '中国大陆', '45分钟/集', 9.1, '犯罪,剧情,扫黑除恶', 1, 5000000),

-- 动漫 (category_id=3)
('鬼灭之刃 柱训练篇', 3, 'https://picsum.photos/seed/anime1/400/600', 'https://www.w3schools.com/html/mov_bbb.mp4',
 '炭治郎等人为了准备与鬼舞辻无惨的最终决战，在柱们的指导下开始了严酷的训练。',
 '外崎春雄', '花江夏树,鬼头明里,下野纮,松冈祯丞', 2024, '日本', '24分钟/集', 9.0, '热血,战斗,少年', 1, 2000000),
('咒术回战 第二季', 3, 'https://picsum.photos/seed/anime2/400/600', 'https://www.w3schools.com/html/mov_bbb.mp4',
 '虎杖悠仁在吞下宿傩手指后，进入咒术高专学习成为咒术师。涉谷事变篇，一场波及整个日本的大战即将爆发。',
 '朴性厚', '榎木淳弥,内田雄马,濑户麻沙美,中村悠一', 2023, '日本', '24分钟/集', 9.2, '热血,战斗,奇幻', 1, 3500000),
('名侦探柯南', 3, 'https://picsum.photos/seed/anime3/400/600', 'https://www.w3schools.com/html/mov_bbb.mp4',
 '高中生侦探工藤新一被灌下毒药后身体缩小，化名江户川柯南，寄住在毛利侦探事务所，一边解决各种案件，一边追查黑衣组织。',
 '山本泰一郎', '高山南,山崎和佳奈,小山力也,林原惠美', 1996, '日本', '25分钟/集', 9.0, '推理,悬疑,经典', 0, 5000000),

-- 综艺 (category_id=4)
('奔跑吧 第12季', 4, 'https://picsum.photos/seed/variety1/400/600', 'https://www.w3schools.com/html/mov_bbb.mp4',
 '跑男团再次集结，全新一季带来更多欢乐与挑战，明星嘉宾在游戏中展现真实一面。',
 '姚译天', '李晨,郑恺,杨颖,沙溢,白鹿,周深,范丞丞', 2024, '中国大陆', '90分钟/期', 7.5, '综艺,真人秀,搞笑', 1, 2500000),

-- 纪录片 (category_id=5)
('地球脉动 第三季', 5, 'https://picsum.photos/seed/doc1/400/600', 'https://www.w3schools.com/html/mov_bbb.mp4',
 'BBC倾力打造的自然纪录片巅峰之作，从海洋深处到冰山之巅，从热带雨林到沙漠腹地，展现地球上最壮丽的自然景观和野生动物。',
 '大卫·爱登堡', '大卫·爱登堡', 2023, '英国', '60分钟/集', 9.9, '自然,动物,经典', 1, 1000000);

-- 测试用户 (密码: 123456, BCrypt加密)
INSERT INTO sys_user (username, password, nickname) VALUES
('test', '$2a$10$N.zmdr9k7uOCQb376NoUnuTJ8iAt6Z5EHsM8lE9lBOsl7iAt6Z5Eh', '测试用户');
