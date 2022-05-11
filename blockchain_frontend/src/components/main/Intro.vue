<template>
  <section id="intro">
    <div>
      <h1>
        Pocket BlockChain
      </h1>
      <ITSButton
          text="pocket-blockchain"
          src="https://github.com/J4stEu/blockchain-python"
          :isSrc="true"
          :buttonColor="'rgba(76, 212, 176, 0.2)'"
      >
        <template v-slot:beforeIcon>
          <GitHubIcon/>
        </template>
        <template v-slot:afterIcon>
          <ShareIcon/>
        </template>
      </ITSButton>
    </div>
    <p>
      Creation of blockchain system on Python for further integration in different projects
    </p>
    <p>
      Python, Flask, Postgres, Vue.js
    </p>
  </section>
</template>

<script>
import GitHubIcon from "@/assets/icons/iconmonstr-github-1.svg?component";
import ShareIcon from "@/assets/icons/iconmonstr-share-8.svg?component";
import ITSButton from "@/components/ui/ITSButton.vue";
export default {
    components: {
        ITSButton,
        GitHubIcon,
        ShareIcon
    },
};
</script>

<style lang="scss" scoped>
  #intro {
    padding: 0 $offsetVal + px;

    div {
      display: flex;
      justify-content: center;

      @media screen and (min-width:0px) and (max-width:635px) {
        flex-direction: column;
        align-items: center;
      }
    }
  }
  h1 {
    font-size: 2em;
    padding: calc($offsetVal / 4) + px;
    text-align: center;
    white-space:nowrap;
  }
  p {
    text-align: center;
    margin-top: $offsetVal + px;
  }
</style>