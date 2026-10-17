// 主页（主分类 + 子分类网格 + 按年份）
const { categoryApi, videoApi } = require('../../utils/api');

// 主流子分类精选（情色放最后，需滑动才可见）
const MAIN_TAGS = {
  1: ['动作', '喜剧', '爱情', '科幻', '恐怖', '悬疑', '剧情', '动画', '战争', '武侠', '犯罪', '奇幻', '冒险', '历史', '灾难', '音乐', '纪录片', '情色'],
  2: ['古装', '都市', '爱情', '悬疑', '谍战', '剧情', '喜剧', '科幻', '历史', '战争', '犯罪', '家庭', '偶像', '武侠', '青春'],
  3: ['热血', '冒险', '搞笑', '奇幻', '科幻', '恋爱', '战斗', '悬疑', '恐怖', '校园', '日常', '催泪', '经典'],
  4: ['真人秀', '音乐', '搞笑', '生活', '竞技'],
  5: ['自然', '历史', '科学', '社会', '探索', '军事', '人物']
};

Page({
  data: {
    banners: [],
    categories: [],
    activeCategoryId: 0,
    subCategories: [],
    activeSubCategory: '',
    orderBy: 'year',
    excludeTag: '情色',
    videoList: [],
    page: 1,
    size: 20,
    hasMore: true,
    loading: false
  },

  onLoad() {
    this.loadCategories();
    this.loadBanners();
    this.loadVideoList();
  },

  onPullDownRefresh() {
    this.setData({ page: 1, videoList: [], hasMore: true });
    this.loadBanners();
    this.loadVideoList();
    wx.stopPullDownRefresh();
  },

  onReachBottom() {
    if (this.data.hasMore && !this.data.loading) this.loadVideoList();
  },

  async loadBanners() {
    try {
      const result = await videoApi.list({ page: 1, size: 5, orderBy: 'year' });
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
        // 默认展示过滤掉情色类
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
      console.error('加载影视列表失败:', err);
    } finally {
      this.setData({ loading: false });
    }
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
