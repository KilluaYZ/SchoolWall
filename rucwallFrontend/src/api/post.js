import request from "../request.js";

export function listPost() {
    return request({
        url: "/post/list",
        method: "get"
    })
}

export function getPost(postId){
    return request({
        url: "/post/get",
        method: "get",
        params: {
            postId
        }
    })
}

export function addPost(content){
    return request({
        url: "/post/add",
        method: "post",
        data: {
            content
        }
    })
}

export function delPost(postId){
    return request({
        url: "/post/del",
        method: "get",
        params: {
            postId
        }
    })
}

export function addPostLike(postId){
    return request({
        url: "/post/like/add",
        method: "get",
        params: {
            postId
        }
    })
}

export function delPostLike(postId){
    return request({
        url: "/post/like/del",
        method: "get",
        params: {
            postId
        }
    })
}



