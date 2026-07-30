// app.js
App({
  globalData: {
    userInfo: null,
    token: null,
    isLogin: false
  },

  onLaunch() {
    // 初始化云托管环境
    const config = require('./utils/config');
    if (config.useCloudCallContainer) {
      wx.cloud.init({
        env: config.cloudEnv
      });
    }

    // 检查登录状态（持久化）
    const token = wx.getStorageSync('token');
    const userInfo = wx.getStorageSync('userInfo');
    if (token) {
      this.globalData.token = token;
      this.globalData.userInfo = userInfo || null;
      this.globalData.isLogin = true;
    }
  },

  // 登录成功后设置用户信息
  setLoginInfo(token, userInfo) {
    this.globalData.token = token;
    this.globalData.userInfo = userInfo;
    this.globalData.isLogin = true;
    wx.setStorageSync('token', token);
    wx.setStorageSync('userInfo', userInfo);
  },

  // 退出登录
  logout() {
    this.globalData.token = null;
    this.globalData.userInfo = null;
    this.globalData.isLogin = false;
    wx.removeStorageSync('token');
    wx.removeStorageSync('userInfo');
  }
});
