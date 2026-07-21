// 我的收藏页
const { favoriteApi } = require('../../utils/api');
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
    this.loadFavorites();
  },

  onPullDownRefresh() {
    this.loadFavorites().then(() => {
      wx.stopPullDownRefresh();
    });
  },

  async loadFavorites() {
    try {
      const list = await favoriteApi.list();
      // 格式化日期
      list.forEach(item => {
        if (item.createTime) {
          item.createTime = item.createTime.substring(0, 10);
        }
      });
      this.setData({ list, loaded: true });
    } catch (err) {
      console.error('加载收藏列表失败:', err);
      this.setData({ loaded: true });
    }
  },

  // 跳转详情
  goDetail(e) {
    const id = e.currentTarget.dataset.id;
    wx.navigateTo({ url: '/pages/detail/detail?id=' + id });
  },

  // 取消收藏
  async removeFav(e) {
    const { id, videoid } = e.currentTarget.dataset;
    try {
      await favoriteApi.toggle(videoid);
      // 从列表中移除
      const list = this.data.list.filter(item => item.id !== id);
      this.setData({ list });
      wx.showToast({ title: '已取消收藏', icon: 'none' });
    } catch (err) {
      console.error('取消收藏失败:', err);
    }
  }
});
