// API 配置
const config = {
  // 是否使用 wx.cloud.callContainer（云托管内部调用，无需配置域名白名单）
  useCloudCallContainer: true,

  // 云环境 ID（微信云托管的环境 ID）
  cloudEnv: 'prod-d0gw37vqib56d9311',

  // 后端地址（useCloudCallContainer=false 时使用）
  baseUrl: 'https://springboot-s8q9-285008-9-1313970055.sh.run.tcloudbase.com',

  // 请求超时时间 (毫秒)
  timeout: 15000,

  // 图片基础路径
  imageBaseUrl: 'https://springboot-s8q9-285008-9-1313970055.sh.run.tcloudbase.com'
};

module.exports = config;
