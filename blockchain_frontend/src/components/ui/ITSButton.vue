<template>
  <a v-if="isSrc" :href="src" target="_blank" class="buttonColor">
    <slot name="beforeIcon"></slot>
    <p v-if="text.length !== 0">{{text}}</p>
    <slot name="afterIcon"></slot>
  </a>
  <div v-else class="buttonColor">
    <slot name="beforeIcon"></slot>
    <p v-if="text.length !== 0">{{text}}</p>
    <slot name="afterIcon"></slot>
  </div>
</template>

<script>
export default {
    props: {
        isSrc: {
            type: Boolean,
            default: false,
        },
        src: {
            type: String,
            default: ""
        },
        text: {
            type: String,
            default: ""
        },
        buttonColor: {
            type: String,
            default: ""
        }
    }
};
</script>

<style lang="scss" scoped>
  a, div {
    display: inline-flex !important;
    border-radius: calc($offsetVal / 4) + px;
    align-items: center;
    text-decoration: none;
    color: black;
    padding: calc($offsetVal / 4) + px;
    cursor: pointer;
    transition: opacity 0.2s linear;

    &:hover {
      opacity: 0.8;
    }
  }
  p {
    padding: 0 calc($offsetVal / 4) + px 0 calc($offsetVal / 4) + px;
    white-space:nowrap;
  }
  .buttonColor {
    background: v-bind(buttonColor);
  }
</style>