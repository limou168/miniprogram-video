/**
 * 统一网络请求封装（支持 Token 自动续期）
 */
const config = require('./config');
const auth = require('./auth');

// 是否正在刷新 token
let isRefreshing = false;
// 等待刷新 token 的请求队列
let refreshQueue = [];

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

/**
 * 刷新 token
 */
function refreshToken() {
  return new Promise((resolve, reject) => {
    const oldToken = auth.getToken();
    if (!oldToken) {
      reject('no token');
      return;
    }
    wx.request({
      url: (config.useCloudCallContainer ? '' : config.baseUrl) + '/api/user/refresh',
      method: 'POST',
      header: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + oldToken
      },
      success: (res) => {
        if (res.data && res.data.code === 200 && res.data.data && res.data.data.token) {
          const newToken = res.data.data.token;
          auth.setToken(newToken);
          resolve(newToken);
        } else {
          reject('refresh failed');
        }
      },
      fail: () => reject('network error')
    });
  });
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
  } else {
    // 即使不需要认证，如果有 token 也带上（方便服务端识别用户）
    const token = auth.getToken();
    if (token) {
      header['Authorization'] = 'Bearer ' + token;
    }
  }

  const handleSuccess = (res, resolve, reject) => {
    if (res.statusCode === 200) {
      const result = res.data;
      if (result.code === 200) {
        resolve(result.data);
      } else if (result.code === 401) {
        // token 过期，尝试自动续期
        handleTokenExpired(res, resolve, reject, url, options);
      } else {
        wx.showToast({ title: result.message || '请求失败', icon: 'none' });
        reject(result);
      }
    } else if (res.statusCode === 401) {
      handleTokenExpired(res, resolve, reject, url, options);
    } else {
      wx.showToast({ title: '网络异常，请稍后重试', icon: 'none' });
      reject(res);
    }
  };

  /**
   * 处理 token 过期：尝试刷新，刷新后重放请求
   */
  function handleTokenExpired(originalRes, originalResolve, originalReject, originalUrl, originalOptions) {
    if (!auth.isLogin()) {
      // 未登录状态，跳转登录
      auth.clearLogin();
      const app = getApp();
      if (app) {
        app.globalData.isLogin = false;
        app.globalData.token = null;
      }
      wx.showToast({ title: '登录已过期，请重新登录', icon: 'none' });
      setTimeout(() => {
        wx.navigateTo({ url: '/pages/login/login' });
      }, 1500);
      originalReject(originalRes);
      return;
    }

    if (!isRefreshing) {
      isRefreshing = true;
      refreshToken().then(newToken => {
        isRefreshing = false;
        // 重放等待队列中的请求
        refreshQueue.forEach(cb => cb(newToken));
        refreshQueue = [];
        // 重放当前请求
        originalOptions.needAuth = true;
        originalOptions.showLoading = false;
        request(originalUrl, originalOptions).then(originalResolve).catch(originalReject);
      }).catch(() => {
        isRefreshing = false;
        refreshQueue = [];
        // 刷新失败，清除登录状态
        auth.clearLogin();
        const app = getApp();
        if (app) {
          app.globalData.isLogin = false;
          app.globalData.token = null;
        }
        wx.showToast({ title: '登录已过期，请重新登录', icon: 'none' });
        setTimeout(() => {
          wx.navigateTo({ url: '/pages/login/login' });
        }, 1500);
        originalReject(originalRes);
      });
    } else {
      // 正在刷新中，加入队列等待
      refreshQueue.push((newToken) => {
        originalOptions.needAuth = true;
        originalOptions.showLoading = false;
        request(originalUrl, originalOptions).then(originalResolve).catch(originalReject);
      });
    }
  }

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
      const cloudHeader = {
        ...header,
        'X-WX-SERVICE': 'springboot-s8q9'
      };
      wx.cloud.callContainer({
        path: url,
        method,
        header: cloudHeader,
        data,
        apiVersion: 2,
        success: (res) => handleSuccess(res, resolve, reject),
        fail: (err) => handleFail(err, reject),
        complete
      });
    } else {
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
