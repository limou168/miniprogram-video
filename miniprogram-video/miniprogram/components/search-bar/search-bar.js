// 搜索栏组件
Component({
  properties: {
    // 占位文字
    placeholder: {
      type: String,
      value: '搜索影视...'
    },
    // 是否自动聚焦
    autoFocus: {
      type: Boolean,
      value: false
    },
    // 是否固定在顶部
    fixed: {
      type: Boolean,
      value: false
    }
  },

  data: {
    keyword: ''
  },

  methods: {
    // 输入事件（带防抖）
    onInput(e) {
      const keyword = e.detail.value;
      this.setData({ keyword });

      // 清除之前的定时器
      if (this._timer) {
        clearTimeout(this._timer);
      }
      this._timer = setTimeout(() => {
        this.triggerEvent('input', { keyword });
      }, 300);
    },

    // 确认搜索
    onConfirm(e) {
      const keyword = e.detail.value;
      this.triggerEvent('search', { keyword });
    },

    // 获得焦点
    onFocus() {
      this.triggerEvent('focus');
    },

    // 点击搜索框
    onTapSearch() {
      this.triggerEvent('tap');
    },

    // 清除搜索
    onClear() {
      this.setData({ keyword: '' });
      this.triggerEvent('input', { keyword: '' });
    }
  }
});
