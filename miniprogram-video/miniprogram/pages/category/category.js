// 分类影视列表页
const { categoryApi, videoApi } = require('../../utils/api');

Page({
  data: {
    categories: [],
    activeCategoryId: 0,
    videoList: [],
    page: 1,
    size: 20,
    hasMore: true,
    loading: false
  },

  onLoad(options) {
    // 如果从其他页面传入分类 ID
    if (options.categoryId) {
      this.setData({ activeCategoryId: Number(options.categoryId) });
    }
    this.loadCategories();
    this.loadVideoList();
  },

  onReachBottom() {
    if (this.data.hasMore && !this.data.loading) {
      this.loadVideoList();
    }
  },

  async loadCategories() {
    try {
      const categories = await categoryApi.list();
      this.setData({ categories });
    } catch (err) {
      console.error('加载分类失败:', err);
    }
  },

  async loadVideoList() {
    if (this.data.loading) return;
    this.setData({ loading: true });

    try {
      const { page, size, activeCategoryId } = this.data;
      const params = { page, size };
      if (activeCategoryId > 0) {
        params.categoryId = activeCategoryId;
      }

      const result = await videoApi.list(params);
      const newList = this.data.videoList.concat(result.records || []);

      this.setData({
        videoList: newList,
        page: page + 1,
        hasMore: result.records && result.records.length >= size
      });
    } catch (err) {
      console.error('加载失败:', err);
    } finally {
      this.setData({ loading: false });
    }
  },

  onCategoryChange(e) {
    const { id } = e.detail;
    this.setData({
      activeCategoryId: id,
      page: 1,
      videoList: [],
      hasMore: true
    });
    this.loadVideoList();
  },

  goSearch() {
    wx.navigateTo({ url: '/pages/search/search' });
  }
});
