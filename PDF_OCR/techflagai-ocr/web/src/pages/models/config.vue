<template>
  <div class="page-layout">
    <page-header ref="pageHeader" :style="`margin-top: 0px`" >
      <slot name="action"  slot="action"></slot>
      <slot slot="content" name="headerContent"></slot>
      <div slot="content" v-if="!this.$slots.headerContent && desc">
        <p>{{desc}}</p>
        <div class="link">
          
        </div>
      </div>
      <slot v-if="this.$slots.extra" slot="extra" name="extra"></slot>
    </page-header>
    <div class="card-step-list">
      <a-steps v-model="step" type="navigation" size="small" :style="stepStyle">
      <a-step
        title="数据准备"
        sub-title=""
        status="finish"
        description="准备并验证训练数据集，确保数据质量"
      />
      <a-step
        title="训练参数"
        sub-title=""
        status="process"
        description="配置训练轮次、批量大小和学习率等核心参数"
      />
      <a-step
        title="提交训练"
        sub-title=""
        status="wait"
        description="启动模型训练任务，监控训练进度"
      />
    </a-steps>
    </div>
    <div class="card-list" style="margin-top: 0;"  v-if="this.step===0">
    
      <a-row class="row">
        <a-col :span="2" class="input_lable">
          模型名称：
        </a-col>
        <a-col >
          <a-input placeholder=""  v-model="modelName"  style="width:300px" >
        </a-input>
        </a-col>
      </a-row> 
      <a-row class="row">
        <a-col :span="2" class="input_lable">
          数据集：
        </a-col>
        <a-col> 
         
          <a-select v-model="selectedDataset" size="small" style="width: 120px;"
                  @change="handleDatasetChange" >
                  <a-select-option v-for="dataset in datasetList" :key="dataset.id" :value="dataset.id">
                    {{ dataset.name }}
                  </a-select-option>
            </a-select>
        
        </a-col>
      </a-row> 
    
      <a-row class="row">
        <a-col :span="2" class="input_lable">
          训练占比:
        </a-col>
        <a-col :span="2"  class="ratio"> 
          <a-input-number
              v-model="train_ratio"
              :min="70"
              :max="95"
              :formatter="value => `${value}%`"
              :parser="value => value.replace('%', '')"
            />
      
        </a-col>
        
        <a-col :span="2" class="input_lable">
          验证占比:
        </a-col>
        <a-col :span="2" class="ratio"> 
          <a-input-number
              v-model="verify_ratio"
              :min="5"
              :max="30"
              :formatter="value => `${value}%`"
              :parser="value => value.replace('%', '')"
              
            />
        </a-col>
      </a-row> 
      <a-row class="row">
        <a-col :span="2">
          
        </a-col>
        <a-col  class="train_desc">
          本工具可完成数据集的训练集和验证集按比例随机切分，如果上传数据焦中含数据切分文件，会进行重新切分并保存为新的数据集，切分占比1-99之间，不可为0
        </a-col>
      </a-row>
      <a-row class="row_button">
      <a-col class="dataset_check" :span="16">
        <a-button style="width: 70%;margin: 0 auto" :disabled="data_set_status == 1"
                       @click="data_check_click">
              {{ data_set_status == 0 ? '开始校验' : data_set_status == 1 ? '校验中' : '重新校验' }}
            </a-button>
      </a-col>
     
    </a-row>
    <a-row class="row" v-if="data_set_status == 2">
      <a-col :span="2" class="train_desc">
        
      </a-col>
      <a-col :span="6" class="train_dataset">
        训练集：{{data_check_result.train_num}}个样本，占比{{train_ratio}}%
      </a-col>
      <a-col :span="6" class="train_dataset">
        验证集：{{data_check_result.val_num}}个样本，占比{{verify_ratio}}%
      </a-col>
      <a-col :span="10" class="train_desc">
        
      </a-col>
    </a-row>
    <a-row class="dataset_preview_row" v-if="data_set_status == 2">
      <a-divider />
      <a-col class="dataset_preview">
        <div style="margin-top: 20px;">
              <div style="display: flex;justify-content: space-between;align-items: center;">
                <div class="dataset_previe_radio">
                  <a-radio-group v-model="datasetType" @change="changeImage">
                    <a-radio-button value="1">训练集</a-radio-button>
                    <a-radio-button value="2">验证集</a-radio-button>
                  </a-radio-group>
                </div>
                <div>抽样展示10个样本</div>
              </div>
              <div style="margin-top: 12px;text-align: center;padding:12px">
                <img style="max-width:100%;height:240px;background:#F7F9FF" :src="getImageUrl(dataimageUrl)" alt="">
                <div class="dataimage_select">
                  <div class="select_item" @click="changedataimage(item,idx)" :class="{'active':dataimageisActive==idx}"
                       :style="'background-image: url('+getImageUrl(item)+')'" v-for="(item,idx) in dataimageList" :key="idx"></div>
                </div>
              </div>
            </div>
      </a-col>
    </a-row>
    <a-row class="row_button">
      
      <a-col class="dataset_next" v-if="data_set_status == 2">
        <a-button type="primary"  @click="toStep(1)" block>下一步</a-button>
      </a-col>
    </a-row>
  </div>
  <div class="card-config-list" style="margin-top: 0;"  v-if="this.step===1">
    <a-row class="train-config-form">
      <a-col >
        <a-form>
          <a-form-item label="轮次(Epochs)" :help="tips.epochs">
            <a-input-number  v-model="train_confing.epochs" class="train-config-item" />
          </a-form-item>
          <a-form-item label="批大小(Batch Size)" :help="tips.batchSize">
            <a-input-number v-model="train_confing.batchSize"  class="train-config-item"  />
          </a-form-item>
          <a-form-item label="学习率(Learning Rate)" :help="tips.learningRate">
            <a-input-number v-model="train_confing.learningRate"  class="train-config-item"   />
          </a-form-item>
          <a-form-item>
            <a-form-item>
              <div class="button-group">
                <a-button type="primary" @click="toStep(0)"  class="btn_next">上一步</a-button>
                <a-button type="primary" @click="toStep(2)"  class="btn_next">下一步</a-button>
              </div>
            </a-form-item>
          </a-form-item>
        </a-form>
      </a-col>
    </a-row>
  </div> 
  <div class="card-config-list" style="margin-top: 0;"  v-if="this.step===2">
    <a-row class="train-config-form">
      <a-col >
        <a-form>
          <a-form-item label="模型框架" :help="tips.models">
            <a-select v-model="selectModel" style="width: 120px" @change="handleModelChange">
                <a-select-option value="jack">
                  Jack
                </a-select-option>
                <a-select-option value="lucy">
                  Lucy
                </a-select-option>
                <a-select-option value="disabled" disabled>
                  Disabled
                </a-select-option>
                <a-select-option value="Yiminghe">
                  yiminghe
                </a-select-option>
              </a-select>
          </a-form-item>
          
          <a-form-item>
            <a-form-item>
              <div class="button-group">
                <a-button type="primary" @click="toStep(1)" class="btn_next">上一步</a-button>
                <a-button type="primary" @click="toStep(3)" class="btn_next">提交</a-button>
              </div>
            </a-form-item>
          </a-form-item>
        </a-form>
      </a-col>
    </a-row>
  </div>  
  <a-result
  v-if="this.step===3"
    style=" background: white; "
    status="success"
    title="新模型提交训练成功，请耐心等待"
    subTitle="模型训练完成后，您可以在模型管理中查看模型的训练状态和性能指标。"
  >
    <template #extra>
      <a-button @click="toModels" type="primary">
      模型管理
      </a-button>
      <a-button @click="toModelLog">
      训练日志
      </a-button>
    </template>
  </a-result>
