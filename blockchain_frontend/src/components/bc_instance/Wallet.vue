<template>
  <div class="wallet">
    <p><span>Address:</span> <span>{{address}}</span></p>
<!--    <p><span>{{address}}</span></p>-->
    <p><span>Private key:</span> <span><EyeIcon @click="$emit('showDialog', BigInt(privateKey))"/></span></p>
    <p><span>Public key:</span> <span><EyeIcon @click="$emit('showDialog', publicKey)"/></span></p>
    <p><span>Balance:</span> <span>{{balance}}</span></p>
  </div>
</template>

<script>
import EyeIcon from "@/assets/icons/iconmonstr-eye-thin.svg?component";
export default {
    props: {
        address: {
            type: String,
            default: "",
            required: true
        },
        privateKey: {
            type: Number,
            default: 0,
            required: true
        },
        publicKey: {
            type: String,
            default: "",
            required: true
        },
        balance: {
            type: Number,
            default: 0,
            required: true
        }
    },
    components: {
        EyeIcon
    }
};
</script>

<style lang="scss" scoped>
  .wallet {
    width: calc(100% - #{calc($offsetVal / 2) * 2 + px});
    height: calc(100% - #{calc($offsetVal / 2) * 2 + px});
    display: flex;
    flex-direction: column;
    justify-content: space-around;
    border: 1px solid black;
    border-radius: $offsetVal + px;
    padding: calc($offsetVal / 2) + px;

    svg {
      cursor: pointer;

      &:hover {
        opacity: 0.5;
      }
    }
  }
  div {
    display: flex;
    flex-direction: column;

    p {
      display: flex;
      margin-top: calc($offsetVal / 2) + px;
      text-indent: 1em;

      &:first-child {
        margin-top: 0;

        span {
          //color: $lightGreen;
        }
      }

      span {
        text-indent: initial;
        min-width: 90px;
        padding-right: calc($offsetVal / 2) + px;
        word-break: break-word;

        &:first-child {
          color: $brown;
          text-decoration: underline;
          text-decoration-color: $brown;
        }
      }
    }
  }
</style>