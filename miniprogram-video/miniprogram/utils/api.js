/**
 * 所有后端 API 调用
 */
const { get, post, put, del } = require('./request');

// ==================== 用户模块 ====================
const userApi = {
  // 注册
  register: (data) => post('/api/user/register', data, { needAuth: false }),
  // 登录
  login: (data) => post('/api/user/login', data, { needAuth: false }),
  // 获取用户信息
  info: () => get('/api/user/info', {}, { needAuth: true }),
  // 修改密码
  changePassword: (data) => put('/api/user/password', data, { needAuth: true }),
  // 修改个人信息
  updateInfo: (data) => put('/api/user/info', data, { needAuth: true })
};

// ==================== 分类模块 ====================
const categoryApi = {
  // 全部分类列表
  list: () => get('/api/category/list')
};

// ==================== 影视模块 ====================
const videoApi = {
  // 分页列表（可按分类筛选）
  list: (params) => get('/api/video/list', params),
  // 影视详情
  detail: (id) => get('/api/video/' + id),
  // 热门推荐
  hot: () => get('/api/video/hot'),
  // 搜索
  search: (params) => get('/api/video/search', params),
  // 获取分集列表
  episodes: (id) => get('/api/video/' + id + '/episodes')
};

// ==================== 播放记录 ====================
const historyApi = {
  list: () => get('/api/history/list', {}, { needAuth: true }),
  save: (data) => post('/api/history/save', { videoId: data.videoId, episodeNumber: data.episodeNumber || 0, progress: data.progress || 0, duration: data.duration || 0 }, { needAuth: true }),
  remove: (id) => del('/api/history/' + id, { needAuth: true })
};

// ==================== 收藏 ====================
const favoriteApi = {
  list: () => get('/api/favorite/list', {}, { needAuth: true }),
  toggle: (videoId) => post('/api/favorite/toggle/' + videoId, {}, { needAuth: true }),
  check: (videoId) => get('/api/favorite/check/' + videoId, {}, { needAuth: true })
};

module.exports = {
  userApi,
  categoryApi,
  videoApi,
  historyApi,
  favoriteApi
};
