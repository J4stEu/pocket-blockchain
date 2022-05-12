<template>
  <div
      id="bio"
      class="
        container
        is-max-desktop
    "
  >
<!--    <h1>{{ title }}</h1>-->
    <p class="bcInstanceHeader">
      System Info
    </p>
    <div>
      <p
          v-for="(option, optionName) in options"
          :key="optionName"
      >
        <strong>{{ option.option }}:</strong>
        <span>{{ option.parameter }}.</span>
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
  #bio {
    margin: 0;
    margin-top: $offsetVal + px;
    //padding: 0px $offsetVal + px;
    color: black;
    display: flex;
    justify-content: flex-start;
    align-items: center;
  }
  h1 {
    color: black;
    font-weight: bold;
    border-bottom: 2px solid $lightGreen;
    display: inline;
    width: min-content;
  }
  div {
    display: flex;
    flex-direction: column;

    p {
      display: flex;
      margin-top: calc($offsetVal / 2) + px;
      //text-indent: 1em;
      text-align: justify;

      strong {
        //font-family: "Open Sans bold", serif;
        color: $brown;
        text-decoration: underline;
        min-width: $offsetVal * 8 + px;
        padding-right: calc($offsetVal / 2) + px;
        white-space: nowrap;

        @media screen and (min-width: 0px) and (max-width: 420px) {
          min-width: $offsetVal * 5 + px;
        }
        @media screen and (min-width: 0px) and (max-width: 330px) {
          min-width: $offsetVal * 2 + px;
        }
      }

    }
    span {
      text-indent: initial;
    }
  }
</style>
