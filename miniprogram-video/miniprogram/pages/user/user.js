// 个人中心页
const auth = require('../../utils/auth');

Page({
  data: {
    isLogin: false,
    userInfo: null
  },

  onShow() {
    this.checkLoginStatus();
  },

  checkLoginStatus() {
    const isLogin = auth.isLogin();
    const userInfo = auth.getUserInfo();
    this.setData({ isLogin, userInfo });
  },

  // 跳转登录
  goLogin() {
    wx.navigateTo({ url: '/pages/login/login' });
  },

  // 修改密码
  goChangePassword() {
    if (!this.data.isLogin) {
      wx.showToast({ title: '请先登录', icon: 'none' });
      setTimeout(() => wx.navigateTo({ url: '/pages/login/login' }), 1000);
      return;
    }
    wx.navigateTo({ url: '/pages/password/password' });
  },

  // 播放历史
  goHistory() {
    if (!this.data.isLogin) {
      wx.showToast({ title: '请先登录', icon: 'none' });
      return;
    }
    wx.navigateTo({ url: '/pages/history/history' });
  },

  // 我的收藏
  goFavorites() {
    if (!this.data.isLogin) {
      wx.showToast({ title: '请先登录', icon: 'none' });
      return;
    }
    wx.navigateTo({ url: '/pages/favorites/favorites' });
  },

  // 关于
  goAbout() {
    wx.showModal({
      title: '关于光影影视',
      content: '光影影视 v1.0.0\n一款简洁优雅的影视播放小程序\n海量影视，随心观看',
      showCancel: false
    });
  },

  // 退出登录
  onLogout() {
    wx.showModal({
      title: '确认退出',
      content: '退出后需要重新登录',
      success: (res) => {
        if (res.confirm) {
          auth.clearLogin();
          const app = getApp();
          app.globalData.token = null;
          app.globalData.userInfo = null;
          app.globalData.isLogin = false;
          this.setData({ isLogin: false, userInfo: null });
          wx.showToast({ title: '已退出', icon: 'none' });
        }
      }
    });
  }
});
