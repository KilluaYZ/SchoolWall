import request from "../request.js";

export function login(username,  password) {
    return request({
        url: "/auth/login",
        method: "post",
        headers:{
          isToken: false
        },
        data: {
            username,
            password
        }
    })
}

export function register(username, password){
    return request({
        url: "/auth/register",
        method: "post",
        headers:{
          isToken: false
        },
        data: {
            username,
            password
        }
    })
}

export function logout() {
    return request({
        url: "/auth/logout",
        method: "get"
    })
}

export function getInfo() {
    return request({
        url: "/auth/profile",
        method: "get"
    })
}
