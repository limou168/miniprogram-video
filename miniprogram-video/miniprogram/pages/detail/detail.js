// 影视详情页
const { videoApi, favoriteApi } = require('../../utils/api');
const auth = require('../../utils/auth');

Page({
  data: {
    video: null,
    videoId: null,
    isFavorite: false,
    recommendList: [],
    episodes: [],
    currentEpisode: 1,
    showEpisodes: false
  },

  onLoad(options) {
    const videoId = options.id;
    if (videoId) {
      this.setData({ videoId: Number(videoId) });
      this.loadDetail();
      this.loadRecommend();
      this.checkFavorite();
    }
  },

  async loadDetail() {
    try {
      const video = await videoApi.detail(this.data.videoId);
      this.setData({ video });
      wx.setNavigationBarTitle({ title: video.title || '影视详情' });

      // 如果是电视剧，加载分集列表
      if (video.categoryId === 2) {
        this.loadEpisodes();
      }
    } catch (err) {
      console.error('加载详情失败:', err);
      wx.showToast({ title: '加载失败', icon: 'none' });
    }
  },

  async loadEpisodes() {
    try {
      const episodes = await videoApi.episodes(this.data.videoId);
      this.setData({ episodes, currentEpisode: 1 });
    } catch (err) {
      console.error('加载分集失败:', err);
    }
  },

  async loadRecommend() {
    try {
      const result = await videoApi.list({ page: 1, size: 6 });
      this.setData({ recommendList: (result.records || []).slice(0, 6) });
    } catch (err) {
      console.error('加载推荐失败:', err);
    }
  },

  async checkFavorite() {
    if (!auth.isLogin()) return;
    try {
      const isFav = await favoriteApi.check(this.data.videoId);
      this.setData({ isFavorite: isFav });
    } catch (err) {
      // 不处理
    }
  },

  // 选集切换
  selectEpisode(e) {
    const episode = Number(e.currentTarget.dataset.episode);
    this.setData({ currentEpisode: episode });
  },

  // 展开/收起选集
  toggleEpisodes() {
    this.setData({ showEpisodes: !this.data.showEpisodes });
  },

  // 播放
  goPlay() {
    const { videoId, currentEpisode, video } = this.data;
    // 电视剧带分集参数，电影不带
    if (video && video.categoryId === 2) {
      wx.navigateTo({ url: '/pages/play/play?id=' + videoId + '&episode=' + currentEpisode });
    } else {
      wx.navigateTo({ url: '/pages/play/play?id=' + videoId });
    }
  },

  // 收藏/取消收藏
  async onToggleFavorite() {
    if (!auth.isLogin()) {
      wx.showToast({ title: '请先登录', icon: 'none' });
      setTimeout(() => {
        wx.navigateTo({ url: '/pages/login/login' });
      }, 1000);
      return;
    }
    try {
      const isFav = await favoriteApi.toggle(this.data.videoId);
      this.setData({ isFavorite: isFav });
      wx.showToast({ title: isFav ? '已收藏' : '已取消收藏', icon: 'none' });
    } catch (err) {
      console.error('收藏操作失败:', err);
    }
  },

  // 返回
  goBack() {
    wx.navigateBack();
  },

  // 分享
  onShareAppMessage() {
    return {
      title: this.data.video ? this.data.video.title : '光影影视',
      path: '/pages/detail/detail?id=' + this.data.videoId
    };
  }
});
