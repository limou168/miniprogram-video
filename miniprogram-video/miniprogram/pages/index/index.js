// 主页（默认展示热门、最新、推荐视频）
const { categoryApi, videoApi } = require('../../utils/api');

Page({
  data: {
    // 轮播推荐
    banners: [],

    // 分类
    categories: [],
    activeCategoryId: 0,

    // 导航标签
    navTabs: [
      { key: 'play_count', name: '🔥 热门' },
      { key: 'time', name: '🕐 最新' },
      { key: 'score', name: '⭐ 高分' }
    ],
    activeNav: 'play_count',

    // 影视列表
    videoList: [],
    page: 1,
    size: 20,
    hasMore: true,
    loading: false,

    // 当前排序
    orderBy: 'play_count'
  },

  onLoad() {
    this.loadCategories();
    this.loadBanners();
    this.loadVideoList();
  },

  onShow() {
    // 每次显示时刷新
  },

  onPullDownRefresh() {
    this.setData({ page: 1, videoList: [], hasMore: true });
    this.loadBanners();
    this.loadVideoList();
    wx.stopPullDownRefresh();
  },

  onReachBottom() {
    if (this.data.hasMore && !this.data.loading) {
      this.loadVideoList();
    }
  },

  // 加载轮播（热门前5）
  async loadBanners() {
    try {
      const result = await videoApi.list({ page: 1, size: 5, orderBy: 'play_count' });
      this.setData({ banners: result.records || [] });
    } catch (err) {
      console.error('加载轮播失败:', err);
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
      const { page, size, activeCategoryId, orderBy } = this.data;
      const params = { page, size, orderBy };
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

  // 导航标签切换
  onNavChange(e) {
    const key = e.currentTarget.dataset.key;
    if (key === this.data.activeNav) return;
    this.setData({
      activeNav: key,
      orderBy: key,
      page: 1,
      videoList: [],
      hasMore: true
    });
    this.loadVideoList();
  },

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

  goSearch() {
    wx.navigateTo({ url: '/pages/search/search' });
  },

  goSearchPage(e) {
    const { keyword } = e.detail;
    if (keyword) {
      wx.navigateTo({ url: '/pages/search/search?keyword=' + encodeURIComponent(keyword) });
    }
  },

  goDetail(e) {
    const id = e.currentTarget.dataset.id;
    wx.navigateTo({ url: '/pages/detail/detail?id=' + id });
  },

  onShareAppMessage() {
    return {
      title: '光影影视 - 海量影视随心看',
      path: '/pages/index/index'
    };
  }
});
