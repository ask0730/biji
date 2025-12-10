<template>
  <div class="page-layout">
    <a-row style=" margin-top: 24px; ">
      <a-col :span="5" style="display: flex; align-items: center; justify-content: space-between;">
        <div style="display: flex; align-items: center;">
          <span class="label" style="margin-right: 8px;">识别模型</span>
          <a-select v-model="model_id" size="small" style="width:150px">
            <a-select-option v-for="model in modelList" :key="model.id" :value="model.id">
              {{ model.name }}
            </a-select-option>
          </a-select>
          <a-button type="primary"
                   size="small"
                   style=" margin-left: 10px; "
                   @click="recognition_click()"
        >
          重新识别
        </a-button>
        </div>
        
      </a-col>
      <a-col :span="5" style="display: flex; align-items: center; justify-content: space-between;">
        <div style="display: flex; align-items: center;">
          <span class="label" style="margin-right: 8px;">识别结构</span>
          <a-select v-model="structure_id" size="small" style="width:150px">
            <a-select-option v-for="structure in structureList" :key="structure.id" :value="structure.id">
              {{ structure.name }}
            </a-select-option>
          </a-select>
          <span>
           <a-tooltip title="
         识别结构预先设置完成，与识别的Excel对应，识别结果与识别结构一一对应。
          您可以在「识别结构」中添加、修改、删除识别结构。识别结果会【提交】同步到其他系统中。
        ">
          <a-icon type="info-circle" style="margin-left: 8px;" />
        </a-tooltip></span>
        </div>
        
      </a-col>
      <a-col :span="14" style="justify-content: flex-end;text-align: right;padding-right: 170px;">
        <span>
            注意：<a-tooltip title="
          1. 左侧的 SVG 图层可能与 Excel 中的单元格不完全对应。
          2. 您可以通过操作（右击） Excel 来进行调整，通常这种不一致是由于 Excel 中多出了一些行，删除一些行后调试即可。
          3. 调试的方式是点击左侧 SVG 图层格子能够准确定位到左侧 Excel 上的单元格。
          4. 如果已经设置了数据结构，建议不要调整 Excel，以免造成数据同步到其他系统时无法根据规则提取。
        ">
          <a-icon type="info-circle" style="margin-left: 8px;" />
        </a-tooltip></span>
      </a-col>
      
    </a-row>
    <a-card class="card-list">
    
      <a-layout style="height: calc(100vh - 150px);">
        <a-layout-sider width="50%" style=" background: #fff;">
          <inc-img v-if="form.upload_image && form.output_json && Object.keys(form.output_json).length > 0"
                 :style="{height: span == 24 ? '250px': '92%','margin-bottom':'5px','padding-top': span == 24 ? '0px' : '20px'}">
           
                 <recognition :key="recognitionKey"
                            :imgsrc="showUrl + form.upload_image" 
                            @boxClick="boxClick" 
                            :ocr-data="form.output_json"
                            style="height: 100%;width: 100%">
                 </recognition>
        </inc-img>
        <div style="height: 10px;width:100%;display: flex; justify-content: center;">
          <svg width="25" height="25" xmlns="http://www.w3.org/2000/svg">
            <circle cx="12" cy="12" r="10" :fill="'#EB262D'" />
          </svg>
          <span style="font-weight: 500;margin-right: 20px">需要纠错</span>
          <svg width="25" height="25" xmlns="http://www.w3.org/2000/svg">
            <circle cx="12" cy="12" r="10" :fill="'#FFEA2F'" />
          </svg>
          <span style="font-weight: 500">需要确认</span>
        </div>
        </a-layout-sider>
        <a-layout-content style=" background: #fff; min-height: 400px;">
          <luckysheet ref="luckysheetRef"
                    v-if="form.output_excel"
                    :allow-edit="true"
                    :config="config"
                    :save_flag="false"
                    @saveExcel="saveExcel"
                    @cellUpdated="cellUpdated"
                    style="height: calc(100vh - 160px);"
                    :name="form.output_excel">
                    
        </luckysheet>
        <a-button type="primary"
                           size="small"
                           style="z-index: 999;position: absolute;right: 100px;top: -40px"
                           @click="confirmClick()"
                >
                  {{ form.confirm_status == 1 ? '重新提交' : '提交' }}
      </a-button>
        </a-layout-content>
        
      </a-layout>

  </a-card>

  </div>

  
</template>

