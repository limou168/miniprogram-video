// 主页
const { categoryApi, videoApi } = require('../../utils/api');

Page({
  data: {
    // 轮播图
    banners: [],

    // 分类
    categories: [],
    activeCategoryId: 0,

    // 影视列表
    videoList: [],
    page: 1,
    size: 20,
    hasMore: true,
    loading: false
  },

  onLoad() {
    this.loadCategories();
    this.loadHotVideos();
    this.loadVideoList();
  },

  onShow() {
    // 每次显示时刷新（从其他 tab 切回来）
  },

  // 下拉刷新
  onPullDownRefresh() {
    this.setData({ page: 1, videoList: [], hasMore: true });
    this.loadHotVideos();
    this.loadVideoList();
    wx.stopPullDownRefresh();
  },

  // 上拉加载更多
  onReachBottom() {
    if (this.data.hasMore && !this.data.loading) {
      this.loadVideoList();
    }
  },

  // ==================== 分类 ====================
  async loadCategories() {
    try {
      const categories = await categoryApi.list();
      this.setData({ categories });
    } catch (err) {
      console.error('加载分类失败:', err);
    }
  },

  // ==================== 轮播图 ====================
  async loadHotVideos() {
    try {
      const result = await videoApi.hot();
      const banners = (result.records || []).slice(0, 5);
      this.setData({ banners });
    } catch (err) {
      console.error('加载热门失败:', err);
    }
  },

  // ==================== 影视列表 ====================
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
      console.error('加载影视列表失败:', err);
    } finally {
      this.setData({ loading: false });
    }
  },

  // ==================== 事件处理 ====================
  // 分类切换
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

  // 点击搜索栏 → 跳转搜索页
  goSearch() {
    wx.navigateTo({ url: '/pages/search/search' });
  },

  // 搜索事件 → 跳转搜索结果
  goSearchPage(e) {
    const { keyword } = e.detail;
    if (keyword) {
      wx.navigateTo({ url: '/pages/search/search?keyword=' + encodeURIComponent(keyword) });
    }
  },

  // 点击影视详情
  goDetail(e) {
    const id = e.currentTarget.dataset.id;
    wx.navigateTo({ url: '/pages/detail/detail?id=' + id });
  },

  // 分享
  onShareAppMessage() {
    return {
      title: '光影影视 - 海量影视随心看',
      path: '/pages/index/index'
    };
  }
});
