<template>
  <section id="wallets">
    <Dialog :show="showDialog" @show="showDialog = !showDialog">
      <div class="walletInfo container is-max-desktop">
        <span>{{ currentWalletInfo }}</span>
        <div>
          <ITSButton text="Copy"
                     :buttonColor="'rgba(76, 212, 176, 0.2)'"
                     @click="writeDataToClipboard(currentWalletInfo)">
            <template v-slot:beforeIcon>
              <CopyTpClipboard/>
            </template>
          </ITSButton>
        </div>
      </div>
    </Dialog>
    <p class="bcInstanceHeader">
      Wallet - a pair of private and public keys.
    </p>
    <div class="wallets_action" @click="newWallet">
      <ITSButton text="Create new wallet"
                 :buttonColor="'rgba(76, 212, 176, 0.2)'">
      </ITSButton>
    </div>
    <div class="walletsContainer" v-if="this.wallets.length > 0">
      <Wallet
          v-for="wallet in wallets" :key="wallet.address"
          :address="wallet.address"
          :privateKey="wallet.wallet.privateKey"
          :publicKey="wallet.wallet.publicKey"
          :balance="wallet.balance"
          @showDialog="showWalletInfo"
      />
    </div>
    <div v-else>
      There are no wallets...
    </div>
    <div v-if="this.fetching">
      Fetching...
    </div>
  </section>
</template>

<script>
import Wallet from "@/components/bc_instance/Wallet.vue";
import Dialog from "@/components/ui/Dialog.vue";
import ITSButton from "@/components/ui/ITSButton.vue";
import CopyTpClipboard from "@/assets/icons/iconmonstr-copy-thin.svg?component";
import {useNotificationStore} from "@/hooks/useNotificationStore";
export default {
    components: {
        Wallet,
        Dialog,
        ITSButton,
        CopyTpClipboard
    },
    setup() {
        const {notification, text, show, success} = useNotificationStore();
        return {
            notification,
            text,
            show,
            success
        };
    },
    data() {
        return {
            wallets: [],
            currentWalletInfo: "",
            fetching: false,
            showDialog: false,
        };
    },
    methods: {
        async getWallets() {
            this.fetching = true;
            await fetch("/api/get_wallets", {
                method: "GET"
            })
                .then(response => response.json())
                .then(data => {
                    // console.log(data);
                    if (data.error !== null) {
                        console.log(data.err);
                        return;
                    }
                    this.wallets = data.data;
                })
                .finally(() => {
                    this.fetching = false;
                })
                .catch(err => {
                    console.log(err);
                    this.fetching = false;
                });
        },
        async writeDataToClipboard(text){
            await navigator.clipboard.writeText(text);
        },
        async newWallet() {
            this.fetching = true;
            await fetch("/api/new_wallet", {
                method: "POST"
            })
                .then(response => response.json())
                .then(data => {
                    console.log(data);
                    if (data.error !== null) {
                        // console.log(data.error);
                        this.notification.notify(data.error, false);
                        return;
                    }
                    this.notification.notify("Success", true);
                })
                .finally(() => {
                    this.fetching = false;
                    this.getWallets();
                })
                .catch(err => {
                    console.log(err);
                    this.notification.notify("Error", false);
                });
        },
        showWalletInfo(currentWalletInfo) {
            this.currentWalletInfo = currentWalletInfo;
            this.showDialog = !this.showDialog;
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
  .wallets_action {
    margin-bottom: $offsetVal + px;
  }
  .walletsContainer {
    width: 100%;
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
    gap: $offsetVal + px;
    padding: 0 $offsetVal + px;
    justify-items: flex-start;
    align-items: center;

  }
  .walletInfo {
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    padding: $offsetVal + px;

    span {
      min-width: calc(300px - #{$offsetVal * 4 + px});
      word-break: break-word;
      margin: $offsetVal + px;
      text-align: justify;
    }
  }
</style>