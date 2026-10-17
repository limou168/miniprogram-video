// 分类标签栏组件
Component({
  properties: {
    // 分类列表
    list: {
      type: Array,
      value: []
    },
    // 当前选中的分类 ID
    activeId: {
      type: Number,
      value: 0
    }
  },

  methods: {
    onTapTab(e) {
      const { id, name } = e.currentTarget.dataset;
      // 不重复选中
      if (id === this.properties.activeId) return;
      this.triggerEvent('change', { id, name });
    }
  }
});
