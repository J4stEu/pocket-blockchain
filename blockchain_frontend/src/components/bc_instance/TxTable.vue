<template>
  <section id="txPool">
    <el-table :data="tableData"
              class="table"
    >
      <el-table-column type="expand">
        <template #default="props">
          <div class="inputsRepresentation" m="4" v-for="input in props.row.inputs" key="input.id">
            <p m="t-0 b-2"><span>Input ID:</span> <span>{{ JSON.parse(input).id }}</span></p>
            <p m="t-0 b-2"><span>Output ID (reference):</span> <span>{{  JSON.parse(input).output }}</span></p>
            <p m="t-0 b-2"><span>Signature (latin1 decoded):</span> <span>{{JSON.parse(input).sig ? JSON.parse(input).sig : "None" }}</span></p>
            <p m="t-0 b-2"><span>Public key:</span> <span>{{  JSON.parse(input).publicKey }}</span></p>
          </div>
          <div class="outputsRepresentation" m="4" v-for="(output, index) in props.row.outputs" key="input.id">
            <p m="t-0 b-2"><span>Output ID:</span> <span>{{  index  }}</span></p>
            <p m="t-0 b-2"><span>Output value:</span> <span>{{  JSON.parse(output).val }}</span></p>
            <p m="t-0 b-2"><span>Public key hash (latin1 decoded):</span> <span>{{  JSON.parse(output).publicKeyHash }}</span></p>
          </div>
        </template>
      </el-table-column>
      <el-table-column label="Transaction ID" prop="id"/>
      <el-table-column label="Inputs (count)" prop="inputs.length"/>
      <el-table-column label="Outputs (count)" prop="outputs.length"/>
      <el-table-column label="Created" prop="created"/>
      <el-table-column label="Included in block" prop="included_in_block"/>
    </el-table>
  </section>
</template>

<script>
export default {
    props: {
        tableData: {
            type: Array,
            default() {
                return [];
            },
            required: true
        }
    }
};
</script>

<style lang="scss" scoped>
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