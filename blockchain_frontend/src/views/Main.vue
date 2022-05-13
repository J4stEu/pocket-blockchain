<template>
  <section id="main" class="container is-max-desktop">
    <Intro/>
    <transition appear name="preview">
      <Preview/>
    </transition>
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
  .preview-enter-from {
    transform: translateY(#{$offsetVal + px});
  }
  .preview-enter-to {
    transform: translateY(0);
  }
  .preview-enter-active {
    transition: transform 0.5s ease-in-out;
  }
  #main {
    display: flex;
    flex-direction: column;
    justify-content: center;
    height: 100%;

    @media screen and (min-height: 0px) and (max-height: 799px) {
      justify-content: flex-start;
      padding-bottom: $offsetVal * 2 + px;
    }
  }
</style>