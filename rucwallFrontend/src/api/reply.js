import request from "../request.js";


export function addReply(postId, content){
    return request({
        url: "/post/reply/add",
        method: "post",
        data: {
            content,
            postId
        }
    })
}

export function delReply(replyId){
    return request({
        url: "/post/reply/del",
        method: "get",
        params: {
            replyId
        }
    })
}

export function addReplyLike(replyId){
    return request({
        url: "/post/reply/like/add",
        method: "get",
        params: {
            replyId
        }
    })
}

export function delReplyLike(replyId){
    return request({
        url: "/post/reply/like/del",
        method: "get",
        params: {
            replyId
        }
    })
}