</div>

  
</template>

<script>
import PageHeader from '@/components/page/header/PageHeader'
import { find,data_check_data,data_check } from '@/services/models'
import { list as datasetList } from '@/services/datasets'

export default {
  name: 'ModelsConfig',
  components: {PageHeader},
  
  data () {
    return {
      current: 1,
      desc: '本OCR模型的训练结果显示出良好的性能指标。模型在识别正确样本方面表现出色，准确率（Accuracy）为80%。精确率（Precision）和召回率（Recall）均为80%，表明模型在识别正样本时的准确性和覆盖率都达到了较高水平。F1分数（F1 Score）为80%，综合了精确率和召回率的表现。均方误差（MSE）和均方根误差（RMSE）均为80%，显示出模型在预测误差方面的稳定性。平均绝对误差（MAE）为80%，进一步验证了模型的预测精度。当前训练状态为：训练中，表明模型仍在持续优化中。',
      modelName: '',
      verify_ratio: 30,
      train_ratio: 70,
      dataimageUrl: 'https://handwrite.oss-cn-nanjing.aliyuncs.com/kqlz1%2F02.png',
      dataimageisActive: 0,
      dataimageList: [     ],
      datasetType: '1',
      step: 0,
      stepStyle: {
        marginBottom: '0px',
        boxShadow: '0px -1px 0 0 #e8e8e8 inset',
        maxWidth: 'none !important',
      },
      tips:{
        "epochs": "训练轮次越大，耗时越久，最终精度通常越高",
        "batchSize": "单卡Batch Size，值越大，显存占用越高",
        "learningRate": "学习率建议参考Batch Size进行同比例的调整",
        "models": "模型框架, 建议选择PaddleOCR"
      },
      train_confing:{
        epochs: 10,
        batchSize: 32,
        learningRate: 0.001
      },
      selectedDataset: '',
      selectModel: '',
      datasetList: [],
      model_id: '',
      data_set_status: 0, //切分状态 0.否 1.切分中 2.切分成功 -1.切分失败
      loading: false,
      data_check_result: {
        "train_num": 0,
        "val_num": 0,
        "val_list": [],
        "train_list": []
      },
      image_base_url: process.env.VUE_APP_FILE_BASE_URL
    }
  },
  async created() {
    this.model_id = this.$route.query.id
    await this.fetchModelData(this.model_id)
    this.fetchDatasets()
  },
  methods: {
    async fetchDatasets() {
      try {
        const res = await datasetList() // 调用数据集列表接口
        this.datasetList = res.data.data.record || []
        console.log('数据集列表', this.datasetList)
      } catch (error) {
        this.$message.error('获取数据集列表失败')
      }
    },
    async fetchModelData(id) {
      if (!id) return
      
      try {
        const res = await find({ id })
        if (res.data?.data) {
          const modelData = res.data.data
          // 更新模型数据
          this.modelName = modelData.name || ''
          this.selectedDataset = modelData.data_set_id || ''
          this.train_ratio = modelData.train_set || 70
          this.verify_ratio = modelData.val_set || 30
          this.data_set_status = modelData.data_set_status || 0
          this.data_check_result =  {
            "train_num": modelData.train_num || 0,
            "val_num": modelData.val_num || 0,
            "val_list": modelData.val_list || [],
            "train_list": modelData.train_list || []
          }

          this.changeImage('1')
          this.dataimageUrl = this.data_check_result.train_list[0]
          
          // 更新训练配置
          if (modelData.customize) {
            const trainConfig = JSON.parse(modelData.customize)
            this.train_confing = {
              epochs: trainConfig.epochs || 10,
              batchSize: trainConfig.batch_size || 32,
              learningRate: trainConfig.learning_rate || 0.001
            }
          }
          
          // 更新模型框架选择
          this.selectModel = modelData.mission_scene || ''
        }
      } catch (error) {
        this.$message.error('获取模型信息失败')
      }
    },
    changedataimage (item, idx)  {
      this.dataimageUrl.value = item
      this.dataimageisActive.value = idx
    },
    changeImage (value) {
      if (value === '1') {
        this.dataimageList = this.data_check_result.train_list
      } else {
        this.dataimageList = this.data_check_result.val_list
      }
    },
    handleModelChange (value) {
      this.selectModel=value
    },
    handleDatasetChange(value) {
      this.selectedDataset = value
    },
    validateStep0() {
      if (!this.modelName?.trim()) {
        this.$message.error('请输入模型名称')
        return false
      }
      if (!this.selectedDataset) {
        this.$message.error('请选择数据集')
        return false
      }
      if (this.train_ratio <= 0 || this.verify_ratio <= 0) {
        this.$message.error('训练占比和验证占比不能为0')
        return false
      }
      if (this.train_ratio + this.verify_ratio !== 100) {
        this.$message.error('训练占比和验证占比之和必须为100%')
        return false
      }
      return true
    },
  
    validateStep1() {
      const { epochs, batchSize, learningRate } = this.train_confing
      if (!epochs || epochs <= 0) {
        this.$message.error('请设置有效的训练轮次')
        return false
      }
      if (!batchSize || batchSize <= 0) {
        this.$message.error('请设置有效的批大小')
        return false
      }
      if (!learningRate || learningRate <= 0) {
        this.$message.error('请设置有效的学习率')
        return false
      }
      return true
    },
  
    validateStep2() {
      if (!this.selectModel) {
        this.$message.error('请选择模型框架')
        return false
      }
      return true
    },
  
    toStep(step) {
      // 前进验证
      if (step > this.step) {
        const validators = {
          1: () => this.validateStep0(),
          2: () => this.validateStep1(),
          3: () => {
            // 提交时验证所有步骤
            return this.validateStep0() && 
                   this.validateStep1() && 
                   this.validateStep2() && 
                   this.submitTraining()
          }
        }
        
        if (validators[step] && !validators[step]()) {
          return
        }
      }
      
      this.step = step
    },
    submitTraining() {
      this.$message.success('训练任务提交成功！')
      return true
    },
    
    toModels() {
      this.$router.push('/models')
    },
    
    toModelLog() {
      this.$router.push('/model/log')
    },

    async data_check_click() {

      if (!this.modelName?.trim()) {
        this.$message.error('请输入模型名称')
        return 
      }

      if (!this.selectedDataset) {
        this.$message.error('请选择数据集')
        return
      }
      
      if (!this.train_ratio) {
        this.$message.error('请设置训练集占比')
        return
      }
      
      if (!this.verify_ratio) {
        this.$message.error('请设置验证集占比')
        return
      }
      if (this.train_ratio + this.verify_ratio !== 100) {
        this.$message.error('训练集占比和验证集占比之和必须为100%')
        return
      }
      
      try {
        await this.$confirm({
          title: '提示',
          content: '确定校验当前数据吗？',
          okText: '确定',
          cancelText: '取消',
          onOk: async () => {  // Add async here
            this.$message.success('数据集校验开始')
              try {
                this.data_set_status = 1 // 设置为校验中状态
                const res = await data_check({
                  id: this.model_id,
                  train_set: this.train_ratio,
                  val_set: this.verify_ratio,
                  data_set_id: this.selectedDataset
                })
                
                if (res.data.code === 200) {
                  this.$message.success('数据集校验成功')
                  this.data_set_status = 2 // 设置为校验成功状态
                  this.data_check_result = res.data.data
                  this.changeImage('1')
                  this.dataimageUrl = this.data_check_result.train_list[0]
                } else {
                  this.$message.error(res.data.msg || '校验失败')
                  this.data_set_status = 0// 设置为校验失败状态
                }
              } catch (error) {
                this.$message.error(error.message || '校验失败')
                this.data_set_status = 0 // 设置为校验失败状态
              } 
          },
          onCancel: () => {
            console.log('取消校验')
          }
        })
      } catch (error) {
        console.error('数据校验失败:', error)
        this.$message.error(error.message || '操作已取消')
      }
    },
    getImageUrl(imageUrl, type = 2) {
      return `${this.image_base_url}${imageUrl}&type=${type}`
    },
  }
}
</script>

