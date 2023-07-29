<template>
  <el-container>
    <el-main>
      <el-row class="flex flex_justify_content_center">
        <h1 class="title">RUC校园墙</h1>
      </el-row>

      <el-row>
        <el-card class="base_card">
          <el-row class="flex_column flex_justify_content_center">
            <h2>注册</h2>
            <el-form :model="form" label-width="60px">
              <el-form-item label="用户名">
                <el-input v-model="form.username"></el-input>
              </el-form-item>
              <el-form-item label="密码">
                <el-input type="password" v-model="form.password"></el-input>
              </el-form-item>
              <el-form-item label="确认">
                <el-input type="password" v-model="form.confirmPassword"></el-input>
              </el-form-item>
              <div class="flex_justify_content_center flex">
                <el-button type="primary" @click="onClickRegisterBtn">注册</el-button>
                <el-button type="success" @click="toLogin">跳转登录</el-button>
              </div>
            </el-form>
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

.flex_column{
  flex-direction: column;
}
</style>

<script setup>
import {ref} from "vue";

import { useRouter } from 'vue-router'
import {ElMessage} from "element-plus";
import {register} from "../api/auth.js";
const router = useRouter()
const form = ref({})

function toLogin(){
  router.push({path:'/login'})
}

function onClickRegisterBtn(){
  if (form.value.username.length == 0 || form.value.password.length == 0 || form.value.confirmPassword.length == 0){
    ElMessage({type: 'error', message: '请输入用户名，密码和确认密码'});
    return;
  }

  if(form.value.password != form.value.confirmPassword){
    ElMessage({type: 'error', message: '两次输入的密码不一致'});
    return;
  }

  register(form.value.username, form.value.password).then(res => {
    if (res.code == 200){
      ElMessage({type: 'success', message: '注册成功'})
      setTimeout(() => {
        router.push({path:'/login'})
      }, 1000)
    }
    else{
      ElMessage({type: 'error', message: res.msg})
    }
  })

}

</script>