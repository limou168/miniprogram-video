// 播放页
const { videoApi, historyApi } = require('../../utils/api');
const auth = require('../../utils/auth');

Page({
  data: {
    videoId: null,
    episodeNumber: 0,
    videoUrl: '',
    videoTitle: '',
    playCount: 0,
    currentProgress: 0,
    duration: 0,
    loading: true
  },

  onLoad(options) {
    const videoId = options.id;
    const episode = options.episode ? Number(options.episode) : 0;
    if (videoId) {
      this.setData({
        videoId: Number(videoId),
        episodeNumber: episode
      });
      this.loadVideoInfo();
    }
  },

  onUnload() {
    // 退出播放页时保存播放进度
    this.saveProgress();
  },

  onHide() {
    this.saveProgress();
  },

  async loadVideoInfo() {
    try {
      this.setData({ loading: true });

      // 如果有分集参数，先获取分集信息
      if (this.data.episodeNumber > 0) {
        const episodes = await videoApi.episodes(this.data.videoId);
        const episode = episodes.find(e => e.episodeNumber === this.data.episodeNumber);
        if (episode) {
          this.setData({
            videoUrl: episode.videoUrl || '',
            videoTitle: episode.episodeTitle || ('第' + episode.episodeNumber + '集'),
            loading: false
          });
          // 同时获取视频详情补充标题
          this.loadDetailInfo();
          return;
        }
      }

      // 没有分集或未找到分集，使用视频详情中的 URL
      const video = await videoApi.detail(this.data.videoId);
      this.setData({
        videoUrl: video.videoUrl || '',
        videoTitle: video.title || '',
        playCount: video.playCount || 0,
        loading: false
      });
      wx.setNavigationBarTitle({ title: video.title || '正在播放' });
    } catch (err) {
      console.error('加载视频信息失败:', err);
      wx.showToast({ title: '加载失败', icon: 'none' });
      this.setData({ loading: false });
    }
  },

  async loadDetailInfo() {
    try {
      const video = await videoApi.detail(this.data.videoId);
      this.setData({ playCount: video.playCount || 0 });
      const title = video.title + ' - 第' + this.data.episodeNumber + '集';
      this.setData({ videoTitle: title });
      wx.setNavigationBarTitle({ title: title });
    } catch (err) {
      // 不阻塞播放
    }
  },

  // 播放时间更新（每 5 秒保存进度）
  onTimeUpdate(e) {
    const { currentTime, duration } = e.detail;
    this.setData({
      currentProgress: Math.floor(currentTime),
      duration: Math.floor(duration)
    });

    // 每 5 秒自动保存
    if (this._saveTimer) return;
    this._saveTimer = setTimeout(() => {
      this.saveProgress();
      this._saveTimer = null;
    }, 5000);
  },

  // 保存播放进度
  async saveProgress() {
    if (!auth.isLogin() || !this.data.videoId) return;
    try {
      await historyApi.save({
        videoId: this.data.videoId,
        episodeNumber: this.data.episodeNumber,
        progress: this.data.currentProgress,
        duration: this.data.duration
      });
    } catch (err) {
      // 静默失败，不影响观看
    }
  },

  // 视频加载错误
  onVideoError(e) {
    console.error('视频播放错误:', e.detail);
    wx.showToast({ title: '播放失败，请稍后重试', icon: 'none' });
  },

  onShareAppMessage() {
    return {
      title: this.data.videoTitle || '光影影视',
      path: '/pages/detail/detail?id=' + this.data.videoId
    };
  }
});
