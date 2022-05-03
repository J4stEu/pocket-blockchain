<template>
  <nav id="navigation" class="container is-max-desktop">
    <span>
      <slot></slot>
    </span>
    <div v-for="item in navItems" :key="item.id">
      <p @click="setCurrentItem(item)" :class="{routeAccent: selectedItem.id === item.id}">{{item.name}}</p>
    </div>
  </nav>
</template>

<script>
export default {
    props: {
        navItems: {
            type: Array,
            default() {
                return [];
            },
            required: true
        },
        selectedItem: {
            type: Object,
            default() {
                return {};
            },
            required: true
        }
    },
    methods: {
        setCurrentItem(item) {
            this.$emit("setCurrentItem", item);
        }
    },
};
</script>

<style lang="scss" scoped>
  #navigation {
    display: flex;
    align-items: center;
    overflow-x: auto;
    overflow-y: hidden;

    p {
      cursor: pointer;
      top: 1px;
      margin: 0 calc($offsetVal / 2) + px;
      padding: 0;
      border-bottom: 2px solid rgba(0, 0, 0, 0);
      white-space: nowrap;

      &:hover {
        border-bottom: 2px solid $lightGreen;
      }
    }
  }
  .routeAccent {
    border-bottom: 2px solid $lightGreen !important;
  }
</style>