<template>
  <transition appear>
    <div class="block">
      <p><span>Hash:</span> <span>{{hash}}</span></p>
      <p><span>Previous hash:</span> <span>{{prevHash.length > 0 ? prevHash : "None" }}</span></p>
      <p><span>Nonce:</span> <span>{{nonce}}</span></p>
      <p><span>Transactions:</span> <span class="more"><EyeIcon @click="$emit('showDialog', transactions)"/></span></p>
    </div>
  </transition>
</template>

<script>
import EyeIcon from "@/assets/icons/iconmonstr-eye-thin.svg?component";
export default {
    components: {
        EyeIcon,
    },
    props: {
        hash: {
            type: String,
            default: "",
            required: true
        },
        prevHash: {
            type: String,
            default: "",
            required: true
        },
        nonce: {
            type: Number,
            default: 0,
            required: true
        },
        transactions: {
            type: Array,
            default() {
                return [];
            },
            required: true
        }
    }
};
</script>

<style lang="scss" scoped>
  .block {
    width: calc(100% - #{calc($offsetVal / 2) * 2 + px});
    height: calc(100% - #{calc($offsetVal / 2) * 2 + px});
    display: flex;
    flex-direction: column;
    justify-content: space-around;
    border: 1px solid black;
    padding: calc($offsetVal / 2) + px;
  }
  div {
    display: flex;
    flex-direction: column;

    p {
      display: flex;
      //margin-top: 15px;
      text-indent: 1em;
      //text-align: justify;

      span {
        text-indent: initial;
        min-width: 90px;
        padding-right: 15px;
        word-break: break-word;
        margin-top: calc($offsetVal / 4) + px;

        svg {
          cursor: pointer;
          transition: opacity 0.2s ease-in-out;

          &:hover {
            opacity: 0.5;
          }
        }

        &:first-child {
          width: $offsetVal * 8 + px;
          color: $brown;
          text-decoration: underline;
          white-space: nowrap;
        }
        &:last-child {
          width: 100%;
        }
      }
    }
  }
</style>