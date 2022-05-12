<template>
  <div id="notification" :class="{successColor: success, errorColor: !success }" v-if="show" @click="notification.reset">
    <span>{{text}}</span>
  </div>
</template>

<script>
import {useNotificationStore} from "@/hooks/useNotificationStore.js";
export default {
    setup() {
        const {notification, text, show, success} = useNotificationStore();
        return {
            notification,
            text,
            show,
            success
        };
    }
};
</script>

<style lang="scss" scoped>
  #notification {
    position: fixed;
    z-index: 3;
    right: $offsetVal + px;
    top: $offsetVal + px;
    width: 300px;
    height: 50px;
    display: flex;
    justify-content: flex-start;
    align-items: center;
    border-radius: calc($offsetVal / 4) + px;

    span {
      margin-left: $offsetVal + px;
    }
  }
  .successColor {
    background: #dbf6ef;
  }
  .errorColor {
    background: $red;
  }
</style>