<template>
<el-container>
  <el-main>
    <el-row class="flex flex_justify_content_center">
      <h1 class="title">RUC校园墙</h1>
    </el-row>

    <el-row>
      <el-card class="base_card">
        <el-row class="flex_column flex_justify_content_center">
          <h2>登录</h2>
          <el-form :model="form" label-width="60px">
            <el-form-item label="用户名">
              <el-input v-model="form.username"></el-input>
            </el-form-item>
            <el-form-item label="密码">
              <el-input type="password" v-model="form.password"></el-input>
            </el-form-item>
            <div class="flex_justify_content_center flex">
              <el-button type="primary" @click="onClickLoginBtn">登录</el-button>
              <el-button type="success" @click="toRegister">跳转注册</el-button>
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
import {login} from "../api/auth.js";
import {ElMessage} from "element-plus";
import {setToken} from "../util/auth.js";

const router = useRouter()

const form = ref({})

function toRegister(){
  router.push({path:'/register'})
}

function onClickLoginBtn(){
  if (form.value.username.length == 0 || form.value.password.length == 0){
    ElMessage({type: 'error', message: '请输入用户名和密码'});
    return;
  }
  login(form.value.username, form.value.password).then(res => {
    if (res.code == 200){
      ElMessage({type: 'success', message: '登录成功'})
      setToken(res.data.token);
      router.push({path:'/'})
    }
    else{
      ElMessage({type: 'error', message: res.msg})
    }
  })

}


</script>