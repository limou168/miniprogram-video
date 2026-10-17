// 修改密码页
const { userApi } = require('../../utils/api');
const auth = require('../../utils/auth');

Page({
  data: {
    oldPassword: '',
    newPassword: '',
    confirmPassword: '',
    loading: false
  },

  onOldPwdInput(e) {
    this.setData({ oldPassword: e.detail.value });
  },

  onNewPwdInput(e) {
    this.setData({ newPassword: e.detail.value });
  },

  onConfirmPwdInput(e) {
    this.setData({ confirmPassword: e.detail.value });
  },

  async onSubmit() {
    const { oldPassword, newPassword, confirmPassword } = this.data;

    if (!oldPassword) {
      wx.showToast({ title: '请输入旧密码', icon: 'none' });
      return;
    }
    if (!newPassword) {
      wx.showToast({ title: '请输入新密码', icon: 'none' });
      return;
    }
    if (newPassword.length < 6) {
      wx.showToast({ title: '新密码至少6个字符', icon: 'none' });
      return;
    }
    if (newPassword !== confirmPassword) {
      wx.showToast({ title: '两次密码不一致', icon: 'none' });
      return;
    }
    if (oldPassword === newPassword) {
      wx.showToast({ title: '新密码不能与旧密码相同', icon: 'none' });
      return;
    }

    this.setData({ loading: true });

    try {
      await userApi.changePassword({
        oldPassword,
        newPassword
      });

      wx.showToast({ title: '密码修改成功，请重新登录', icon: 'success' });

      // 清除登录状态
      setTimeout(() => {
        auth.clearLogin();
        const app = getApp();
        app.globalData.token = null;
        app.globalData.isLogin = false;
        // 跳转到登录页
        wx.reLaunch({ url: '/pages/login/login' });
      }, 1500);
    } catch (err) {
      console.error('修改密码失败:', err);
    } finally {
      this.setData({ loading: false });
    }
  }
});
