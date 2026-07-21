// 播放记录页
const { historyApi } = require('../../utils/api');
const auth = require('../../utils/auth');

Page({
  data: {
    list: [],
    loaded: false
  },

  onShow() {
    if (!auth.isLogin()) {
      wx.showToast({ title: '请先登录', icon: 'none' });
      setTimeout(() => wx.navigateBack(), 1000);
      return;
    }
    this.loadHistory();
  },

  onPullDownRefresh() {
    this.loadHistory().then(() => {
      wx.stopPullDownRefresh();
    });
  },

  async loadHistory() {
    try {
      const list = await historyApi.list();
      this.setData({ list, loaded: true });
    } catch (err) {
      console.error('加载播放记录失败:', err);
      this.setData({ loaded: true });
    }
  },

  // 跳转详情
  goDetail(e) {
    const id = e.currentTarget.dataset.id;
    wx.navigateTo({ url: '/pages/detail/detail?id=' + id });
  },

  // 删除记录
  async removeHistory(e) {
    const id = e.currentTarget.dataset.id;
    try {
      await historyApi.remove(id);
      const list = this.data.list.filter(item => item.id !== id);
      this.setData({ list });
      wx.showToast({ title: '已删除', icon: 'none' });
    } catch (err) {
      console.error('删除播放记录失败:', err);
    }
  },

  // 格式化时长 (秒 -> 分:秒)
  formatProgress(seconds) {
    if (!seconds) return '00:00';
    const m = Math.floor(seconds / 60);
    const s = Math.floor(seconds % 60);
    return (m < 10 ? '0' : '') + m + ':' + (s < 10 ? '0' : '') + s;
  },

  // 格式化时间
  formatTime(time) {
    if (!time) return '';
    return time.substring(0, 19).replace('T', ' ');
  }
});
