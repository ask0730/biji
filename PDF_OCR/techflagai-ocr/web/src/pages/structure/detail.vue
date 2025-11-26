<template>
  <div class="page-layout">
    
    <a-card class="card-list">
    
      <a-layout style="height: calc(100vh - 150px);">
        <a-layout-sider width="50%" style=" background: #fff;">
          <luckysheet ref="luckysheetRef"
                    v-if="form.output_excel"
                    :allow-edit="false"
                    :config="config"
                    :save_flag="false"
                    style="height: calc(100vh - 160px);"
                    @cellMousedownBefore="cellMousedownBefore"
                    :name="form.output_excel">
        </luckysheet>
        </a-layout-sider>
        <a-layout-content style=" background: #fff; min-height: 400px;">
          <vue-json-editor 
        v-model="form.json_content"  lang="zh"
        @textSelectionChange="textSelectionChange" style="height: calc(100vh - 160px);" />
        <a-button size="small" type="danger"  :loading="loading"  style="position: absolute;top: 5px;right: 150px" @click="submitForm">保存</a-button>
      
        </a-layout-content>
      </a-layout>

  </a-card>

  </div>

  
</template>

<script>
import vueJsonEditor  from 'vue-json-editor';
import Luckysheet from "@/components/Luckysheet/index.vue";
import { find,save_or_update} from '@/services/structure'
export default {
  name: 'Structure',
  components: {
    Luckysheet,
    vueJsonEditor
  },
  data () {
    return {
      form: {
        id: undefined,
        output_excel: '',
        json_content: {}
      },
      config: {
        showinfobar: false,
        showtoolbar: false, // 是否显示工具栏
        showsheetbar: false, // 是否显示底部sheet页按钮
        showstatisticBar: false, // 是否显示底部计数栏
        sheetBottomConfig: false, // sheet页下方的添加行按钮和回到顶部按钮配置
        showsheetbarConfig: {
          add: false, //新增sheet
          menu: false, //sheet管理菜单
          sheet: false, //sheet页显示
        }
        
      },
      json: {
        msg: 'demo of jsoneditor'
      },
      loading: false,
    }
  },
  
  mounted() {
    const id = this.$route.query.id
    if (id) {
      this.fetchData(id)
    }
  },
  methods: {
    async fetchData(id) {
      try {
        const res = await find({id})
        if (res.data.code === 200) {
          this.form = res.data.data
        }
      } catch (error) {
        this.$message.error('获取详情失败')
      }
    },
    textSelectionChange (editor, start, end, text)  {
      console.log('textSelectionChange', editor, start, end, text)
      if (text.startsWith ('#{') && text.endsWith('}')){
        var val = text.replace('#{','').replace('}','')
        var item = val.split(',')
        console.log(item)
      }
    },
    onJsonSave(){ // 点击保存触发
    },
    cellMousedownBefore (cell, position) {
      const res = [position.r, position.c].join(',')

      const textarea = document.createElement('textarea');
      textarea.value = `"#{${res}}"`;
      textarea.style.position = 'absolute';
      textarea.style.opacity = '0';
      document.body.appendChild(textarea);
      textarea.select();
      document.execCommand('copy');
      document.body.removeChild(textarea);
      this.$message.success('复制成功')
    },
    submitForm () {
      this.loading = true;
      console.log(this.form)
      this.form={
        id: this.form.id,
        name: this.form.name,
        output_excel: this.form.output_excel,
        json_content: this.form.json_content
      }
      save_or_update(this.form).then(res => {
        if (res.data.code === 200) {
          this.$message.success('保存成功')
          this.getData()
        } else {
          this.$message.error(res.data.msg)
        }
      })
      this.loading = false;
      
    },
    
  },
  
  
}
</script>

<style lang="less" scoped>
 .card-list{
    margin-top: 24px;
  }
  
  ::v-deep .jsoneditor-vue {
    height: calc(100vh - 160px) !important;
  }
</style>
