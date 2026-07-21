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

  return new Promise((resolve, reject) => {
    wx.request({
      url: config.baseUrl + url,
      method,
      data,
      header,
      success(res) {
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
      },
      fail(err) {
        wx.showToast({ title: '网络连接失败', icon: 'none' });
        reject(err);
      },
      complete() {
        if (show) {
          hideLoading();
        }
      }
    });
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
