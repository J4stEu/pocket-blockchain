<template>
  <div
      id="bio"
      class="
        container
        is-max-desktop
    "
  >
    <transition appear name="info-header">
      <h1 class="infoHeader"> {{ title }} </h1>
    </transition>
    <div>
      <p
          v-for="(option, optionName) in options"
          :key="optionName"
      >
        <span>{{ option.option }}:</span>
        <span>{{ option.parameter }}</span>
      </p>
    </div>
  </div>
</template>

<script>
export default {
    props: {
        title: {
            type: String,
            default: ""
        },
        options: {
            type: Object,
            default () {
                return {
                    option: "1999",
                    parameter: "Born in Chita, Russia"
                };
            }
        }
    }
};
</script>

<style lang="scss" scoped>
  .info-header-enter-from {
    transform: translateY(-#{$offsetVal + px});
  }
  .info-header-enter-to {
    transform: translateY(0);
  }
  .info-header-enter-active {
    transition: transform 0.4s ease-in-out;
  }
  #bio {
    margin: 0;
    margin-top: $offsetVal * 2 + px;
    //padding: 0px $offsetVal + px;
    color: black;
    display: flex;
    justify-content: flex-start;
    align-items: center;
  }
  div {
    display: flex;
    flex-direction: column;

    p {
      display: flex;
      margin-top: calc($offsetVal / 2) + px;
      text-align: justify;

      span {
        text-indent: initial;

        &:first-child {
          color: $brown;
          text-decoration: underline;
          min-width: $offsetVal * 6 + px;
          padding-right: calc($offsetVal / 2) + px;
          white-space: nowrap;
        }

        &:last-child {
          word-break: break-word;
        }
      }
    }
  }
</style>
