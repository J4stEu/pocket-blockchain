<template>
  <div id="app">
    <Header/>
    <Notification/>
    <router-view v-slot="{ Component }">
      <transition name="router">
        <component :is="Component" />
      </transition>
    </router-view>
  </div>
</template>

<script>
import Header from "@/views/Header.vue";
import Notification from "@/components/ui/Notification.vue";
export default {
    components: {
        Header,
        Notification
    }
};
</script>

<style lang="scss">
  .router-enter-from {
    opacity: 0;
  }
  .router-enter-to {
    opacity: 1;
  }
  .router-enter-active {
    transition: all 0.5s ease-in-out;
  }
  #app {
    width: 100vw;
    height: 100vh;
  }
</style>
