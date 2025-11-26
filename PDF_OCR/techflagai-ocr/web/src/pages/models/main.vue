<template>
  <div class="page-layout">
    <page-header ref="pageHeader" :style="`margin-top: 0px`" >
      <slot name="action"  slot="action"></slot>
      <slot slot="content" name="headerContent"></slot>
      <div slot="content" v-if="!this.$slots.headerContent && desc">
        <p>{{desc}}</p>
        <div class="link">
          <span @click="handleNewModel()">
            <a-icon type="plus-circle" />创建模型
          </span>
          
          <span @click="openDoc">
            <a-icon type="file-text" />使用说明
          </span>
        </div>
      </div>
      <slot v-if="this.$slots.extra" slot="extra" name="extra"></slot>
    </page-header>
    <div class="card-list">
    
    <a-list itemLayout="vertical">
      <a-list-item 
        :key="item.id" 
        v-for="item in modelsList" 
        :style="{ position: 'relative', cursor: item.producte_line === 1 ? 'pointer' : 'default' }"
        @click="item.producte_line === 1 ? handleModeConfig(item) : null"
      >
          <a-button 
            v-if="item.status === 2" 
            size="small" 
            type="primary" 
            class="deployed" 
            @click.stop="toggleDeployment(item)" 
            style="color: white;"
          >
            {{ item.use_status === 1 ? '下线' : '发布上线' }}
          </a-button>
          <a-button
                v-if="item.producte_line === 2 || item.producte_line === 3"
                size="small"
                type="primary"
                class="deployed" 
                style="margin-right: 100px;color: white;"
                @click.stop="handleUpdateModel(item)"
              >
                更新模型
          </a-button>
        <a-list-item-meta :title="item.name">
          <!-- 自训练模型 (producte_line === 1) -->
          <div slot="description" v-if="item.producte_line === 1">
            <div v-if="item.status === 2">
              <a-tag v-if="item.acc">准确率（Accuracy）：{{item.acc}}</a-tag>
              <a-tag>训练集占比：{{item.train_set}}%</a-tag>
              <a-tag>测试集占比：{{item.val_set}}%</a-tag>
              <a-tag>状态：
                <span v-if="item.status === 0">配置中</span>
                <span v-if="item.status === 1">运行中</span>
                <span v-if="item.status === 2">运行完成</span>
                <span v-if="item.status === 3">已取消</span>
              </a-tag>
            </div>
            <div v-else>
              <a-tag>状态：
                <span v-if="item.status === 0">配置中</span>
                <span v-if="item.status === 1">运行中</span>
                <span v-if="item.status === 3">已取消</span>
                <span v-else>未知状态</span>
              </a-tag>
            </div>
          </div>
          <!-- 其他模型类型 (producte_line !== 1) -->
          <div slot="description" v-else>
            <a-tag>模型类型：{{ getModelLabel(item.producte_line) }}</a-tag>
            <!-- 状态信息已移除 -->
            <!-- rec_yml 显示，仅当 producte_line 为 2 或 3，且 rec_yml 有效时 -->
            <div 
              style="margin-top: 8px;" 
              v-if="(item.producte_line === 2 || item.producte_line === 3) && item.rec_yml && item.rec_yml !== '{}'"
            >
              <strong>配置详情 :</strong>
              <pre class="rec-yml-display">{{ item.rec_yml }}</pre>
            </div>
          </div>
        </a-list-item-meta>
        <div class="content">
          <div class="train-status" style="margin-top: 12px;">
            <span>更新时间：{{item.update_time}}</span>
            <a-button 
              v-if="item.producte_line === 1" 
              size="small" 
              type="primary" 
              style="margin-left: 16px;" 
              @click.stop
            >
              训练日志
            </a-button>
          </div>
        </div>
      </a-list-item>
    </a-list>
  </div>
  <div class="pagination-container">
  <a-pagination v-model="current" :total="modelsLisTotal" :show-total="total => `共 ${total} 条记录`"  @change="onPageChange" show-less-items  />
  </div>  

  <a-modal 
      v-model="open" 
      title="新增模型" 
      @ok="handleOk" 
      width="500px" 
      :destroyOnClose="true"
    >
      <template #footer>
        <a-button key="back" @click="handleCancel">取消</a-button>
        <a-button key="submit" type="primary" :loading="loading" @click="handleOk">提交</a-button>
      </template>
      
      <a-row>
        <a-col :span="24">
          <div class="dataset-upload">
            <div class="upload-label">
              <span class="label">名称：</span>
            </div>
            <div class="upload-content">
              <a-input 
                v-model="modelName" 
                placeholder="请输入模型名称" 
                style="width: 100%"
                :maxLength="20"
                :rules="[{ required: true, message: '请输入名称', trigger: 'blur' }]"
              />
            </div>
          </div>
        </a-col>
      </a-row>
      <a-row style="margin-top: 16px;">
        <a-col :span="24">
          <div class="dataset-upload">
            <div class="upload-label">
              <span class="label">模型：</span>
            </div>
            <div class="upload-content">
              <a-select v-model="producte_line" @change="updateRecYmlForProvider" style="width: 100%">
                <a-select-option 
                  v-for="option in modelOptions" 
                  :key="option.value" 
                  :value="option.value"
                >
                  {{ option.label }}
                </a-select-option>
              </a-select>
            </div>
          </div>
        </a-col>
      </a-row>

      <!-- JSON输入区域，当选择合合OCR或百度OCR时显示 -->
      <a-row v-if="producte_line === '2' || producte_line === '3'" style="margin-top: 16px;">
        <a-col :span="24">
          <div class="dataset-upload">
            <div class="upload-label" style="margin-bottom: 8px; display: flex; justify-content: space-between; align-items: center;">
              <span class="label">请求 JSON :</span>
              <a-button 
                type="dashed" 
                size="small"
                @click="handleTestRecYml" 
                :loading="testingRecYml"
              >
                测试配置
              </a-button>
              <a @click="openApiDocumentation" style="font-size: 12px;">API 说明</a>
            </div>
            <div class="upload-content">
              <a-textarea 
                v-model="rec_yml" 
                :placeholder="`请输入 ${producte_line === '2' ? '合合OCR' : '百度OCR'} 的 JSON 请求体`" 
                :rows="10"
                style="width: 100%; font-family: monospace;"
              />
            </div>
          </div>
        </a-col>
      </a-row>

    </a-modal>
  
