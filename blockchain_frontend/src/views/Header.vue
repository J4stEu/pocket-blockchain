<template>
  <header id="header">
    <Navigation
        :navItems="navItems"
        :selectedItem="selectedItem"
        @setCurrentItem="setCurrentItem"
    >
      <ArrowRightIcon/>
    </Navigation>
  </header>
</template>

<script>
import Navigation from "@/components/ui/Navigation.vue";
import ArrowRightIcon from "@/assets/icons/iconmonstr-arrow-right-lined.svg?component";
import {useNavigation} from "@/hooks/useNavigation";
export default {
    components: {
        Navigation,
        ArrowRightIcon
    },
    setup() {
        const {navItems, selectedItem, currentRouteName, setCurrentItem} = useNavigation([
            {id: 1, name: "Home", path: "/"},
            {id: 2, name: "Info", path: "/info"},
            {id: 3, name: "BC Instance", path: "/bc-instance/wallets"},
        ]);
        return {
            navItems, selectedItem, currentRouteName, setCurrentItem
        };
    },
    mounted() {
        this.$router.isReady().then(() => {
            // console.log(this.currentRouteName());
            if (this.currentRouteName() === "/") {
                this.selectedItem = this.navItems[0];
            }
            if (this.currentRouteName() === "/info") {
                this.selectedItem = this.navItems[1];
            }
            if (this.currentRouteName() === "/bc-instance/wallets" || this.currentRouteName().includes("/bc-instance")) {
                this.selectedItem = this.navItems[2];
            }
        });
    }
};
</script>

<style lang="scss" scoped>
  #header {
    z-index: 2;
    position: fixed;
    top: 0;
    width: 100%;
    padding: calc($offsetVal / 2) + px 0;
    background: rgba(255, 255, 255, 0.9);

    @media screen and (min-width: 0px) and (max-width: 1022px) {
      padding: calc($offsetVal / 2) + px $offsetVal + px;
    }
  }
</style>