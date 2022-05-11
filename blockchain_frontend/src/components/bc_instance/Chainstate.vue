<template>
  <section id="chainstate">
    <p class="bcInstanceHeader">
      Chainstate - pool that shows only unspent transactions / outputs.
    </p>
    <div v-if="fetching">
      Fetching...
    </div>
    <el-table v-else-if="!fetching && tableData.length !== 0"
              :data="tableData"
              class="table"
    >
      <el-table-column type="expand">
        <template #default="props">
          <div class="outputsRepresentation" m="4" v-for="output in props.row.outputs" key="output.publicKeyHash">
            <p m="t-0 b-2"><span>Output ID:</span> <span>{{ output.outputID }}</span></p>
            <p m="t-0 b-2"><span>Value:</span> <span>{{ output.val }}</span></p>
            <p m="t-0 b-2"><span>Public Key Hash (latin1 decoded):</span> <span>{{ output.publicKeyHash }}</span></p>
          </div>
        </template>
      </el-table-column>
      <el-table-column label="Transaction ID" prop="txID"/>
      <el-table-column label="Outputs" prop="outputsCount" width="150px" />
    </el-table>
    <div v-else-if="tableData.length === 0">
      There is no chainstate
    </div>
  </section>
</template>

<script>
export default {
    data() {
        return {
            tableData: [],
            fetching: false,
        };
    },
    methods: {
        async getChainState() {
            this.fetching = true;
            await fetch("/api/get_chainstate", {
                method: "GET"
            })
                .then(response => response.json())
                .then(data => {
                    // console.log(data);
                    for (let txID in data) {
                        let transaction = data[txID];
                        let outputs = JSON.parse(transaction.serializedUnspentOutputs);
                        this.tableData.push({
                            txID: txID,
                            outputsCount: outputs.length,
                            outputs: outputs,
                        });
                    }
                    this.fetching = false;
                })
                .catch(err => {
                    console.log(err);
                    this.fetching = true;
                });
        }
    },
    mounted() {
        this.getChainState();
    }
};
</script>

<style lang="scss" scoped>
  #chainstate {
    display: flex;
    flex-direction: column;
    justify-content: flex-start;
    align-items: center;
    margin-top: $offsetVal + px;
  }
  .outputsRepresentation {
    padding: calc($offsetVal / 2) + px $offsetVal + px;
    margin-left: $offsetVal + px;
    border-bottom: 1px solid black;

    &:last-child {
      border-bottom: 0px solid black;
    }
  }
  p {
    display: flex;
    //margin-top: 15px;
    text-indent: 1em;
    //text-align: justify;

    @media screen and (min-width:0px) and (max-width:949px) {
      display: block;
      white-space: nowrap;
      overflow-x: scroll;
      overflow-y: hidden;
    }

    span {
      text-indent: initial;
      min-width: 90px;
      padding-right: 15px;
      word-break: break-word;
      margin-top: calc($offsetVal / 4) + px;

      &:first-child {
        width: $offsetVal * 12 + px;
        color: $brown;
        white-space: nowrap;
      }
      &:last-child {
        width: 100%;
      }
    }
  }
</style>