// 分类影视列表页（支持二级分类）
const { categoryApi, videoApi } = require('../../utils/api');

Page({
  data: {
    categories: [],
    activeCategoryId: 0,
    // 二级分类（标签）
    tags: [],
    activeTag: '',
    showTagPanel: false,
    pendingCategoryId: 0,
    pendingTag: '',
    // 排序
    orderBy: 'play_count',
    orderOptions: [
      { key: 'play_count', name: '热门' },
      { key: 'time', name: '最新' },
      { key: 'score', name: '评分' }
    ],
    // 视频列表
    videoList: [],
    page: 1,
    size: 20,
    hasMore: true,
    loading: false
  },

  onLoad(options) {
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

  async loadTags(categoryId) {
    if (!categoryId || categoryId === 0) {
      this.setData({ tags: [] });
      return;
    }
    try {
      const tags = await videoApi.tags(categoryId);
      this.setData({ tags });
    } catch (err) {
      console.error('加载标签失败:', err);
    }
  },

  async loadVideoList() {
    if (this.data.loading) return;
    this.setData({ loading: true });

    try {
      const { page, size, activeCategoryId, activeTag, orderBy } = this.data;
      const params = { page, size, orderBy };
      if (activeCategoryId > 0) {
        params.categoryId = activeCategoryId;
      }
      // 如果有选中的二级标签，作为关键词筛选
      if (activeTag) {
        params.keyword = activeTag;
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

  // 主分类点击 - 打开二级分类面板
  onCategoryTap(e) {
    const { id, name } = e.currentTarget.dataset;
    if (id === 0) {
      // 全部：直接切换，清除二级分类
      this.setData({
        activeCategoryId: 0,
        activeTag: '',
        tags: [],
        page: 1,
        videoList: [],
        hasMore: true
      });
      this.loadVideoList();
    } else {
      // 打开二级分类面板
      this.setData({
        pendingCategoryId: id,
        pendingTag: '',
        showTagPanel: true
      });
      this.loadTags(id);
    }
  },

  // 选择二级分类标签
  onSelectTag(e) {
    const tag = e.currentTarget.dataset.tag || '';
    this.setData({ pendingTag: tag });
  },

  // 确认按钮
  onConfirmCategory() {
    const { pendingCategoryId, pendingTag } = this.data;
    this.setData({
      activeCategoryId: pendingCategoryId,
      activeTag: pendingTag,
      showTagPanel: false,
      page: 1,
      videoList: [],
      hasMore: true
    });
    this.loadVideoList();
  },

  // 取消二级分类选择
  onCancelCategory() {
    this.setData({ showTagPanel: false });
  },

  // 排序切换
  onOrderChange(e) {
    const orderBy = e.currentTarget.dataset.key;
    this.setData({
      orderBy,
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
