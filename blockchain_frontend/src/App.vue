<template>
  <div id="app">
    <Header/>
    <Notification/>
    <router-view></router-view>
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
  #app {
    width: 100vw;
    height: 100vh;
  }
</style>
