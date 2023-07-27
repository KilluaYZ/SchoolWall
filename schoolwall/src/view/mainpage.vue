

<template>
  <el-row class="flex_justify_content_center">
    <h1 class="title">RUC校园墙</h1>
  </el-row>
<el-row>
  <el-card class="base_card">
    <el-input
        v-model="commit_text"
        :rows="7"
        type="textarea"
        placeholder="分享你的快乐，分担你的忧愁" />
    <el-row class="flex_justify_content_end" >
      <el-button type="primary" class="margin_top_20px" @click="onCommit">发表</el-button>
    </el-row>
  </el-card>
</el-row>

  <el-row>
    <el-card class="base_card margin_top_20px">
      <el-input
        v-model="search_text"
        placeholder="请输入关键词"
        class="serach_input"
      />
      <el-button type="primary"  @click="onSearch">搜索</el-button>
    </el-card>
  </el-row>

    <el-row v-for="(post, index) in posts" :key="index">
      <el-card class="base_card margin_top_20px">
        <el-row class="flex_justify_content_space_between">
          <p>#{{post.id}}</p>
          <p>{{post.time}}</p>
        </el-row>
        <el-row class="content_el_row">
          <p class="content_p">{{post.content}}</p>
        </el-row>
        <el-row>
          <el-divider />
        </el-row>

        <el-row class="flex_justify_content_space_between">
          <div>

          </div>
        </el-row>
      </el-card>
    </el-row>

</template>

<style scoped>
.base_card{
  width: 500px;
}

.title{

}

.flex_justify_content_center{
  justify-content: center;
}

.flex_justify_content_start{
  justify-content: flex-start;
}

.flex_justify_content_end{
  justify-content: flex-end;
}

.flex_justify_content_space_between{
  justify-content: space-between;
}

.margin_top_20px{
  margin-top: 20px;
}

.serach_input{
  width: 400px;
}

.content_el_row{
  flex-wrap: wrap;
  height: fit-content;
  word-wrap: break-word;
  word-break: break-all;
}

.content_p{
  text-align: start;

}


</style>

<script setup>

import {ref} from "vue";

const commit_text = ref('');
const search_text = ref('');
const posts = ref([
  {
    id: 123,
    content: "hihihihihi",
    time: "2023-07-27 10:00:00"
  },
  {
    id: 124,
    content: "hihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihi",
    time: "2023-07-27 10:00:00"
  },
  {
    id: 125,
    content: "hihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihi",
    time: "2023-07-27 10:00:00"
  },
  {
    id: 126,
    content: "hihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihi",
    time: "2023-07-27 10:00:00"
  }
]);


function onCommit(){

}

function onSearch(){

}

</script>