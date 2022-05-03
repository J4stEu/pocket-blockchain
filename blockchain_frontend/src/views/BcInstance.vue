<template>
  <section id="infoAndActions" class="container is-max-desktop">
    <div>
      <Navigation
          :navItems="navItems"
          :selectedItem="selectedItem"
          @setCurrentItem="setCurrentItem"
      >
        <SquareIcon/>
      </Navigation>
    </div>
    <div class="blockchainContent" v-if="currentRouteName() === '/bc-instance/wallets'">
      <Wallets/>
    </div>
    <div class="blockchainContent" v-if="currentRouteName() === '/bc-instance/blocks'">
      <Blocks/>
    </div>
    <div class="blockchainContent" v-if="currentRouteName() === '/bc-instance/chainstate'">
      <Chainstate/>
    </div>
    <div class="blockchainContent" v-if="currentRouteName() === '/bc-instance/tx_pool'">
      <TxPool/>
    </div>
  </section>
</template>

<script>
import Navigation from "@/components/ui/Navigation.vue";
import SquareIcon from"@/assets/icons/iconmonstr-square-4.svg?component";
import Wallets from "@/components/bc_instance/Wallets.vue";
import Blocks from "@/components/bc_instance/Blocks.vue";
import Chainstate from "@/components/bc_instance/Chainstate.vue";
import TxPool from "@/components/bc_instance/TxPool.vue";
import {useNavigation} from "@/hooks/useNavigation";
export default {
    components: {
        Navigation,
        SquareIcon,
        Wallets,
        Blocks,
        Chainstate,
        TxPool
    },
    setup() {
        const {navItems, selectedItem, currentRouteName, setCurrentItem} = useNavigation([
            {id: 1, name: "Wallets", path: "/bc-instance/wallets"},
            {id: 2, name: "Blocks", path: "/bc-instance/blocks"},
            {id: 3, name: "Chainstate", path: "/bc-instance/chainstate"},
            {id: 4, name: "TX pool", path: "/bc-instance/tx_pool"}
        ],);
        return {
            navItems, selectedItem, currentRouteName, setCurrentItem
        };
    },
    mounted() {
        this.$router.isReady().then(() => {
            this.navItems.forEach(item => {
                if (this.currentRouteName().includes(item.path)) {
                    this.selectedItem = item;
                }
            });
        });
    }
};
</script>

<style lang="scss" scoped>
  #infoAndActions {
    display: flex;
    flex-direction: column;
    justify-content: flex-start;
    height: 100%;
    padding: 0 $offsetVal + px;
    margin-top: $offsetVal * 2 + px;

    div:first-child {
      display: flex;
      align-items: center;

      h1 {
        font-size: 2em;
      }
    }
  }
  .blockchainContent {
    padding-bottom: $offsetVal + px;
  }
</style>