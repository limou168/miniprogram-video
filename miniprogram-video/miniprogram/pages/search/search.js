// 搜索页
const { videoApi } = require('../../utils/api');

const HISTORY_KEY = 'search_history';
const MAX_HISTORY = 10;

Page({
  data: {
    keyword: '',
    searchKeyword: '',
    hasSearched: false,
    searchHistory: [],
    hotKeys: ['流浪地球', '庆余年', '鬼灭之刃', '狂飙', '封神', '咒术回战'],

    // 搜索结果
    videoList: [],
    total: 0,
    page: 1,
    size: 20,
    hasMore: true,
    loading: false
  },

  onLoad(options) {
    this.loadHistory();

    // 如果从其他页面带入了搜索关键词
    if (options.keyword) {
      const keyword = decodeURIComponent(options.keyword);
      this.setData({ keyword, searchKeyword: keyword, hasSearched: true });
      this.doSearch();
    }
  },

  onReachBottom() {
    if (this.data.hasSearched && this.data.hasMore && !this.data.loading) {
      this.doSearch();
    }
  },

  // ==================== 搜索历史 ====================
  loadHistory() {
    const history = wx.getStorageSync(HISTORY_KEY) || [];
    this.setData({ searchHistory: history });
  },

  saveHistory(keyword) {
    let history = wx.getStorageSync(HISTORY_KEY) || [];
    // 移除重复项
    history = history.filter(item => item !== keyword);
    // 添加到开头
    history.unshift(keyword);
    // 限制数量
    if (history.length > MAX_HISTORY) {
      history = history.slice(0, MAX_HISTORY);
    }
    wx.setStorageSync(HISTORY_KEY, history);
    this.setData({ searchHistory: history });
  },

  clearHistory() {
    wx.removeStorageSync(HISTORY_KEY);
    this.setData({ searchHistory: [] });
  },

  // ==================== 搜索 ====================
  onKeywordInput(e) {
    this.setData({ keyword: e.detail.value });
  },

  onSearch(e) {
    const keyword = (e.detail.value || this.data.keyword).trim();
    if (!keyword) return;

    this.saveHistory(keyword);
    this.setData({
      searchKeyword: keyword,
      hasSearched: true,
      page: 1,
      videoList: [],
      total: 0,
      hasMore: true
    });
    this.doSearch();
  },

  async doSearch() {
    if (this.data.loading) return;
    this.setData({ loading: true });

    try {
      const { page, size, searchKeyword } = this.data;
      const result = await videoApi.search({ keyword: searchKeyword, page, size });
      const newList = this.data.videoList.concat(result.records || []);

      this.setData({
        videoList: newList,
        total: result.total,
        page: page + 1,
        hasMore: result.records && result.records.length >= size
      });
    } catch (err) {
      console.error('搜索失败:', err);
    } finally {
      this.setData({ loading: false });
    }
  },

  // 点击历史/热门标签
  onTapHistory(e) {
    const keyword = e.currentTarget.dataset.keyword;
    this.setData({ keyword });
    this.onSearch({ detail: { value: keyword } });
  },

  onClear() {
    this.setData({ keyword: '' });
  },

  goBack() {
    wx.navigateBack();
  }
});
