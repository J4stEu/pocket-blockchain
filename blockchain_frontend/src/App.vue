<template>
  <div id="app">
    <Header/>
    <router-view></router-view>
  </div>
</template>

<script>
import Header from "@/views/Header.vue";
export default {
    components: {
        Header
    }
};
</script>

<style lang="scss">
  #app {
    width: 100vw;
    height: 100vh;
  }
</style>
