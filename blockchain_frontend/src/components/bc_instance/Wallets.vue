<template>
  <section id="wallets">
    <p class="bcInstanceHeader">
      Wallet - a pair of private and public keys.
    </p>
    <div class="walletsContainer" v-if="!this.fetching && Object.keys(this.wallets).length > 0">
      <Wallet
          v-for="(value, key) in wallets" :key="key"
          :address="key"
          :privateKey="value.wallet.privateKey"
          :publicKey="value.wallet.publicKey"
          :balance="value.balance"
      />
    </div>
    <div v-else-if="this.fetching">
      Fetching...
    </div>
    <div v-else-if="Object.keys(this.wallets).length === 0">
      There are no wallets...
    </div>
  </section>
</template>

<script>
import Wallet from "@/components/bc_instance/Wallet.vue";
export default {
    components: {
        Wallet
    },
    data() {
        return {
            wallets: {},
            fetching: false
        };
    },
    methods: {
        async getWallets() {
            this.fetching = true;
            await fetch("http://192.168.1.7:5000/get_wallets", {
                method: "GET",
                mode: "cors",
                headers: {
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                    "Access-Control-Allow-Origin": "*"
                }
            })
                .then(response => response.json())
                .then(data => {
                    // console.log(data);
                    this.wallets = data;
                    this.fetching = false;
                })
                .catch(err => {
                    console.log(err);
                    this.fetching = true;
                });
        }
    },
    mounted() {
        this.getWallets();
    }
};
</script>

<style lang="scss" scoped>
  #wallets {
    display: flex;
    flex-direction: column;
    justify-content: flex-start;
    align-items: center;
    margin-top: $offsetVal + px;
  }
  .walletsContainer {
    width: 100%;
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
    gap: $offsetVal + px;
    padding: 0 $offsetVal + px;
    justify-items: flex-start;
    align-items: center;

    //@media screen and (min-width:0px) and (max-width:889px) {
    //  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
    //}
  }
</style>