<script>
import Luckysheet from "@/components/Luckysheet/index.vue";
import Recognition from "@/components/ocr/Recognition.vue";
import IncImg from "@/components/IncImg";
import { list as get_model_list } from '@/services/models' 
import { list as get_structure_list} from '@/services/structure'
import { 
  save, 
  read_excel, recognition, update_by_excel,submit, update,
  find
} from '@/services/tasks'

import {
  upload
} from '@/services/file'

export default {
  name: 'TaskResult',
  components: {
    Luckysheet,
    Recognition,
    IncImg
  },
  data () {
    return {
      form: {
        id: undefined,
        output_excel: '',
        output_image:'',
        upload_image:'',
        output_json:{},
        json_content: {},
        confirm_status: 0,
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
      span: 16,
      showUrl : process.env.VUE_APP_FILE_BASE_URL || '',
      modify_the_value: [],
      loading: false,
      arranged: false,
      icon_name: 'vertical',
      modelList: [],        // List of models for the upload modal's select dropdown
      model_id: null,       // Selected model ID from the upload modal
      recognitionKey: 0,  // 添加这一行
      structureList: [],
      structure_id: null,
    }
  },
  
  mounted() {
    this.getTaskDetail();
    this.fetchActiveModelsForSelection();
    this.getStructureList();
    // 如果有 output_excel，初始化 luckysheet
    if (this.form.output_excel) {
      this.$nextTick(() => {
        this.$refs.luckysheetRef?.initLuckysheet()
          .then(luckysheet => {
            this.luckysheetInstance = luckysheet;
          })
          .catch(error => {
            console.error('Luckysheet初始化失败:', error);
          });
      });
    }
  },
  methods: {
    async getTaskDetail() {
      try {
        const taskId = this.$route.query.id; // 保持原有逻辑
        if (!taskId) {
          this.$message.error('缺少任务ID参数');
          return;
        }
        this.form.id = taskId;
        const response = await find({ id: taskId });
        let taskData = response.data.data;
        

        if (taskData) {
          this.form.output_json = taskData.output_json || {};
          this.form.upload_image = taskData.upload_image || '';
          this.form.output_excel = taskData.output_excel;
          this.model_id = taskData.model_id || null;
          this.recognitionKey += 1;  // 添加这一行，强制 recognition 组件重新渲染
        } else {
          this.form.output_json = {};
          this.form.upload_image = '';
          this.form.output_excel = '';
          this.model_id = null; // 如果没有 taskData，也重置 model_id
          // this.form.confirm_status = 0;
        }
      } catch (error) {
          const errorMsg = error.response?.data?.message || error.message;
          this.$message.error(`获取任务详情失败：${errorMsg}`);
          // 发生错误时，也建议重置表单
          this.form.output_json = {};
          this.form.upload_image = '';
          this.form.output_excel = '';
          this.model_id = null; // 发生错误时，也重置 model_id
          // this.form.confirm_status = 0;
      }
    },

    async getStructureList() {
      try {
        const res = await get_structure_list({
          page: 1,
          size: 100
        })
        const structureRes = res.data
        if (structureRes.code === 200) {
          const { total, record } = structureRes.data
          this.structureList = record.map(item => ({
            ...item,
            key: item.id
          }))
        }
      } catch (error) {
        this.$message.error('获取结构化规则列表失败')
      }
    },

    async fetchActiveModelsForSelection() {
      try {
        const res = await get_model_list({ use_status: 1 }); // Call with use_status: 1
        if (res.data && res.data.code === 200 && res.data.data) {
          this.modelList = res.data.data.record || [];
        } else {
          this.modelList = [];
          this.$message.error('获取可用识别模型列表失败: ' + (res.data.msg || '未知错误'));
        }
      } catch (error) {
        this.modelList = [];
        this.$message.error('请求识别模型列表失败: ' + (error.message || '网络错误'));
      }
    },

    async recognition_click() {
      if (!this.model_id) {
        this.$message.error('请选择识别模型');
        return;
      }
      if (!this.form.id) {
        this.$message.error('任务ID不存在，无法进行识别');
        return;
      }

      this.loading = true;
      this.$message.loading('正在重新识别，请稍候...'); // 显示加载提示

      try {
        const params = {
          id: this.form.id,
          model_id: this.model_id
        };
        const res = await recognition(params); // 调用 recognition 服务

        if (res.data && res.data.code === 200) {
          this.$message.success('重新识别成功');
          await this.getTaskDetail(); // 成功后刷新任务详情
        } else {
          this.$message.error(res.data.msg || '重新识别失败，请重试');
        }
      } catch (error) {
        console.error('重新识别请求失败:', error);
        const errorMsg = error.response?.data?.message || error.message || '重新识别过程中发生错误';
        this.$message.error(`重新识别失败: ${errorMsg}`);
      } finally {
        this.loading = false;
      }
    },

    boxClick(item) {
      console.log('boxClick', item)
      // 确保 luckysheet 已经初始化
      if (this.luckysheetInstance && typeof this.luckysheetInstance.setRangeShow === 'function') {
        this.doLuckysheetAction(item);
      } else {
        // 如果实例不存在或方法不可用，尝试重新获取实例
        const currentInstance = window.luckysheet;
        if (currentInstance && typeof currentInstance.setRangeShow === 'function') {
          this.luckysheetInstance = currentInstance;
          this.doLuckysheetAction(item);
        } else {
          console.error('Luckysheet 实例未就绪');
          this.$message.error('表格未准备就绪，请稍后重试');
        }
      }
    },
    doLuckysheetAction(item) {
      this.luckysheetInstance.setRangeShow({
        row: [item.row[0], item.row[1] - 1],
        column: [item.col[0], item.col[1] - 1]
      });
      
      this.luckysheetInstance.scroll({
        targetRow: item.row[0] - 4,
        targetColumn: item.col[0] - 4,
      });
    },
    // 单元格更新回调
    cellUpdated(r, c, oldValue, newValue) {
      var value = newValue.v;
      if (value === undefined || value === null) { // 检查 undefined 和 null
        if (newValue?.ct?.s && newValue.ct.s.length > 0) {
          value = newValue.ct.s[newValue.ct.s.length - 1]?.v;
        }
      }

      var row = [];
      var col = [];
      console.log('cellUpdated - newValue:', JSON.stringify(newValue));

      if (newValue.mc) { // 如果是合并单元格
        console.log('----------------innn new view (merged cell) ----');
        row = [newValue.mc.r, newValue.mc.r + newValue.mc.rs];
        col = [newValue.mc.c, newValue.mc.c + newValue.mc.cs];
        console.log(`cellUpdated - Merged cell range: row=[${row[0]},${row[1]}), col=[${col[0]},${col[1]})`);
      } else { // 非合并单元格
        console.log('----------------nooo new view (regular cell) ----');
        row = [r, r + 1];
        col = [c, c + 1];
        console.log(`cellUpdated - Regular cell range: row=[${row[0]},${row[1]}), col=[${col[0]},${col[1]})`);
      }

      // 只有当值实际提取出来后才记录修改 (包括空字符串 "" 作为一次有效的清空操作)
      if (value !== undefined && value !== null) {
        this.modify_the_value.push({ 
          row: row,
          col: col,
          value: String(value) // 确保值为字符串类型
        });
      }
      
      console.log('callUpdated - this.modify_the_value:', JSON.stringify(this.modify_the_value));
    },
    async saveExcel(file) {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('id', this.form.id);
      formData.append('output_excel', this.form.output_excel);
      
      this.loading = true;
      try {
        let res = await upload(formData);
        if (res.data.code === 200) {
          let cres = await update_by_excel({
            id: this.form.id,
            modify_the_value: this.modify_the_value || []
          });
          
          this.modify_the_value = [];
          console.log('cres', cres.data.code)
          if (cres.data.code === 200) {
            this.$message.success('暂存成功');
            this.getTaskDetail();
            return;
          }else{
          this.$message.error('暂存失败');
        }
        }else{
          this.$message.error('暂存失败');
        }
        
      } catch (error) {
        this.loading = false;
        console.error(error);
      }
    },
    async confirmClick() {
      this.$message.info('此次是将修改后的excel数据同步到其他系统');
    },
    async arrangedClick() {
      this.arranged = false;
      this.$modal.loading();
      this.icon_name = this.icon_name === 'vertical' ? 'horizontal' : 'vertical';
      this.span = this.icon_name === 'vertical' ? 16 : 24;
      await new Promise(resolve => setTimeout(resolve, 1000));
      this.$modal.closeLoading();
      this.arranged = true;
    }
  },
  
  
}
</script>

<style lang="less" scoped>
 .card-list{
    margin-top: 12px;
  }
  
  ::v-deep .jsoneditor-vue {
    height: calc(100vh - 160px) !important;
  }
</style>
