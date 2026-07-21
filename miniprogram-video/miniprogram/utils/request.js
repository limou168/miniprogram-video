/**
 * 统一网络请求封装
 */
const config = require('./config');
const auth = require('./auth');

// 显示 loading 的请求计数
let requestCount = 0;

function showLoading() {
  if (requestCount === 0) {
    wx.showLoading({ title: '加载中...', mask: true });
  }
  requestCount++;
}

function hideLoading() {
  requestCount--;
  if (requestCount <= 0) {
    requestCount = 0;
    wx.hideLoading();
  }
}

function request(url, options = {}) {
  const {
    method = 'GET',
    data = {},
    showLoading: show = true,
    needAuth = false
  } = options;

  if (show) {
    showLoading();
  }

  const header = {
    'Content-Type': 'application/json'
  };

  // 需要认证的接口带上 token
  if (needAuth) {
    const token = auth.getToken();
    if (token) {
      header['Authorization'] = 'Bearer ' + token;
    }
  }

  // 统一处理成功/失败的回调逻辑
  const handleSuccess = (res, resolve, reject) => {
    if (res.statusCode === 200) {
      const result = res.data;
      if (result.code === 200) {
        resolve(result.data);
      } else if (result.code === 401) {
        // token 过期，清除登录状态
        auth.clearLogin();
        const app = getApp();
        app.globalData.isLogin = false;
        app.globalData.token = null;
        wx.showToast({ title: '登录已过期，请重新登录', icon: 'none' });
        setTimeout(() => {
          wx.navigateTo({ url: '/pages/login/login' });
        }, 1500);
        reject(result);
      } else {
        wx.showToast({ title: result.message || '请求失败', icon: 'none' });
        reject(result);
      }
    } else if (res.statusCode === 401) {
      auth.clearLogin();
      wx.showToast({ title: '登录已过期，请重新登录', icon: 'none' });
      setTimeout(() => {
        wx.navigateTo({ url: '/pages/login/login' });
      }, 1500);
      reject(res);
    } else {
      wx.showToast({ title: '网络异常，请稍后重试', icon: 'none' });
      reject(res);
    }
  };

  const handleFail = (err, reject) => {
    console.error('请求失败:', err);
    wx.showToast({ title: '网络连接失败', icon: 'none' });
    reject(err);
  };

  return new Promise((resolve, reject) => {
    const complete = () => {
      if (show) {
        hideLoading();
      }
    };

    if (config.useCloudCallContainer) {
      // 使用云托管内部调用（无需配置域名白名单）
      // 必须指定 X-WX-SERVICE 为云托管的服务名称
      const cloudHeader = {
        ...header,
        'X-WX-SERVICE': 'springboot-s8q9'
      };
      wx.cloud.callContainer({
        path: url,
        method,
        header: cloudHeader,
        data,
        apiVersion: 2, // 避免 INVALID_PATH 缓存问题
        success: (res) => handleSuccess(res, resolve, reject),
        fail: (err) => handleFail(err, reject),
        complete
      });
    } else {
      // 使用传统 wx.request（需要配置域名白名单）
      wx.request({
        url: config.baseUrl + url,
        method,
        data,
        header,
        success: (res) => handleSuccess(res, resolve, reject),
        fail: (err) => handleFail(err, reject),
        complete
      });
    }
  });
}

// GET 请求
function get(url, params = {}, options = {}) {
  // 将 params 转为 query string
  const keys = Object.keys(params).filter(k => params[k] !== undefined && params[k] !== null && params[k] !== '');
  if (keys.length > 0) {
    const query = keys.map(k => encodeURIComponent(k) + '=' + encodeURIComponent(params[k])).join('&');
    url = url + (url.includes('?') ? '&' : '?') + query;
  }
  return request(url, { ...options, method: 'GET', data: {} });
}

// POST 请求
function post(url, data = {}, options = {}) {
  return request(url, { ...options, method: 'POST', data });
}

// PUT 请求
function put(url, data = {}, options = {}) {
  return request(url, { ...options, method: 'PUT', data });
}

// DELETE 请求
function del(url, options = {}) {
  return request(url, { ...options, method: 'DELETE' });
}

module.exports = {
  request,
  get,
  post,
  put,
  del
};
