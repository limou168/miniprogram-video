// 注册页
const { userApi } = require('../../utils/api');
const auth = require('../../utils/auth');

Page({
  data: {
    username: '',
    nickname: '',
    password: '',
    confirmPassword: '',
    loading: false
  },

  onUsernameInput(e) {
    this.setData({ username: e.detail.value });
  },

  onNicknameInput(e) {
    this.setData({ nickname: e.detail.value });
  },

  onPasswordInput(e) {
    this.setData({ password: e.detail.value });
  },

  onConfirmPwdInput(e) {
    this.setData({ confirmPassword: e.detail.value });
  },

  // 注册
  async onRegister() {
    const { username, nickname, password, confirmPassword } = this.data;

    if (!username.trim()) {
      wx.showToast({ title: '请输入用户名', icon: 'none' });
      return;
    }
    if (username.trim().length < 3) {
      wx.showToast({ title: '用户名至少3个字符', icon: 'none' });
      return;
    }
    if (!password) {
      wx.showToast({ title: '请输入密码', icon: 'none' });
      return;
    }
    if (password.length < 6) {
      wx.showToast({ title: '密码至少6个字符', icon: 'none' });
      return;
    }
    if (password !== confirmPassword) {
      wx.showToast({ title: '两次密码不一致', icon: 'none' });
      return;
    }

    this.setData({ loading: true });

    try {
      await userApi.register({
        username: username.trim(),
        password: password,
        nickname: nickname.trim() || username.trim()
      });

      wx.showToast({ title: '注册成功，请登录', icon: 'success' });

      setTimeout(() => {
        wx.navigateBack();
      }, 1500);
    } catch (err) {
      console.error('注册失败:', err);
    } finally {
      this.setData({ loading: false });
    }
  },

  // 跳转登录页
  goLogin() {
    wx.navigateBack();
  }
});
