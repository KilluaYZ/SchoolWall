<template>
  <el-container class="outer_container">
    <el-main>

      <el-card class="base_card margin_top_20px">
        <el-row class="flex_justify_content_space_between flex_align-items_center">
          <p>#{{ cur_post.id }}</p>
          <div class="flex flex_align-items_center">
            <p>{{ cur_post.time }}</p>
          </div>
        </el-row>
        <el-row class="content_el_row">
          <p class="content_p">{{ cur_post.content }}</p>
        </el-row>
        <el-row>
          <el-divider/>
        </el-row>

        <el-row class="flex_justify_content_space_between">
          <div class="flex flex_align-items_center">
            <el-image class="squire_18px" src="/src/assets/like.png"/>
            <p class="margin_left_5px">{{ cur_post.likeNum }}</p>
          </div>
          <div class="flex flex_align-items_center">
            <el-image class="squire_18px" src="/src/assets/message.png"/>
            <p class="margin_left_5px">{{ cur_post.replyNum }}</p>
          </div>
        </el-row>
      </el-card>


      <el-row>
        <el-card class="base_card margin_top_20px">
          <el-input
              v-model="commit_text"
              :rows="7"
              placeholder="相知从评论开始"
              type="textarea"/>
          <el-row class="flex_justify_content_end">
            <el-button class="margin_top_20px" type="primary" @click="onCommit">评论</el-button>
          </el-row>
        </el-card>
      </el-row>

      <el-row v-for="(post, index) in posts" :key="index">
        <el-card class="base_card margin_top_20px">
          <el-row class="flex_justify_content_space_between flex_align-items_center">
            <p>#{{ post.id }}</p>
            <div class="flex flex_align-items_center">
              <p>{{ post.time }}</p>
              <el-dropdown :hide-on-click="false" class="margin_left_5px">
                <!--          <span class="el-dropdown-link">-->
                <!--            Dropdown List<el-icon class="el-icon&#45;&#45;right"><arrow-down/></el-icon>-->
                <!--          </span>-->
                <el-image class="squire_18px" src="/src/assets/options-vertical.png"/>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item>举报</el-dropdown-item>
                    <el-dropdown-item>删除</el-dropdown-item>
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

          <el-row class="flex_justify_content_start">
            <div class="flex flex_align-items_center">
              <el-image class="squire_18px" src="/src/assets/like.png"/>
              <p class="margin_left_5px">{{ post.likeNum }}</p>
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

import {ref} from "vue";

const commit_text = ref('');
const search_text = ref('');
const is_login = ref(false);

const posts = ref([
  {
    id: 123,
    content: "hihihihihi",
    time: "2023-07-27 10:00:00",
    likeNum: 10,
    replyNum: 12
  },
  {
    id: 124,
    content: "hihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihi",
    time: "2023-07-27 10:00:00",
    likeNum: 10,
    replyNum: 12
  },
  {
    id: 125,
    content: "hihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihi",
    time: "2023-07-27 10:00:00",
    likeNum: 10,
    replyNum: 12
  },
  {
    id: 126,
    content: "hihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihihi",
    time: "2023-07-27 10:00:00",
    likeNum: 10,
    replyNum: 12
  }
]);

const cur_post = ref({
  id: 333,
  content: "nihaonihaonihaonihaonihaonihaonihaonihaonihaonihaonihaonihaonihaonihaonihaonihaonihaonihaonihaonihaonihaonihaonihaonihaonihao",
  time: "2023-07-22 10:00:00",
  likeNum: 111,
  replyNum: 222
})
function onCommit() {

}

function onSearch() {

}

</script>