<template>
  <transition name="notification">
    <div id="notification" :class="{successColor: success, errorColor: !success}" v-if="show" @click="notification.reset">
      <span>{{cutText(text)}}</span>
    </div>
  </transition>
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
    },
    methods: {
        cutText(text) {
            return text.length > 30 ? text.slice(0, 30) + "..." : text;
        }
    }
};
</script>

<style lang="scss" scoped>
  .notification-enter-from, .notification-leave-to {
    transform: translateX(30px);
  }
  .notification-enter-to, .notification-leave-from {
    transform: translateX(0);
  }
  .notification-enter-active, .notification-leave-active {
    transition: all 0.5s ease-in-out;
  }
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
    transition: opacity 0.2s linear;
    cursor: pointer;
    box-shadow: $shadow;

    &:hover {
      opacity: 0.8;
    }

    span {
      margin-left: $offsetVal + px;
      white-space: nowrap;
    }
  }
  .successColor {
    background: #dbf6ef;
  }
  .errorColor {
    background: $red;
  }
  .warningColor {
    background: $yellow;
  }
</style>