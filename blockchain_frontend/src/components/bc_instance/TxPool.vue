<template>
  <section id="txPool">
    <Dialog :show="showDialog" @show="showDialog = !showDialog">
      <div class="interactForm">
        <span>From: </span>
<!--        <input type="text" name="from" placeholder="from" v-model="from">-->
        <select v-model="from">
          <option v-for="address in addresses"
                  key="address"
                  :value="address">
            {{address}}
          </option>
        </select>
        <span>To: </span>
<!--        <input type="text" name="to" placeholder="to" v-model="to">-->
        <select v-model="to">
          <option v-for="address in addresses"
                  key="address"
                  :value="address">
            {{address}}
          </option>
        </select>
        <span>Amount: </span>
        <input type="number" min="1" name="amount" placeholder="amount" v-model="amount">
        <div @click="send">
          <ITSButton text="Send"
                     :buttonColor="'rgba(76, 212, 176, 0.2)'">
          </ITSButton>
        </div>
      </div>
    </Dialog>
    <h1 class="infoHeader">
      Transactions pool - pool of transactions that are awaiting confirmation (storing in new block).
    </h1>
    <div class="bcInstanceAction" @click="showDialog = !showDialog">
      <ITSButton text="Send"
                 :buttonColor="'rgba(76, 212, 176, 0.2)'">
      </ITSButton>
    </div>
    <el-table v-if="tableData.length > 0"
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
          <div v-else class="errorRepresentation">
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
    <div v-else-if="!fetching && tableData.length === 0">
      There is no transaction pool
    </div>
    <div v-if="fetching">
      Fetching...
    </div>
  </section>
</template>

<script>
import {useNotificationStore} from "@/hooks/useNotificationStore";
import Dialog from "@/components/ui/Dialog.vue";
import ITSButton from "@/components/ui/ITSButton.vue";
import {useWalletsStore} from "@/hooks/useWalletsStore";
import {ref} from "vue";
export default {
    components: {
        Dialog,
        ITSButton
    },
    setup() {
        const {notification} = useNotificationStore();
        const { walletsStore, addresses } = useWalletsStore();
        const tableData = ref([]);
        const fetching = ref(false);
        const showDialog =  ref(false);
        const from = ref("");
        const to = ref("");
        const amount = ref(1);
        return {
            notification,
            walletsStore,
            addresses,
            tableData,
            fetching,
            showDialog,
            from,
            to,
            amount
        };
    },
    methods: {
        async getTxPool() {
            this.fetching = true;
            await fetch("/api/get_pool", {
                method: "GET"
            })
                .then(response => response.json())
                .then(data => {
                    // console.log(data);
                    this.tableData = [];
                    data.forEach((value) => {
                        // console.log(value);
                        this.tableData.push(
                            {
                                ...value,
                                deserializedTransaction: JSON.parse(value.serializedTransaction)
                            }
                        );
                    });
                })
                .finally(() => {
                    this.fetching = false;
                })
                .catch(err => {
                    console.log(err);
                    this.fetching = true;
                });
        },
        async send() {
            if (this.fetching) {
                return;
            }
            if (!this.validateTxPoolInteractForm()) {
                this.notification.notify("Invalid request parameters...", false);
                return;
            }
            this.fetching = true;
            await fetch("/api/send", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    from: this.from,
                    to: this.to,
                    amount: parseInt(this.amount)
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
                    this.notification.notify("Send: success", true);
                })
                .finally(() => {
                    this.fetching = false;
                    this. from = "";
                    this.to = "";
                    this.amount = 1;
                    this.showDialog = false;
                    this.getTxPool();
                })
                .catch(err => {
                    console.log(err);
                    this.notification.notify("Send: failed", false);
                    this.fetching = true;
                });
        },
        validateTxPoolInteractForm() {
            if (typeof this.to !== "string") {
                return false;
            }
            if (typeof this.from !== "string") {
                return false;
            }
            if (typeof this.amount !== "number") {
                return false;
            }
            return !(this.to === "" || this.from === "" || this.txAmount < 1);
        }
    },
    mounted() {
        this.getTxPool();
        if (this.addresses.length === 0 ) {
            this.walletsStore.getWallets();
        }
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
  .inputsRepresentation, .outputsRepresentation, .errorRepresentation {
    padding: calc($offsetVal / 2) + px $offsetVal + px;
    margin-left: $offsetVal + px;
    border-bottom: 1px solid black;

    &:last-child {
      border-bottom: 0px solid black;
    }
  }
  p {
    display: flex;
    text-indent: 1em;

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