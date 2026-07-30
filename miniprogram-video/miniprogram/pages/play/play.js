// 播放页（支持长按快进、倍速播放、多播放源）
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
    loading: true,
    // 播放源
    sources: [],
    currentSourceIndex: 0,
    showSourcePanel: false,
    // 倍速
    playSpeed: 1,
    showSpeedPanel: false,
    speedList: [0.5, 0.75, 1, 1.25, 1.5, 2],
    // 长按快进
    pressing: false,
    fastForwardSpeed: 0,
    pressTimer: null,
    // 播放状态
    isPlaying: true
  },

  onLoad(options) {
    const videoId = options.id;
    const episode = options.episode ? Number(options.episode) : 0;
    const sourceIndex = options.sourceIndex ? Number(options.sourceIndex) : 0;

    if (videoId) {
      this.setData({
        videoId: Number(videoId),
        episodeNumber: episode,
        currentSourceIndex: sourceIndex
      });
      this.loadVideoInfo();
      this.loadSources();
    }
  },

  onUnload() {
    this.saveProgress();
    this.clearPressTimer();
  },

  onHide() {
    this.saveProgress();
    this.clearPressTimer();
  },

  async loadVideoInfo() {
    try {
      this.setData({ loading: true });

      if (this.data.episodeNumber > 0) {
        const episodes = await videoApi.episodes(this.data.videoId);
        const episode = episodes.find(e => e.episodeNumber === this.data.episodeNumber);
        if (episode) {
          this.setData({
            videoUrl: episode.videoUrl || '',
            videoTitle: episode.episodeTitle || ('第' + episode.episodeNumber + '集'),
            loading: false
          });
          this.loadDetailInfo();
          return;
        }
      }

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

  // 加载播放源
  async loadSources() {
    try {
      const sources = await videoApi.sources(this.data.videoId, this.data.episodeNumber);
      this.setData({ sources: sources || [] });
      // 如果当前源索引有效，使用对应URL
      if (sources && sources.length > this.data.currentSourceIndex) {
        const selectedSource = sources[this.data.currentSourceIndex];
        if (selectedSource && selectedSource.sourceUrl) {
          this.setData({ videoUrl: selectedSource.sourceUrl });
        }
      }
    } catch (err) {
      console.error('加载播放源失败:', err);
    }
  },

  // 切换播放源
  switchSource(e) {
    const index = Number(e.currentTarget.dataset.index);
    if (index >= 0 && index < this.data.sources.length) {
      const source = this.data.sources[index];
      this.setData({
        currentSourceIndex: index,
        videoUrl: source.sourceUrl,
        showSourcePanel: false
      });
      // 重新加载视频
      this.initVideo();
      wx.showToast({ title: '已切换至' + source.sourceName, icon: 'none' });
    }
  },

  // 切换倍速
  switchSpeed(e) {
    const speed = Number(e.currentTarget.dataset.speed);
    this.setData({
      playSpeed: speed,
      showSpeedPanel: false
    });
    const videoCtx = wx.createVideoContext('myVideo');
    videoCtx.playbackRate(speed);
    wx.showToast({ title: speed + 'x 倍速', icon: 'none' });
  },

  // 初始化视频（切换源后重新播放）
  initVideo() {
    const videoCtx = wx.createVideoContext('myVideo');
    videoCtx.stop();
    setTimeout(() => {
      videoCtx.play();
      videoCtx.playbackRate(this.data.playSpeed);
    }, 100);
  },

  // ===== 长按快进 =====
  // 手指按下
  onTouchStart(e) {
    // 检测触摸位置 - 只在右侧区域触发快进
    const touch = e.touches[0];
    if (!touch) return;

    const windowWidth = wx.getSystemInfoSync().windowWidth;
    // 右侧40%区域为快进区，左侧40%为快退区
    if (touch.clientX > windowWidth * 0.6) {
      this.data.pressing = true;
      this.data.fastForwardSpeed = 2;
      this.data.pressTimer = setTimeout(() => {
        if (this.data.pressing) {
          this.doFastForward();
        }
      }, 500);
    } else if (touch.clientX < windowWidth * 0.4) {
      this.data.pressing = true;
      this.data.fastForwardSpeed = -2;
      this.data.pressTimer = setTimeout(() => {
        if (this.data.pressing) {
          this.doFastForward();
        }
      }, 500);
    }
  },

  // 手指抬起
  onTouchEnd() {
    this.data.pressing = false;
    this.clearPressTimer();
  },

  clearPressTimer() {
    if (this.data.pressTimer) {
      clearTimeout(this.data.pressTimer);
      this.data.pressTimer = null;
    }
  },

  doFastForward() {
    if (!this.data.pressing) return;
    const videoCtx = wx.createVideoContext('myVideo');
    videoCtx.playbackRate(Math.abs(this.data.fastForwardSpeed));
    wx.showToast({
      title: (this.data.fastForwardSpeed > 0 ? '⏩ 快进' : '⏪ 快退') + Math.abs(this.data.fastForwardSpeed) + 'x',
      icon: 'none',
      duration: 800
    });
    // 1.5秒后恢复原速
    setTimeout(() => {
      if (!this.data.pressing) {
        videoCtx.playbackRate(this.data.playSpeed);
      }
    }, 1500);
  },

  // 点击切换倍速面板
  toggleSpeedPanel() {
    this.setData({
      showSpeedPanel: !this.data.showSpeedPanel,
      showSourcePanel: false
    });
  },

  // 切换播放源面板
  toggleSourcePanel() {
    this.setData({
      showSourcePanel: !this.data.showSourcePanel,
      showSpeedPanel: false
    });
  },

  // 关闭所有面板
  closePanels() {
    this.setData({
      showSpeedPanel: false,
      showSourcePanel: false
    });
  },

  // 播放时间更新（每 5 秒保存进度）
  onTimeUpdate(e) {
    const { currentTime, duration } = e.detail;
    this.setData({
      currentProgress: Math.floor(currentTime),
      duration: Math.floor(duration),
      isPlaying: true
    });

    if (this._saveTimer) return;
    this._saveTimer = setTimeout(() => {
      this.saveProgress();
      this._saveTimer = null;
    }, 5000);
  },

  // 暂停
  onPause() {
    this.setData({ isPlaying: false });
  },

  // 播放
  onPlay() {
    this.setData({ isPlaying: true });
  },

  // 视频加载完成
  onReady() {
    const videoCtx = wx.createVideoContext('myVideo');
    videoCtx.playbackRate(this.data.playSpeed);
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
      // 静默失败
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
