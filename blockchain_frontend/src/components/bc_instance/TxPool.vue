<template>
  <section id="txPool">
    <p class="bcInstanceHeader">
      Transactions pool - pool of transactions that are awaiting confirmation (storing in new block).
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
          <div v-if="!props.row.error">
            <div class="inputsRepresentation" m="4" v-for="input in props.row.deserializedTransaction.inputs" key="input.id">
              <p m="t-0 b-2"><span>Input ID:</span> <span>{{ JSON.parse(input).id }}</span></p>
              <p m="t-0 b-2"><span>Output ID (reference):</span> <span>{{  JSON.parse(input).output }}</span></p>
              <p m="t-0 b-2"><span>Signature (latin1 decoded):</span> <span>{{  JSON.parse(input).sig }}</span></p>
              <p m="t-0 b-2"><span>Public key:</span> <span>{{  JSON.parse(input).publicKey }}</span></p>
            </div>
            <div class="outputsRepresentation" m="4" v-for="(output, index) in props.row.deserializedTransaction.outputs" key="input.id">
              <p m="t-0 b-2"><span>Output ID:</span> <span>{{  index  }}</span></p>
              <p m="t-0 b-2"><span>Output value:</span> <span>{{  JSON.parse(output).val }}</span></p>
              <p m="t-0 b-2"><span>Public key hash (latin1 decoded):</span> <span>{{  JSON.parse(output).publicKeyHash }}</span></p>
            </div>
          </div>
          <div v-else>
            <p m="t-0 b-2"><span>TX error:</span> <span>{{  props.row.errorText  }}</span></p>
          </div>
        </template>
      </el-table-column>
      <el-table-column label="Transaction ID" prop="txID"/>
      <el-table-column label="Created" prop="deserializedTransaction.created"/>
      <el-table-column label="From address" prop="fromAddr"/>
      <el-table-column label="To address" prop="toAddr"/>
      <el-table-column label="Amount" prop="amount" width="150px"/>
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
            await fetch("http://192.168.1.7:5000/get_pool", {
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
                        this.tableData.push(
                            {
                                ...value,
                                deserializedTransaction: JSON.parse(value.serializedTransaction)
                            }
                        );
                    });
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
  #txPool {
    display: flex;
    flex-direction: column;
    justify-content: flex-start;
    align-items: center;
    margin-top: $offsetVal + px;
  }
  .inputsRepresentation, .outputsRepresentation {
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