// 登录页
const { userApi } = require('../../utils/api');
const auth = require('../../utils/auth');

Page({
  data: {
    username: '',
    password: '',
    loading: false
  },

  onUsernameInput(e) {
    this.setData({ username: e.detail.value });
  },

  onPasswordInput(e) {
    this.setData({ password: e.detail.value });
  },

  // 登录
  async onLogin() {
    const { username, password } = this.data;

    if (!username.trim()) {
      wx.showToast({ title: '请输入用户名', icon: 'none' });
      return;
    }
    if (!password.trim()) {
      wx.showToast({ title: '请输入密码', icon: 'none' });
      return;
    }

    this.setData({ loading: true });

    try {
      const result = await userApi.login({
        username: username.trim(),
        password: password
      });

      // 保存登录状态
      auth.setToken(result.token);
      auth.setUserInfo({
        userId: result.userId,
        nickname: result.nickname,
        avatarUrl: result.avatarUrl
      });

      // 更新全局状态
      const app = getApp();
      app.globalData.token = result.token;
      app.globalData.userInfo = result;
      app.globalData.isLogin = true;

      wx.showToast({ title: '登录成功', icon: 'success' });

      setTimeout(() => {
        wx.switchTab({ url: '/pages/index/index' });
      }, 1000);
    } catch (err) {
      console.error('登录失败:', err);
    } finally {
      this.setData({ loading: false });
    }
  },

  // 跳转注册页
  goRegister() {
    wx.navigateTo({ url: '/pages/register/register' });
  }
});
