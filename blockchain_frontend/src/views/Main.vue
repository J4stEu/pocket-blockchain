<template>
  <section id="main" class="container is-max-desktop">
    <Intro/>
    <Preview/>
  </section>
</template>

<script>
import Preview from "@/components/main/Preview.vue";
import Intro from "@/components/main/Intro.vue";
export default {
    components: {
        Preview,
        Intro,
    }
};
</script>

<style lang="scss" scoped>
  #main {
    display: flex;
    flex-direction: column;
    justify-content: center;
    height: 100%;

    @media screen and (min-height: 0px) and (max-height: 799px) {
      justify-content: flex-start;
    }

  }
</style>