</div>
</template>

<script>
import PageHeader from '@/components/page/header/PageHeader'
// 假设您会在 services/models.js 中添加 test_model_config 方法
import { rec_model_test, list, save_model, test_model_config,update_model } from '@/services/models' 

export default {
  name: 'ModelsList',
  components: {PageHeader},
  
  data () {
    const defaultRecYmlTemplates = {
      '2': JSON.stringify({ // 合合OCR (TextIn)
        "header":{
            "x-ti-app-id":"YOUR_APP_ID", // 请替换为您的实际App ID
            "x-ti-secret-code":"YOUR_SECRET_CODE" // 请替换为您的实际Secret Code
        },
        "body":{

        },
        "parameters":{
                "character":1,
                "straighten": 1,
                "output_order": "table_and_remain",
                "table_type_hint": "automatic",
                "excel": 1
        }
      }, null, 2),
      '3': JSON.stringify({ // 百度OCR
        "header":{
          "API_KEY": "YOUR_API_KEY", 
          "SECRET_KEY": "YOUR_SECRET_KEY" ,
          "Content-Type": "application/x-www-form-urlencoded"
        },
        "body":{ },
        "parameters":{}
      }, null, 2)
    };

    return {
      desc: '本OCR模型的训练结果显示出良好的性能指标。模型在识别正确样本方面表现出色，准确率（Accuracy）为80%。精确率（Precision）和召回率（Recall）均为80%，表明模型在识别正样本时的准确性和覆盖率都达到了较高水平。F1分数（F1 Score）为80%，综合了精确率和召回率的表现。均方误差（MSE）和均方根误差（RMSE）均为80%，显示出模型在预测误差方面的稳定性。平均绝对误差（MAE）为80%，进一步验证了模型的预测精度。当前训练状态为：训练中，表明模型仍在持续优化中。',
      trainStatus: 'finished', // This seems like a static description, not a dynamic status
      // isDeployed: false, // This should be per-model, not global
      current:1,
      pageSize: 10,
      listLoading: false,
      modelsLisTotal: 0,
      modelsList: [],
      modelName: '',
      open: false,
      loading: false,
      producte_line: '1', // 默认选中 '自训练'
      modelOptions: [
        { value: '1', label: '自训练' },
        { value: '2', label: '合合OCR' },
        { value: '3', label: '百度OCR' }
      ],
      rec_yml: '', // 初始化为空字符串
      defaultRecYmlTemplates, // 将模板存储在data中
      testingRecYml: false, // 新增：用于测试按钮的加载状态
      testingRecYmlOK: false,//用户对第三方测试结果的确认状态
    }
  },
  watch: {
    rec_yml(newValue, oldValue) {
      // 如果 rec_yml 是由用户手动编辑（而不是通过 updateRecYmlForProvider 设置的初始模板）
      // 并且新旧值不同，则重置测试确认状态
      if (newValue !== oldValue && this.open) { // 仅在模态框打开时，避免初始化触发
         // 更精确的判断：如果不是由 updateRecYmlForProvider 引起的更改
        const templateForCurrentProvider = (this.producte_line === '2' || this.producte_line === '3') 
                                          ? this.defaultRecYmlTemplates[this.producte_line] 
                                          : '';
        if (newValue !== templateForCurrentProvider || oldValue !== templateForCurrentProvider) {
             this.testingRecYmlOK = false;
        }
      }
    }
  },
  created() {
    this.fetchModels()
  },
  methods: {
    /**
     * 根据 producte_line 的值获取模型标签
     * @param {string|number} producteLineValue - 产品线的值
     * @returns {string} 模型标签，如 '自训练', '合合OCR', '百度OCR', 或 '未知类型'
     */
    getModelLabel(producteLineValue) {
      // Ensure producteLineValue is compared correctly with modelOptions.value (string)
      const option = this.modelOptions.find(opt => opt.value === String(producteLineValue));
      return option ? option.label : '未知类型';
    },
    /**
     * 处理分页变化事件
     * @param {number} page - 当前页码
     */
    onPageChange(page) {
      this.current = page
      this.fetchModels()
    },
    /**
     * 切换模型的发布/下线状态
     * @param {object} item - 模型对象
     */
    toggleDeployment(item) {
      const newStatus = item.use_status === 1 ? 0 : 1; // 切换状态
      const actionText = newStatus === 1 ? '发布上线' : '下线';

      // 创建 payload，复制 item 对象并更新 use_status
      const payload = {
        ...item, // 复制 item 的所有属性
        use_status: newStatus // 更新 use_status
      };
      
      this.loading = true; // 开始加载状态，如果需要的话

      save_model(payload).then(res => {
          if (res.data.code === 200) {
            this.$message.success(`${actionText}成功`);
            item.use_status = newStatus; // 成功后更新列表中的状态
          } else {
            this.$message.error(`${actionText}失败`);
          }
        }).catch(error => {
          this.$message.error(`${actionText}失败：` + (error.response?.data?.msg || error.message || '未知错误'));
        }).finally(() => {
          this.loading = false; // 结束加载状态
        });
    },
    /**
     * 处理更新模型操作，打开模态框并使用选中模型数据预填充表单
     * @param {object} item - 要更新的模型对象
     */
     handleUpdateModel(item) {
      this.modalTitle = '更新模型';
      this.editingModelId = item.id;
      this.currentModelUseStatus = item.use_status; // 存储当前模型的 use_status
      this.modelName = item.name;
      
      const newProductLine = String(item.producte_line);
      this.producte_line = newProductLine; // 设置 product_line

      // 设置 rec_yml
      if (newProductLine === '2' || newProductLine === '3') {
        this.rec_yml = item.rec_yml || this.defaultRecYmlTemplates[newProductLine] || '';
      } else {
        this.rec_yml = ''; // 其他类型（理论上此按钮不显示）
      }

      // 对于编辑第三方OCR模型，默认测试状态为OK，允许用户直接保存或重新测试
      if (newProductLine === '2' || newProductLine === '3') {
        this.testingRecYmlOK = true;
      } else {
        this.testingRecYmlOK = false;
      }

      this.loading = false; // 重置加载状态
      this.open = true;     // 打开模态框
    },
    /**
     * 打开使用说明文档链接
     */
    openDoc() {
      window.open(process.env.VUE_APP_WEBSITE + '/help', '_blank')
    },
    /**
     * 处理模型配置导航
     * @param {object} item - 模型对象
     */
    handleModeConfig(item) {
      this.$router.push({
        path: '/models/config',
        query: {
          id: item ? item.id : null
        }
      })
    },

    /**
     * 根据选择的模型提供商更新 rec_yml 的内容，并重置测试确认状态
     * @param {string} providerValue - 选择的模型提供商的值 ('1', '2', '3')
     */
    updateRecYmlForProvider(providerValue) {
      // producte_line is already updated by v-model on a-select
      if (providerValue === '2' || providerValue === '3') {
        this.rec_yml = this.defaultRecYmlTemplates[providerValue] || '';
      } else {
        this.rec_yml = ''; // 自训练或其他类型不需要rec_yml
      }
      this.testingRecYmlOK = false; // 重置测试确认状态
    },

    /**
     * 处理新建模型操作，打开模态框并初始化表单
     */
    handleNewModel() {
      this.modelName = '';
      this.producte_line = '1'; // 默认选中第一个 '自训练'
      this.updateRecYmlForProvider(this.producte_line); // 根据默认选项更新rec_yml (这也会重置 testingRecYmlOK)
      this.loading = false; // Ensure loading is reset
      this.open = true;
    },
    
    /**
     * 异步获取模型列表数据
     */
    async fetchModels() {
      this.listLoading = true
      try {
        const res = await list({
          page: this.current,
          size: this.pageSize
        })
        this.modelsList = res.data.data.record || []
        this.modelsLisTotal = res.data.data.total || 0
      } catch (error) {
        this.$message.error('获取模型列表失败')
      } finally {
        this.listLoading = false
      }
    },
    /**
     * 处理模态框取消操作
     */
    handleCancel() {
      this.open = false
    },
    /**
     * 重置模态框表单字段，关闭模态框并刷新模型列表
     */
    resetModalForm() {
      this.loading = false;
      this.open = false;
      // Fields are reset in handleNewModel before opening,
      // or explicitly here if preferred after successful submission
      this.modelName = '';
      this.producte_line = '1';
      this.rec_yml = ''; 
      this.testingRecYmlOK = false; // 重置测试状态
      this.fetchModels(); // 刷新列表
    },

    /**
     * 根据当前选择的模型提供商打开对应的 API 文档链接
     */
    openApiDocumentation() {
      if (this.producte_line === '2') {
        window.open('https://www.textin.com/document/recognize_table_multipage', '_blank');
      } else if (this.producte_line === '3') {
        window.open('https://cloud.baidu.com/doc/OCR/s/Al1zvpylt', '_blank');
      }
    },

    /**
     * 处理第三方 OCR 配置 (rec_yml) 的测试请求
     */
    async handleTestRecYml() {
      if (!this.rec_yml || this.rec_yml.trim().length === 0) {
        this.$message.error(`请输入 ${this.producte_line === '2' ? '合合OCR' : '百度OCR'} 的请求 JSON `);
        return;
      }


      this.testingRecYml = true;
      this.testingRecYmlOK = false; // 在开始测试前，重置确认状态
      try {
        const res = await rec_model_test({
          producte_line: parseInt(this.producte_line),
          rec_yml: this.rec_yml 
        });
        if (res.data.code === 200) {
          this.testingRecYmlOK = true;
          this.$message.success('配置测试成功！' + (res.data.msg ? `详情: ${res.data.msg}` : ''));
        } else {
          // testingRecYmlOK 保持 false
          this.$message.error('配置测试失败：' + (res.data.msg || '未知错误'));
        }
      } catch (error) {
        // testingRecYmlOK 保持 false
        this.$message.error('配置测试请求失败：' + (error.response?.data?.msg || error.message || '网络错误'));
      } finally {
        this.testingRecYml = false;
      }
    },

    /**
     * 处理新增/编辑模型表单的提交操作
     * 包含表单校验、JSON 格式校验以及对未测试配置的确认提示
     */
    handleOk() {
      if (!this.modelName || this.modelName.trim().length === 0) {
        this.$message.error('请输入模型名称');
        return;
      }
      if (this.modelName.length > 20) {
        this.$message.error('模型名称不能超过20个字符');
        return;
      }

      const processSave = () => {
        this.loading = true;
        const payload = {
          name: this.modelName,
          producte_line: parseInt(this.producte_line),
          status:2,
          use_status:1,
        };

        if (this.producte_line === '2' || this.producte_line === '3') { // 合合OCR 或 百度OCR
          if (!this.rec_yml || this.rec_yml.trim().length === 0) {
            this.$message.error(`请输入 ${this.producte_line === '2' ? '合合OCR' : '百度OCR'} 的请求 JSON `);
            this.loading = false;
            return;
          }
          try {
            JSON.parse(this.rec_yml); 
            payload.rec_yml = this.rec_yml;
          } catch (e) {
            this.$message.error('请求 JSON  格式无效');
            this.loading = false;
            return;
          }
        } else if (this.producte_line === '1') {
          payload.rec_yml = "{}";
        } else {
          this.$message.warn('未知的模型类型');
          this.loading = false;
          return; 
        }
        
        save_model(payload).then(res => {
          if (res.data.code === 200) {
            let successMessage = '创建模型成功';
            if (this.producte_line === '2') successMessage = '合合OCR 模型配置已提交';
            if (this.producte_line === '3') successMessage = '百度OCR 模型配置已提交';
            this.$message.success(successMessage);
            this.resetModalForm();
          } else {
            this.$message.error(res.data.msg || '操作失败');
          }
        }).catch(error => {
          this.$message.error('操作失败：' + (error.response?.data?.msg || error.message || '未知错误'));
        }).finally(() => {
          this.loading = false; 
        });
      };

      if ((this.producte_line === '2' || this.producte_line === '3') && !this.testingRecYmlOK) {
        this.$confirm({
          title: '确认保存?',
          content: '当前第三方OCR配置测试未通过或未进行测试，是否仍要保存该配置？',
          okText: '仍要保存',
          okType: 'warning',
          cancelText: '取消',
          onOk: () => {
            processSave();
          },
          onCancel: () => {
            // 用户取消，不做任何事情，停留在模态框
          },
        });
      } else {
        processSave();
      }
    }
  }
}
</script>

