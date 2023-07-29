import axios from 'axios'
import {ElNotification, ElMessage} from "element-plus";
import errorCode from "./util/errorCode.js";
import {getToken} from "./util/auth.js";

axios.defaults.headers['Content-Type'] = 'application/json;charset=utf-8';

export function tansParams(params) {
    let result = ''
    for (const propName of Object.keys(params)) {
        const value = params[propName];
        var part = encodeURIComponent(propName) + "=";
        if (value !== null && value !== "" && typeof (value) !== "undefined") {
            if (typeof value === 'object') {
                for (const key of Object.keys(value)) {
                    if (value[key] !== null && value[key] !== "" && typeof (value[key]) !== 'undefined') {
                        let params = propName + '[' + key + ']';
                        var subPart = encodeURIComponent(params) + "=";
                        result += subPart + encodeURIComponent(value[key]) + "&";
                    }
                }
            } else {
                result += part + encodeURIComponent(value) + "&";
            }
        }
    }
    return result
}



// 创建axios实例
const service = axios.create({
    // axios中请求配置有baseURL选项，表示请求URL公共部分
    baseURL: 'http://127.0.0.1:5000',
    // 超时
    timeout: 10000
})
// request拦截器
service.interceptors.request.use(config => {
    const isToken = (config.headers || {}).isToken === false;

    if (getToken() && !isToken) {
        config.headers['Authorization'] = getToken();
    }

    if (config.method === 'get' && config.params){
        let url = config.url + '?' + tansParams(config.params);
        url = url.slice(0, -1);
        config.params = {};
        config.url = url;
    }

    return config
}, error => {
    console.log(error)
    Promise.reject(error)
})

// 响应拦截器
service.interceptors.response.use(res => {
        console.log(res)
        const code = res.data.code || 200;
        const msg = errorCode[code] || res.data.msg || errorCode['default'];

        if(res.request.responseType === 'blob'
        || res.request.responseType === 'arraybuffer'){
            return res.data;
        }

        if (code === 401) {
            return Promise.reject('无效的会话，或者会话已过期，请重新登录。')
        } else if (code === 500) {
            ElMessage({ message: msg, type: 'error' })
            return Promise.reject(new Error(msg))
        } else if (code === 601) {
            ElMessage({ message: msg, type: 'warning' })
            return Promise.reject('error')
        } else if (code !== 200) {
            ElNotification({ title: msg, type: 'error' })
            return Promise.reject('error')
        } else {
            return res.data
        }
    },
    error => {
        let responseData = error.response.data
        // 未设置状态码则默认成功状态
        const code = responseData.code || 500;
        // 获取错误信息
        const msg = responseData.msg || errorCode['default']

        if (code === 401) {
            return Promise.reject('无效的会话，或者会话已过期，请重新登录。')
        } else if (code === 500) {
            ElMessage({ message: msg, type: 'error' })
            return Promise.reject(new Error(msg))
        } else if (code === 601) {
            ElMessage({ message: msg, type: 'warning' })
            return Promise.reject('error')
        } else if (code !== 200) {
            ElNotification({ title: msg, type: 'error' })
            return Promise.reject('error')
        }
        ElMessage({ message: msg, type: 'error'})
        return Promise.reject(error)
    }
)

export default service;