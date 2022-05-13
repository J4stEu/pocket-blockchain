<template>
  <section id="blocks">
    <Dialog :show="showMineDialog" @show="showMineDialog = !showMineDialog">
      <div class="interactForm">
        <span>Address: </span>
<!--        <input type="text" name="address" placeholder="Address" v-model="address">-->
        <select v-model="address">
          <option v-for="address in addresses"
                  key="address"
                  :value="address">
            {{address}}
          </option>
        </select>
        <span>Transactions amount: </span>
        <input type="number" min="1" name="amount" placeholder="Transactions amount" v-model="txAmount">
        <div @click="mineBlock">
          <ITSButton text="Mine"
                     :buttonColor="'rgba(76, 212, 176, 0.2)'">
          </ITSButton>
        </div>
      </div>
    </Dialog>
    <Dialog :show="showDialog" @show="showDialog = !showDialog">
      <TxTable :tableData="currentBlockTransactions"/>
    </Dialog>
    <h1 class="infoHeader">
      Block - abstraction that stores data. Every block is related to previous one.
    </h1>
    <div class="bcInstanceAction" @click="showMineDialog = !showMineDialog">
      <ITSButton text="Mine new block"
                 :buttonColor="'rgba(76, 212, 176, 0.2)'">
      </ITSButton>
    </div>
    <div class="blocksContainer" v-if="this.blocks.length > 0">
      <Block
          v-for="block in blocks" :key="block.hash"
          :hash="block.hash"
          :nonce="block.block.nonce"
          :prevHash="block.block.prevHash"
          :transactions="block.block.transactions"
          @showDialog="showBlockTransactions"
      />
    </div>
    <div v-else-if="this.blocks.length === 0 && !this.fetching">
      There are no blocks...
    </div>
    <div v-if="this.fetching">
      Fetching...
    </div>
  </section>
</template>

<script>
import Block from "@/components/bc_instance/Block.vue";
import Dialog from "@/components/ui/Dialog.vue";
import TxTable from "@/components/bc_instance/TxTable.vue";
import {useNotificationStore} from "@/hooks/useNotificationStore";
import {useWalletsStore} from "@/hooks/useWalletsStore";
import {ref} from "vue";
export default {
    components: {
        Block,
        Dialog,
        TxTable
    },
    setup() {
        const { notification } = useNotificationStore();
        const { walletsStore, addresses } = useWalletsStore();
        const  blocks = ref([]);
        const  currentBlockTransactions = ref([]);
        const  fetching = ref(false);
        const  showDialog = ref(false);
        const  showMineDialog = ref(false);
        const  address = ref("");
        const  txAmount = ref(1);
        return {
            notification,
            walletsStore,
            addresses,
            blocks,
            currentBlockTransactions,
            fetching,
            showDialog,
            showMineDialog,
            address,
            txAmount
        };
    },
    methods: {
        async getBlocks() {
            this.fetching = true;
            await fetch("/api/get_blocks", {
                method: "GET",
            })
                .then(response => response.json())
                .then(data => {
                    // console.log(data);
                    this.blocks = [];
                    data.forEach((value) => {
                        // console.log(value);
                        this.blocks.push(
                            {
                                ...value,
                                block: JSON.parse(value.serializedBlock)
                            }
                        );
                    });
                })
                .finally(() => {
                    this.fetching = false;
                })
                .catch(err => {
                    console.log(err);
                    this.fetching = false;
                });
        },
        async mineBlock() {
            if (this.fetching) {
                return;
            }
            if (!this.validateBlocksInteractForm()) {
                this.notification.notify("Invalid request parameters...", false);
                return;
            }
            this.fetching = true;
            await fetch("/api/mine_block", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    address: this.address,
                    txAmount: parseInt(this.txAmount)
                })
            })
                .then(response => response.json())
                .then(data => {
                    // console.log(data);
                    if (data.error !== null) {
                        console.log(data.error);
                        this.notification.notify(data.error, false);
                        return;
                    }
                    this.notification.notify("Mine new block: success", true);
                })
                .finally(() => {
                    this.fetching = false;
                    this.address = "";
                    this.txAmount = 1;
                    this.showMineDialog = false;
                    this.getBlocks();
                    this.walletsStore.getWallets();
                })
                .catch(err => {
                    console.log(err);
                    this.notification.notify("Mine new block: error", false);
                    this.fetching = true;
                });
        },
        showBlockTransactions(serializedTransactions) {
            let transactions = [];
            serializedTransactions.forEach(transaction => {
                transactions.push(JSON.parse(transaction));
            });
            this.currentBlockTransactions = transactions;
            this.showDialog = !this.showDialog;
        },
        validateBlocksInteractForm() {
            if (typeof this.address !== "string") {
                return false;
            }
            if (typeof this.txAmount !== "number") {
                return false;
            }
            return !(this.address === "" || this.txAmount < 1);
        }
    },
    mounted() {
        this.getBlocks();
        if (this.addresses.length === 0 ) {
            this.walletsStore.getWallets();
        }
    }
};
</script>

<style lang="scss" scoped>
  #blocks {
    display: flex;
    flex-direction: column;
    justify-content: flex-start;
    align-items: center;
    margin-top: $offsetVal + px;
  }
  .blocksContainer {
    width: 100%;
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
    gap: $offsetVal + px;
    padding: 0 $offsetVal + px;
    justify-items: flex-start;
    align-items: center;

  }
</style>