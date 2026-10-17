// 影视卡片组件
Component({
  properties: {
    video: {
      type: Object,
      value: {}
    }
  },

  methods: {
    onTapCard() {
      const videoId = this.properties.video.id;
      if (videoId) {
        wx.navigateTo({
          url: '/pages/detail/detail?id=' + videoId
        });
      }
    }
  }
});
