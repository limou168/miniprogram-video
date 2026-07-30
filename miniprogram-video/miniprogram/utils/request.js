/**
 * 统一网络请求封装
 * 原则：只有 needAuth=true 才发 token，401 直接跳登录，不自动刷新（后端需部署后才支持）
 */
const config = require('./config');
const auth = require('./auth');

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

  if (show) showLoading();

  const header = { 'Content-Type': 'application/json' };

  // 只有 needAuth=true 才发 token，避免非认证接口因过期 token 导致 401
  if (needAuth && auth.isLogin()) {
    header['Authorization'] = 'Bearer ' + auth.getToken();
  }

  function handleSuccess(res, resolve, reject) {
    if (res.statusCode === 200) {
      const result = res.data;
      if (result.code === 200) {
        resolve(result.data);
      } else if (result.code === 401) {
        // token 过期，跳转登录
        redirectToLogin();
        reject(result);
      } else {
        wx.showToast({ title: result.message || '请求失败', icon: 'none' });
        reject(result);
      }
    } else if (res.statusCode === 401) {
      redirectToLogin();
      reject(res);
    } else {
      wx.showToast({ title: '网络异常，请稍后重试', icon: 'none' });
      reject(res);
    }
  }

  function redirectToLogin() {
    auth.clearLogin();
    const app = getApp();
    if (app) {
      app.globalData.isLogin = false;
      app.globalData.token = null;
    }
    wx.showToast({ title: '请先登录', icon: 'none' });
    setTimeout(() => {
      wx.navigateTo({ url: '/pages/login/login' });
    }, 1000);
  }

  const handleFail = (err, reject) => {
    console.error('请求失败:', err);
    wx.showToast({ title: '网络连接失败', icon: 'none' });
    reject(err);
  };

  return new Promise((resolve, reject) => {
    const complete = () => { if (show) hideLoading(); };

    if (config.useCloudCallContainer) {
      wx.cloud.callContainer({
        path: url,
        method,
        header: { ...header, 'X-WX-SERVICE': 'springboot-s8q9' },
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

function get(url, params = {}, options = {}) {
  const keys = Object.keys(params).filter(k => params[k] !== undefined && params[k] !== null && params[k] !== '');
  if (keys.length > 0) {
    const query = keys.map(k => encodeURIComponent(k) + '=' + encodeURIComponent(params[k])).join('&');
    url = url + (url.includes('?') ? '&' : '?') + query;
  }
  return request(url, { ...options, method: 'GET', data: {} });
}

function post(url, data = {}, options = {}) {
  return request(url, { ...options, method: 'POST', data });
}

function put(url, data = {}, options = {}) {
  return request(url, { ...options, method: 'PUT', data });
}

function del(url, options = {}) {
  return request(url, { ...options, method: 'DELETE' });
}

module.exports = { request, get, post, put, del };
