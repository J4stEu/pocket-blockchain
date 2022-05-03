<template>
  <div class="wallet">
    <p><span>Address:</span> <span>{{address}}</span></p>
    <p><span>Private key:</span> <span>{{privateKey}}</span></p>
    <p><span>Public key:</span> <span>{{publicKey}}</span></p>
    <p><span>Balance:</span> <span>{{balance}}</span></p>
  </div>
</template>

<script>
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
    }
};
</script>

<style lang="scss" scoped>
  .wallet {
    width: calc(100% - #{calc($offsetVal / 4) * 2 + px});
    height: calc(100% - #{calc($offsetVal / 4) * 2 + px});
    display: flex;
    flex-direction: column;
    justify-content: space-around;
    border: 1px solid black;
    padding: calc($offsetVal / 4) + px;
  }
  div {
    display: flex;
    flex-direction: column;

    p {
      display: flex;
      margin-top: calc($offsetVal / 2) + px;
      text-indent: 1em;
      //text-align: justify;

      span {
        text-indent: initial;
        min-width: 90px;
        padding-right: calc($offsetVal / 2) + px;
        word-break: break-word;

        &:first-child {
          color: $brown;
        }
      }
    }
  }
</style>