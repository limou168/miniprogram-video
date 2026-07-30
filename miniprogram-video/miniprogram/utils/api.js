/**
 * 所有后端 API 调用
 */
const { get, post, put, del } = require('./request');

// ==================== 用户模块 ====================
const userApi = {
  register: (data) => post('/api/user/register', data, { needAuth: false }),
  login: (data) => post('/api/user/login', data, { needAuth: false }),
  info: () => get('/api/user/info', {}, { needAuth: true }),
  changePassword: (data) => put('/api/user/password', data, { needAuth: true }),
  updateInfo: (data) => put('/api/user/info', data, { needAuth: true })
};

// ==================== 分类模块 ====================
const categoryApi = {
  list: () => get('/api/category/list')
};

// ==================== 影视模块 ====================
const videoApi = {
  list: (params) => get('/api/video/list', params),
  detail: (id) => get('/api/video/' + id),
  hot: () => get('/api/video/hot', {}, { needAuth: false }),
  search: (params) => get('/api/video/search', params),
  suggest: (params) => get('/api/video/search/suggest', params),
  episodes: (id) => get('/api/video/' + id + '/episodes'),
  sources: (id, episodeNumber) => get('/api/video/' + id + '/sources', { episodeNumber }),
  tags: (categoryId) => get('/api/video/tags', { categoryId })
};

// ==================== 播放记录 ====================
const historyApi = {
  list: () => get('/api/history/list', {}, { needAuth: true }),
  save: (data) => post('/api/history/save', {
    videoId: data.videoId,
    episodeNumber: data.episodeNumber || 0,
    progress: data.progress || 0,
    duration: data.duration || 0
  }, { needAuth: true }),
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
