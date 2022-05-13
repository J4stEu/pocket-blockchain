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
      {{intro.Intro.text}}
    </p>
    <p>
      {{intro.Intro.stack}}
    </p>
  </section>
</template>

<script>
import GitHubIcon from "@/assets/icons/iconmonstr-github-1.svg?component";
import ShareIcon from "@/assets/icons/iconmonstr-share-8.svg?component";
import ITSButton from "@/components/ui/ITSButton.vue";
import Intro from "@/data/intro.json";
export default {
    components: {
        ITSButton,
        GitHubIcon,
        ShareIcon
    },
    data() {
        return {
            intro: Intro
        };
    }
};
</script>

<style lang="scss" scoped>
  #intro {
    padding: 0 $offsetVal + px;

    @media screen and (min-height: 0px) and (max-height: 799px) {
      margin-top: $offsetVal * 3 + px;
    }

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

    &:last-child {
      font-family: "Open Sans light", serif !important;
    }
  }
</style>