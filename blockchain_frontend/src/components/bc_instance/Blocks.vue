<template>
  <section id="blocks">
    <Dialog :show="showDialog" @show="showDialog = !showDialog">
      <TxTable :tableData="currentBlockTransactions"/>
    </Dialog>
    <p class="bcInstanceHeader">
      Block - abstraction that stores data. Every block is related to previous one.
    </p>
    <div class="blocksContainer" v-if="!this.fetching && Object.keys(this.blocks).length > 0">
      <Block
          v-for="block in blocks" :key="block.hash"
          :hash="block.hash"
          :nonce="block.block.nonce"
          :prevHash="block.block.prevHash"
          :transactions="block.block.transactions"
          @showDialog="showBlockTransactions"
      />
    </div>
    <div v-else-if="this.fetching">
      Fetching...
    </div>
    <div v-else-if="Object.keys(this.blocks).length === 0">
      There are no blocks...
    </div>
  </section>
</template>

<script>
import Block from "@/components/bc_instance/Block.vue";
import Dialog from "@/components/ui/Dialog.vue";
import TxTable from "@/components/bc_instance/TxTable.vue";
export default {
    components: {
        Block,
        Dialog,
        TxTable
    },
    data() {
        return {
            blocks: [],
            currentBlockTransactions: [],
            fetching: false,
            showDialog: false,
        };
    },
    methods: {
        async getBlocks() {
            this.fetching = true;
            await fetch("http://192.168.1.7:5000/get_blocks", {
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
</style>