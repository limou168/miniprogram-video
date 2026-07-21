/**
 * Token 管理工具
 */

const TOKEN_KEY = 'token';
const USER_INFO_KEY = 'userInfo';

// 获取 token
function getToken() {
  return wx.getStorageSync(TOKEN_KEY) || '';
}

// 保存 token
function setToken(token) {
  wx.setStorageSync(TOKEN_KEY, token);
}

// 获取用户信息
function getUserInfo() {
  return wx.getStorageSync(USER_INFO_KEY) || null;
}

// 保存用户信息
function setUserInfo(userInfo) {
  wx.setStorageSync(USER_INFO_KEY, userInfo);
}

// 检查是否已登录
function isLogin() {
  return !!getToken();
}

// 清除登录信息
function clearLogin() {
  wx.removeStorageSync(TOKEN_KEY);
  wx.removeStorageSync(USER_INFO_KEY);
}

module.exports = {
  getToken,
  setToken,
  getUserInfo,
  setUserInfo,
  isLogin,
  clearLogin
};
