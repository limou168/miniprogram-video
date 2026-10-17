// 分类页（主分类 + 子分类网格 + 排序 + 过滤情色）
const { categoryApi, videoApi } = require('../../utils/api');

// 主流子分类精选（情色放最后）
const MAIN_TAGS = {
  1: ['动作', '喜剧', '爱情', '科幻', '恐怖', '悬疑', '剧情', '动画', '战争', '武侠', '犯罪', '奇幻', '冒险', '历史', '灾难', '音乐', '纪录片', '情色'],
  2: ['古装', '都市', '爱情', '悬疑', '谍战', '剧情', '喜剧', '科幻', '历史', '战争', '犯罪', '家庭', '偶像', '武侠', '青春'],
  3: ['热血', '冒险', '搞笑', '奇幻', '科幻', '恋爱', '战斗', '悬疑', '恐怖', '校园', '日常', '催泪', '经典'],
  4: ['真人秀', '音乐', '搞笑', '生活', '竞技'],
  5: ['自然', '历史', '科学', '社会', '探索', '军事', '人物']
};

Page({
  data: {
    categories: [],
    activeCategoryId: 0,
    subCategories: [],
    activeSubCategory: '',
    orderBy: 'year',
    orderOptions: [
      { key: 'year', name: '最近几年' },
      { key: 'play_count', name: '热门' },
      { key: 'score', name: '评分' }
    ],
    excludeTag: '情色',
    videoList: [],
    page: 1,
    size: 20,
    hasMore: true,
    loading: false
  },

  onLoad(options) {
    if (options.categoryId) {
      const id = Number(options.categoryId);
      this.setData({ activeCategoryId: id, subCategories: MAIN_TAGS[id] || [] });
    }
    this.loadCategories();
    this.loadVideoList();
  },

  onReachBottom() {
    if (this.data.hasMore && !this.data.loading) this.loadVideoList();
  },

  async loadCategories() {
    try {
      const categories = await categoryApi.list();
      this.setData({ categories });
    } catch (err) {
      console.error('加载分类失败:', err);
    }
  },

  onCategoryTap(e) {
    const id = Number(e.currentTarget.dataset.id);
    this.setData({
      activeCategoryId: id,
      activeSubCategory: '',
      subCategories: MAIN_TAGS[id] || [],
      page: 1, videoList: [], hasMore: true
    });
    this.loadVideoList();
  },

  onSubCategoryTap(e) {
    const tag = e.currentTarget.dataset.tag || '';
    this.setData({
      activeSubCategory: tag,
      page: 1, videoList: [], hasMore: true
    });
    this.loadVideoList();
  },

  async loadVideoList() {
    if (this.data.loading) return;
    this.setData({ loading: true });

    try {
      const { page, size, activeCategoryId, activeSubCategory, orderBy, excludeTag } = this.data;
      const params = { page, size, orderBy };
      if (activeCategoryId > 0) params.categoryId = activeCategoryId;
      if (activeSubCategory) {
        params.tag = activeSubCategory;
      } else {
        // 默认过滤情色类
        params.excludeTag = excludeTag;
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

  onOrderChange(e) {
    const orderBy = e.currentTarget.dataset.key;
    this.setData({
      orderBy,
      page: 1, videoList: [], hasMore: true
    });
    this.loadVideoList();
  },

  goSearch() {
    wx.navigateTo({ url: '/pages/search/search' });
  }
});
