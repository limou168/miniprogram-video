// 搜索页（增强版：实时搜索建议 + 快速响应）
const { videoApi } = require('../../utils/api');

const HISTORY_KEY = 'search_history';
const MAX_HISTORY = 10;

Page({
  data: {
    keyword: '',
    searchKeyword: '',
    hasSearched: false,
    searchHistory: [],
    hotKeys: [],

    // 搜索建议
    suggestions: [],
    showSuggestions: false,
    _suggestTimer: null,
    _searchTimer: null,

    // 搜索结果
    videoList: [],
    total: 0,
    page: 1,
    size: 20,
    hasMore: true,
    loading: false,

    showNoResult: false
  },

  onLoad(options) {
    this.loadHistory();
    this.loadHotKeys();

    if (options.keyword) {
      const keyword = decodeURIComponent(options.keyword);
      this.setData({ keyword });
      this.startSearch(keyword);
    }
  },

  onUnload() {
    if (this.data._suggestTimer) clearTimeout(this.data._suggestTimer);
    if (this.data._searchTimer) clearTimeout(this.data._searchTimer);
  },

  onReachBottom() {
    if (this.data.hasSearched && this.data.hasMore && !this.data.loading) {
      this.loadMore();
    }
  },

  // ==================== 搜索历史 ====================
  loadHistory() {
    const history = wx.getStorageSync(HISTORY_KEY) || [];
    this.setData({ searchHistory: history });
  },

  saveHistory(keyword) {
    let history = wx.getStorageSync(HISTORY_KEY) || [];
    history = history.filter(item => item !== keyword);
    history.unshift(keyword);
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

  // 获取热门搜索
  async loadHotKeys() {
    try {
      // 直接用播放量最高的视频标题作为热门搜索
      const result = await videoApi.list({ page: 1, size: 10, orderBy: 'play_count' });
      const hotKeys = (result.records || []).map(v => v.title).filter(Boolean);
      this.setData({ hotKeys });
    } catch (err) {
      console.error('加载热门搜索失败:', err);
    }
  },

  // ==================== 搜索建议 ====================
  onKeywordInput(e) {
    const keyword = e.detail.value;
    this.setData({ keyword });

    if (this.data._suggestTimer) {
      clearTimeout(this.data._suggestTimer);
    }
    if (this.data._searchTimer) {
      clearTimeout(this.data._searchTimer);
    }

    if (!keyword.trim()) {
      this.setData({ suggestions: [], showSuggestions: false });
      return;
    }

    // 防抖 200ms 后请求建议
    const timer = setTimeout(async () => {
      try {
        const suggestions = await videoApi.suggest({ keyword: keyword.trim(), limit: 8 });
        this.setData({
          suggestions,
          showSuggestions: suggestions.length > 0
        });
      } catch (err) {
        console.error('获取搜索建议失败:', err);
      }
    }, 200);
    this.setData({ _suggestTimer: timer });
  },

  onTapSuggestion(e) {
    const keyword = e.currentTarget.dataset.keyword;
    this.setData({ keyword, showSuggestions: false });
    this.startSearch(keyword);
  },

  // ==================== 搜索 ====================
  onSearch(e) {
    const keyword = (e.detail.value || this.data.keyword).trim();
    if (!keyword) return;
    this.setData({ showSuggestions: false });
    this.startSearch(keyword);
  },

  startSearch(keyword) {
    this.saveHistory(keyword);
    this.setData({
      searchKeyword: keyword,
      hasSearched: true,
      page: 1,
      videoList: [],
      total: 0,
      hasMore: true,
      showNoResult: false
    });
    this.loadMore();
  },

  async loadMore() {
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
        hasMore: result.records && result.records.length >= size,
        loading: false,
        showNoResult: newList.length === 0
      });
    } catch (err) {
      console.error('搜索失败:', err);
      this.setData({ loading: false });
    }
  },

  // ==================== 事件 ====================
  onTapHistory(e) {
    const keyword = e.currentTarget.dataset.keyword;
    this.setData({ keyword, showSuggestions: false });
    this.startSearch(keyword);
  },

  onClear() {
    this.setData({ keyword: '', suggestions: [], showSuggestions: false });
  },

  goBack() {
    wx.navigateBack();
  }
});
