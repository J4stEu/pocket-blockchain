<template>
  <section id="bcInstance" class="container is-max-desktop">
    <div>
      <transition appear name="bc-instance-menu">
        <Navigation
            :navItems="navItems"
            :selectedItem="selectedItem"
            @setCurrentItem="setCurrentItem"
        >
          <SquareIcon/>
        </Navigation>
      </transition>
    </div>
    <transition>
      <div class="bcInstanceContent" v-if="currentRouteName() === '/bc-instance/wallets'">
        <Wallets/>
      </div>
    </transition>
    <transition>
      <div class="bcInstanceContent" v-if="currentRouteName() === '/bc-instance/blocks'">
         <Blocks/>
      </div>
    </transition>
    <transition>
      <div class="bcInstanceContent" v-if="currentRouteName() === '/bc-instance/chainstate'">
        <Chainstate/>
      </div>
    </transition>
    <transition>
      <div class="bcInstanceContent" v-if="currentRouteName() === '/bc-instance/tx_pool'">
        <TxPool/>
      </div>
    </transition>
    <transition>
      <div class="bcInstanceContent" v-if="!paths.includes(currentRouteName())">
        <NoSuchBcInstance/>
      </div>
    </transition>
  </section>
</template>

<script>
import Navigation from "@/components/ui/Navigation.vue";
import SquareIcon from"@/assets/icons/iconmonstr-square-4.svg?component";
import Wallets from "@/components/bc_instance/Wallets.vue";
import Blocks from "@/components/bc_instance/Blocks.vue";
import Chainstate from "@/components/bc_instance/Chainstate.vue";
import TxPool from "@/components/bc_instance/TxPool.vue";
import NoSuchBcInstance from "@/components/bc_instance/NoSuchBcInstance.vue";
import {useNavigation} from "@/hooks/useNavigation";
import {ref} from "vue";
export default {
    components: {
        Navigation,
        SquareIcon,
        Wallets,
        Blocks,
        Chainstate,
        TxPool,
        NoSuchBcInstance
    },
    setup() {
        const {navItems, selectedItem, currentRouteName, setCurrentItem} = useNavigation([
            {id: 1, name: "Wallets", path: "/bc-instance/wallets"},
            {id: 2, name: "Blocks", path: "/bc-instance/blocks"},
            {id: 3, name: "Chainstate", path: "/bc-instance/chainstate"},
            {id: 4, name: "TX pool", path: "/bc-instance/tx_pool"}
        ],);
        const paths = ref(["/bc-instance/wallets", "/bc-instance/blocks", "/bc-instance/chainstate", "/bc-instance/tx_pool"]);
        return {
            navItems, selectedItem, currentRouteName, setCurrentItem, paths
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
  .bc-instance-menu-enter-from {
    transform: translateX(-#{$offsetVal + px});
  }
  .bc-instance-menu-enter-to {
    transform: translateX(0);
  }
  .bc-instance-menu-enter-active {
    transition: transform 0.5s ease-in-out;
  }
  #bcInstance {
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
  .bcInstanceContent {
    padding-bottom: $offsetVal + px;
  }
</style>