<style lang="less" scoped>
:deep(.ant-tag) {
  color: #333 !important;
}
 .card-list{
    margin-top: 24px;
    background: white; 
    padding-left: 20px;
  }
 .page-header{
    margin: 0 -24px 0;
  }
  .link{
    /*margin-top: 16px;*/
    line-height: 24px;
    a, span {
      font-size: 14px;
      margin-right: 32px;
      cursor: pointer;
      color: #1890ff;
      i{
        font-size: 22px;
        margin-right: 8px;
      }
    }
  }
  
  .card-avatar {
    width: 48px;
    height: 48px;
    border-radius: 48px;
  }
  .new-btn{
    border-radius: 2px;
    width: 100%;
    height: 187px;
  }
  .extra{
    width: 272px;
    height: 1px;
  }
  .content {
    .detail {
      line-height: 22px;
    }
    .author {
      color: @text-color-second;
      margin-top: 16px;
      line-height: 22px;
      & > :global(.ant-avatar) {
          vertical-align: top;
          margin-right: 8px;
          width: 20px;
          height: 20px;
          position: relative;
          top: 1px;
        }
      & > em {
          color: @disabled-color;
          font-style: normal;
          margin-left: 16px;
        }
    }
  }

  .deployed {
    color: white;
    position: absolute;top: 25px;right: 65px;
  }

  .pagination-container {
    clear: both; /* 清除浮动 */
    width: 100%;
    text-align: center;
    padding: 16px 0;
    background: #fff;
  }

  .rec-yml-display {
    white-space: pre-wrap;    /* CSS3 */
    white-space: -moz-pre-wrap; /* Firefox */
    white-space: -pre-wrap;   /* Opera <7 */
    white-space: -o-pre-wrap;   /* Opera 7 */
    word-wrap: break-word;      /* IE */
    word-break: break-all;
    background-color: #f8f9fa;
    padding: 10px;
    border: 1px solid #e9ecef;
    border-radius: 4px;
    max-height: 120px;
    overflow-y: auto;
    font-size: 0.85em;
    line-height: 1.4;
    color: #495057;
    margin-top: 4px; /* Add some space above the pre block */
  }
</style>
