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
              <CopyToClipboard/>
            </template>
          </ITSButton>
        </div>
      </div>
    </Dialog>
    <h1 class="infoHeader">
      Wallet - a pair of private and public keys.
    </h1>
    <div class="bcInstanceAction" @click="newWallet">
      <ITSButton text="Create new wallet"
                 :buttonColor="'rgba(76, 212, 176, 0.2)'">
      </ITSButton>
    </div>
    <div class="walletsContainer" v-if="wallets.length > 0">
      <Wallet
          v-for="wallet in wallets" :key="wallet.address"
          :address="wallet.address"
          :privateKey="wallet.wallet.privateKey"
          :publicKey="wallet.wallet.publicKey"
          :balance="wallet.balance"
          @showDialog="showWalletInfo"
      />
    </div>
    <div v-else-if="wallets.length === 0 && !fetching">
      There are no wallets...
    </div>
    <div v-if="fetching">
      Fetching...
    </div>
  </section>
</template>

<script>
import Wallet from "@/components/bc_instance/Wallet.vue";
import Dialog from "@/components/ui/Dialog.vue";
import ITSButton from "@/components/ui/ITSButton.vue";
import CopyToClipboard from "@/assets/icons/iconmonstr-copy-thin.svg?component";
import {useNotificationStore} from "@/hooks/useNotificationStore";
import {useWalletsStore} from "@/hooks/useWalletsStore";
import {ref} from "vue";
export default {
    components: {
        Wallet,
        Dialog,
        ITSButton,
        CopyToClipboard
    },
    setup() {
        const { notification } = useNotificationStore();
        const { walletsStore, wallets } = useWalletsStore();
        const currentWalletInfo = ref("");
        const fetching = ref(false);
        const showDialog = ref(false);
        return {
            notification,
            walletsStore,
            wallets,
            currentWalletInfo,
            fetching,
            showDialog
        };
    },
    methods: {
        async newWallet() {
            if (this.fetching) {
                return;
            }
            this.fetching = true;
            await fetch("/api/new_wallet", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
            })
                .then(response => response.json())
                .then(data => {
                    // console.log(data);
                    if (data.error !== null) {
                        console.log(data.error);
                        this.notification.notify(data.error, false);
                        return;
                    }
                    this.notification.notify("Create new wallet: success", true);
                })
                .finally(() => {
                    this.fetching = false;
                    this.walletsStore.getWallets();
                })
                .catch(err => {
                    console.log(err);
                    this.notification.notify("Create new wallet: failed", false);
                });
        },
        showWalletInfo(currentWalletInfo) {
            this.currentWalletInfo = currentWalletInfo;
            this.showDialog = !this.showDialog;
        },
        async writeDataToClipboard(text){
            await navigator.clipboard.writeText(text);
        },
    },
    mounted() {
        if (this.wallets.length === 0) {
            this.walletsStore.getWallets();
        }
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