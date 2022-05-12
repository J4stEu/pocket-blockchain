<template>
  <section id="blocks">
    <Dialog :show="showMineDialog" @show="showMineDialog = !showMineDialog">
      <div class="mineForm">
        <span>Address: </span>
        <input type="text" name="address" placeholder="Address" v-model="address">
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
    <p class="bcInstanceHeader">
      Block - abstraction that stores data. Every block is related to previous one.
    </p>
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
    <div v-else-if="!this.fetching && this.blocks.length === 0">
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
export default {
    components: {
        Block,
        Dialog,
        TxTable
    },
    setup() {
        const {notification} = useNotificationStore();
        return {
            notification
        };
    },
    data() {
        return {
            blocks: [],
            currentBlockTransactions: [],
            fetching: false,
            showDialog: false,
            showMineDialog: false,
            address: "",
            txAmount: 1,
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
                    this.fetching = false;
                })
                .catch(err => {
                    console.log(err);
                    this.fetching = true;
                });
        },
        async mineBlock() {
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
                    console.log(data);
                    if (data.error !== null) {
                        console.log(data.error);
                        this.notification.notify(data.error, false);
                        return;
                    }
                    this.notification.notify("Success", true);
                })
                .finally(() => {
                    this.fetching = false;
                    this.address = "";
                    this.txAmount = 1;
                    this.showMineDialog = false;
                    this.getBlocks();
                })
                .catch(err => {
                    console.log(err);
                    this.notification.notify("Error", false);
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
        }
    },
    mounted() {
        this.getBlocks();
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

    //@media screen and (min-width:0px) and (max-width:889px) {
    //  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
    //}
  }
  .mineForm {
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    padding: $offsetVal+ px;

    input {
      margin: $offsetVal + px;
      width: 300px;
      min-width: calc(300px - #{$offsetVal * 4 + px});
      height: 25px;
      border: 1px solid black;
      border-radius: calc($offsetVal / 4) + px;
      padding-left: calc($offsetVal / 4) + px;
    }
  }
</style>