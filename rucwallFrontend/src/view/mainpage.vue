<template>
 <el-container class="outer_container">
   <el-header>
     <div class="flex flex_justify_content_end">
       <div v-if="user_info.username" class="flex flex_justify_content_end flex_align-items_center">
         <p>{{user_info.username}}</p>
         <el-button type="info" @click="onCLickLogout">退出</el-button>
       </div>
       <div v-else class="flex flex_justify_content_end flex_align-items_center">
         <el-button type="primary" @click="toLogin">登录</el-button>
       </div>
     </div>
   </el-header>

   <el-main>
     <el-row class="flex flex_justify_content_center">
       <h1 class="title">RUC校园墙</h1>
     </el-row>
     <el-row>
       <el-card class="base_card">
         <el-input
             v-model="commit_text"
             :rows="7"
             placeholder="分享你的快乐，分担你的忧愁"
             type="textarea"/>
         <el-row class="flex_justify_content_end">
           <el-button class="margin_top_20px" type="primary" @click="onCommit">发表</el-button>
         </el-row>
       </el-card>
     </el-row>

     <el-row>
       <el-card class="base_card margin_top_20px">
         <el-input
             v-model="search_text"
             class="serach_input"
             placeholder="请输入关键词"
         />
         <el-button type="primary" @click="onSearch">搜索</el-button>
       </el-card>
     </el-row>

     <el-row v-for="(post, index) in posts" :key="index">
       <el-card class="base_card margin_top_20px">
         <el-row class="flex_justify_content_space_between flex_align-items_center">
           <p>#{{ post.id }}</p>
           <div class="flex flex_align-items_center">
             <p>{{ post.createTime }}</p>
             <el-dropdown :hide-on-click="false" class="margin_left_5px">
               <!--          <span class="el-dropdown-link">-->
               <!--            Dropdown List<el-icon class="el-icon&#45;&#45;right"><arrow-down/></el-icon>-->
               <!--          </span>-->
               <el-image class="squire_18px" src="/src/assets/options-vertical.png"/>
               <template #dropdown>
                 <el-dropdown-menu>
                   <el-dropdown-item>举报</el-dropdown-item>
                   <el-dropdown-item v-if="post.isYours" @click="onClickDelBtn(post.id)">删除</el-dropdown-item>
                 </el-dropdown-menu>
               </template>
             </el-dropdown>
           </div>
         </el-row>
         <el-row class="content_el_row">
           <p class="content_p">{{ post.content }}</p>
         </el-row>
         <el-row>
           <el-divider/>
         </el-row>

         <el-row class="flex_justify_content_space_between">
           <div class="flex flex_align-items_center">
             <template v-if="post.isLiked">
               <el-image class="squire_18px" src="/src/assets/liked.png" @click="onClickLikeBtn(index)"/>
               <p class="margin_left_5px">{{ post.likeNum }}</p>
             </template>
             <template v-else>
               <el-image class="squire_18px" src="/src/assets/like.png" @click="onClickLikeBtn(index)"/>
               <p class="margin_left_5px">{{ post.likeNum }}</p>
             </template>
           </div>
           <div class="flex flex_align-items_center">
             <el-image class="squire_18px" src="/src/assets/message.png"/>
             <p class="margin_left_5px">{{ post.replyNum }}</p>
           </div>
         </el-row>
       </el-card>
     </el-row>
   </el-main>
 </el-container>

</template>

<style scoped>
.base_card {
  width: 500px;
}

.title {

}

.flex_justify_content_center {
  justify-content: center;
}

.flex_justify_content_start {
  justify-content: flex-start;
}

.flex_justify_content_end {
  justify-content: flex-end;
}

.flex_justify_content_space_between {
  justify-content: space-between;
}

.margin_top_20px {
  margin-top: 20px;
}

.serach_input {
  width: 400px;
}

.content_el_row {
  flex-wrap: wrap;
  height: fit-content;
  word-wrap: break-word;
  word-break: break-all;
}

.content_p {
  text-align: start;

}

.flex {
  display: flex;
}

.squire_18px {
  width: 18px;
  height: 18px;
}

.flex_align-items_center {
  align-items: center;
}

.margin_left_5px {
  margin-left: 5px;
}


.outer_container{
  width: 100%;
}
</style>

<script setup>

import {onMounted, ref} from "vue";
import {useRouter} from "vue-router";
import {getInfo, logout} from "../api/auth.js";
import {listPost, addPost, addPostLike, delPostLike, delPost} from "../api/post.js";
import {removeToken} from "../util/auth.js";
import {ElMessage, ElMessageBox} from "element-plus";

const router = useRouter()
const commit_text = ref('');
const search_text = ref('');

const user_info = ref({});
const posts = ref([]);

function loadUserInfo(){
  getInfo().then(res => {
    user_info.value = res.data.userInfo;
  })
}

function loadPostInfo(){
  listPost().then(res => {
    posts.value = res.data;
  })
}

function loadAllInfo(){
  loadUserInfo();
  loadPostInfo();
}

onMounted(loadAllInfo);

function onCommit() {
  let content = commit_text.value;
  if(content.trim() === ''){
    return;
  }
  content = content.trim();
  addPost(content).then(res => {
    loadPostInfo();
    ElMessage({type:"success", message: res.msg})
  })
}

function onSearch() {

}

function onClickDelBtn(postId){
  ElMessageBox.alert('确定删除该条动态吗？', '删除', {
    confirmButtonText: '确定',
    callback: (action) => {
      if (action === 'confirm') {
        delPost(postId).then(res => {
          loadPostInfo();
          ElMessage({type:'success', message: res.msg});
        })
      }
    },
    cancelButtonText: '取消'
  }
  );
}

function  onClickLikeBtn(index){
  if(posts.value[index].isLiked){
    posts.value[index].isLiked = false;
    posts.value[index].likeNum--;
    delPostLike(posts.value[index].id);
  }else{
    posts.value[index].isLiked = true;
    posts.value[index].likeNum++;
    addPostLike(posts.value[index].id);
  }
}

function toLogin(){
  router.push({path:'/login'})
}

function onCLickLogout(){
  logout().then(() => {
    removeToken();
    loadAllInfo();
  })
}

</script>