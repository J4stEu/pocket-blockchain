<template>
  <div id="dialog" v-if="show" @click.stop="showDialog">
    <div @click.stop class="dialogContent container is-max-desktop">
      <slot></slot>
    </div>
  </div>
</template>

<script>
export default {
    props: {
        show: {
            type: Boolean,
            default: false
        }
    },
    methods: {
        showDialog() {
            this.$emit("show");
        }
    }
};
</script>

<style lang="scss" scoped>
  #dialog {
    top: 0;
    bottom: 0;
    right: 0;
    left: 0;
    position: fixed;
    background: rgba(0, 0, 0, 0.5);
    display: flex;
    justify-content: flex-start;
    align-items: center;

    .dialogContent {
      position: relative;
      margin: auto;
      background: white;
      max-height: calc(100vh - #{$offsetVal * 7 + px});
      overflow: auto;
      border-radius: $offsetVal + px;

      @media screen and (min-width: 0px) and (max-width: 1023px) {
        margin: 0 $offsetVal + px;
      }
    }
  }
</style>