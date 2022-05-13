<template>
  <section id="notFound" class="container is-max-desktop">
    <h1 class="infoHeader">There is nothing here...</h1>
  </section>
</template>

<script>
export default {

};
</script>

<style lang="scss" scoped>
  #notFound {
    display: flex;
    flex-direction: column;
    justify-content: flex-start;
    align-items: center;
    height: 100%;
    padding: 0 $offsetVal + px;
    margin-top: $offsetVal * 2 + px;
  }
</style>