<style lang="less" scoped>
:deep(.ant-steps) {
  .ant-steps-item-description {
    max-width: none !important;
    white-space: normal;
  }
}
.stepStyle {
    margin-bottom: '60px';
    box-shadow: '0px -1px 0 0 #e8e8e8 inset';
    :deep(.ant-steps-horizontal:not(.ant-steps-label-vertical) .ant-steps-item-description) {
      max-width: none !important;  // 移除最大宽度限制
      white-space: normal;
      padding-right: 10px;
    }
}

.dataimage_select {
  margin-top: 16px;
  display: flex;
  overflow-x: auto;
}

.select_item {
  cursor: pointer;
  width: 70px;
  height: 52px;
  border-radius: 0px;
  border: 1px solid transparent;
  background: #F7F9FF;
  flex: 0 0 auto;
  margin-right: 8px;
  margin-left: auto;
  background-size: contain;
  background-repeat: no-repeat;
  background-position: center center;
}

.select_item.active {
  border: 1px solid #5061FF;
}

:deep(.ant-tag) {
  color: #333 !important;
}
 .card-list{
    padding-top: 15px;
    margin-top: 24px;
    background: white; 
    padding-bottom: 5px;
  }

  .card-config-list{
    padding-top: 15px;
    margin-top: 24px;
    background: white; 
    padding-bottom: 5px;
    margin-left: auto;    // 添加左右margin为auto实现水平居中
    margin-right: auto;
    padding-left: 24px;   // 添加左右padding使内容更美观
    padding-right: 24px;
  }

  .train-config-form{
    padding-top: 15px;
    margin-top: 24px;
    background: white; 
    padding-bottom: 5px;
    width: 50%;           // 添加宽度50%
    margin-left: auto;    // 添加左右margin为auto实现水平居中
    margin-right: auto;
    padding-left: 24px;   // 添加左右padding使内容更美观
    padding-right: 24px;
    
  }
  .button-group {
      display: flex;
      justify-content: space-between;
      align-items: center;  // 添加垂直居中对齐
      padding: 0 20%;
      margin-top: 20px;
      height: 31px;        // 添加固定高度
      .btn_next {
        width: 150px;
        height: 31px;
        line-height: 31px;
      }
    }
  .train-config-item{
    width: 300px;
  }
  .card-step-list{
    margin-top: 24px;
    background: white; 
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

  .input_lable {
    height: 31px; line-height: 31px; 
    text-align: right;
  }
  .train_desc {
    height: 31px; line-height: 31px; 
    text-align: left;
  }
  .train_dataset{
    background: #1890ff1a;
    padding: 0 10px;
    margin-right: 10px;
    height: 31px; line-height: 31px; 
  }
  .row{
    height: 35px;
  }
  .row_button{
    height: 52px;
    line-height: 52px;
  }
  .ratio{
    padding-left: 10px;
  }
  .dataset_check {
    height:52; line-height: 52px; 
    text-align: center;
    button{
      width: 300px;
    }
  }
  .dataset_next {
    height:52; line-height: 52px; 
    text-align: center;
    button{
      width: 200px;
    }
  }
  .dataset_preview_row{
    margin-right: 20px;
  }
  .dataset_preview{

  }

  .dataset_previe_radio{
    margin-left: 30px;
  }
</style>
