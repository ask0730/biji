<template>
  <div style="background-color: white;">
    <a-card :bordered="false">
      <div style="display: flex; flex-wrap: wrap">
        <head-info title="进行中" :content="`${statusCounts['0']}条`" :bordered="true" />
        <head-info title="已完成" :content="`${statusCounts['1']}条`" :bordered="true" />
        <head-info title="异常" :content="`${statusCounts['2']}条`" />
      </div>
    </a-card>
    <a-divider style="margin-top: 0px;margin-bottom: 0px;background: rgb(240 240 240);" />
    <a-card :bordered="false" class="search-form">
      <a-row>
        <a-col :span="6">
          <a-radio-group default-value="" button-style="solid" @change="sampleStautsOnChange">
            <a-radio-button value="">全部</a-radio-button>
            <a-radio-button value="0">进行中</a-radio-button>
            <a-radio-button value="1">已完成</a-radio-button>
            <a-radio-button value="2">异常</a-radio-button>
          </a-radio-group>
        </a-col>
        <a-col :span="6">
          <div style="display: inline-block; margin-right: 8px; line-height: 32px;">任务名称:</div>
          <a-select v-model="selectedTaskName" placeholder="选择任务名称" style="width: 150px" @change="handleTaskNameChange">
            <a-select-option value="">全部</a-select-option>
            <a-select-option v-for="name in taskNameList" :key="name" :value="name">
              {{ name }}
            </a-select-option>
          </a-select>
        </a-col>
        <a-col :span="6">
          <div style="display: inline-block; margin-right: 8px; line-height: 32px;">数据集:</div>

          <a-select v-model="data_set_id" placeholder="选择数据集" style="width: 150px" @change="handleDatasetChange">
            <a-select-option value="">全部</a-select-option>
            <a-select-option v-for="dataset in datasetList" :key="dataset.id" :value="dataset.id">
              {{ dataset.name }}
            </a-select-option>
          </a-select>

        </a-col>
        <a-col :span="6" style="text-align: right;">
          <a-button @click="addNew" type="primary">上传数据</a-button>
        </a-col>

      </a-row>
    </a-card>

    <!-- 移除重复的列表，只保留一个 -->
    <a-list :grid='{ gutter: 24, xl: 8, lg: 3, md: 3, sm: 2, xs: 1 }' style="padding: 10px;background: white;"
      :loading="listLoading">
      <a-list-item :key="task.id" v-for="task in taskList" style="padding: 0 4px">
        <a-card class="card-list">
          <img slot="cover" :src="getTaskImage(task.upload_image)" @click="handleCardClick(task.id)" height="154" />
          <a-card-meta>
            <div slot="description" style="font-size: 12px;">
              <div> 
                <a-tag :color="task.status === 1 ? '#87d068' : task.status === 2 ? '#f50' : '#2db7f5'">
                  {{ getStatusText(task.status) }}
                </a-tag>
                  <a-tag :color="task.rectifye_status === 1 ? 'green' : undefined">
                    {{ task.rectifye_status === 1 ? '已纠偏' : '未纠偏' }}
                  </a-tag>
                </div>
              <div>{{ task.update_time }}</div>
              <div>
                <a-select v-model="task.data_set_id" size="small" style="width: 120px;"
                  @change="(value) => updateTaskDataset(task.id, value)">
                  <a-select-option v-for="dataset in datasetList" :key="dataset.id" :value="dataset.id">
                    {{ dataset.name }}
                  </a-select-option>
                </a-select>
                <!-- <a-tag color="blue">{{task.data_set_name}}</a-tag> -->
              </div>
            </div>
          </a-card-meta>
        </a-card>
      </a-list-item>
    </a-list>

    <!-- 使用清除浮动确保分页在列表下方 -->
    <div class="pagination-container">
      <a-pagination v-model="current" :show-total="total => `共 ${total} 条记录`" :page-size.sync="pageSize"
        :total="taskTotal" show-less-items @change="onPageChange" />
    </div>

    <a-modal v-model="open" title="上传数据" @ok="handleOk" width="700px" :destroyOnClose="true">
      <template #footer>
        <a-button key="back" @click="handleCancel">取消</a-button>
        <a-button key="submit" type="primary" :loading="loading" @click="handleOk">提交</a-button>
      </template>
      <a-row>
        <a-col :span="12">
          <div class="dataset-upload">
            <div class="upload-label">
              <span class="label">任务名称</span>
            </div>
            <div class="upload-content">
              <a-input placeholder="输入任务名称" v-model="taskName" style="width:300px" />
            </div>
          </div>
        </a-col>
      </a-row>
      <a-row>
        <a-col :span="12">
          <div class="dataset-upload">
            <div class="upload-label">
              <span class="label">识别模型</span>
            </div>
            <div class="upload-content">
              <a-select v-model="model_id" size="small" style="width:300px" @change="handleModelChange">
                <a-select-option v-for="model in modelList" :key="model.id" :value="model.id">
                  {{ model.name }}
                </a-select-option>
              </a-select>
            </div>
          </div>
        </a-col>
      </a-row>
      <a-row style="margin-top: 10px;">
        <a-col :span="12">
          <div class="dataset-upload">
            <div class="upload-label">
              <span class="label">选择文件:</span>
            </div>
            <div class="upload-content">
              <a-upload-dragger 
                v-model="fileList" 
                name="file" 
                :multiple="true"
                :before-upload="falseFn" 
                @change="handleChange"
              >
                <p class="ant-upload-drag-icon">
                  <a-icon type="file-add" theme="twoTone" />
                </p>
                <p class="ant-upload-text">点击或拖拽文件到此区域上传</p>
              </a-upload-dragger>
            </div>
          </div>
        </a-col>
      </a-row>
    </a-modal>

  </div>
</template>

<script>
import HeadInfo from '@/components/tool/HeadInfo'
import {
  save,
  list,  // 修改为list
  statusCount, task_names, update_data_set
} from '@/services/tasks'
import { list as datasetList } from '@/services/datasets'
import { list as get_model_list } from '@/services/models' 

export default {
  name: 'TasksList',
  components: { HeadInfo },
  data() {
    return {
      current: 1,
      taskTotal: 0,
      status: 2, // Default filter status, not related to individual task submission status
      taskName: '',
      fileList: [],
      open: false,
      loading: false,
      pageSize: 16,
      taskList: [],
      listLoading: false,
      statusCounts: {
        "0": 0,
        "1": 0,
        "2": 0
      },
      data_set_id: '',      // For filtering by dataset
      datasetList: [],      // List of datasets for filtering
      selectedTaskName: '', // For filtering by task name
      taskNameList: [],     // List of unique task names for filtering
      modelList: [],        // List of models for the upload modal's select dropdown
      model_id: null,       // Selected model ID from the upload modal
    }
  },
  created() {
    this.fetchTasks()
    this.fetchStatusCount()
    this.fetchDatasets() 
    this.fetchTaskNames()
    this.fetchActiveModelsForSelection() // Fetch active models for the dropdown
  },
  methods: {
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
    /**
     * 阻止 antd Upload 组件的默认上传行为
     * @returns {boolean}总是返回 false
     */
    falseFn() {
      return false;
    },
    /**
     * 处理识别模型选择变化的事件
     * @param {*} value - 当前选中的模型ID
     */
    handleModelChange(value) {
      this.model_id = value;
    },
    async fetchStatusCount() {
      try {
        const res = await statusCount()
        this.statusCounts = res.data.data
      } catch (error) {
        console.error('获取状态统计失败', error)
      }
    },
    onPageChange(page) {
      this.current = page
      this.fetchTasks()
    },

    getStatusText(status) {
      const statusMap = {
        0: '进行中',
        1: '已完成',
        2: '异常'
      }
      return statusMap[status] || '未知状态'
    },
    handleCardClick(id) {
      this.$router.push({
        path: '/task/result',
        query: {
          id: id
        }
      })
    },
    addNew() {
      this.open = true;
      // Reset form fields for the modal
      this.taskName = '';
      this.model_id = null; // Reset selected model
      this.fileList = [];
    },
    sampleStautsOnChange(e) {
      this.current = 1
      const params = {}
      if (e.target.value !== '') {
        params.status = e.target.value
      }
      this.fetchTasks(params)
    },
    async fetchTasks(params = {}) {
      this.listLoading = true
      try {
        const res = await list({
          page: this.current,
          size: this.pageSize,
          ...params
        })
        let taskdata = res.data.data
        if (!taskdata || !taskdata.record || taskdata.record.length === 0) {
          this.taskList = []
          this.$message.warning('暂无任务数据')
          return
        }
        this.taskList = taskdata.record
        this.taskTotal = taskdata.total
        this.current = taskdata.page
      } catch (error) {
        this.$message.error('获取任务列表失败')
      } finally {
        this.listLoading = false
      }
    },

    handleCancel() {
      this.open = false;
      this.taskName = '';
      this.model_id = null;
      this.fileList = [];
    },
    async handleOk() {
      if (!this.taskName || this.taskName.trim() === '') {
        this.$message.warning('请输入任务名称')
        return
      }
      if (!this.model_id) { // Validate if a model is selected
        this.$message.warning('请选择识别模型')
        return
      }
      // this.fileList 现在应该是由 handleChange 更新的原始文件对象数组
      if (!this.fileList || this.fileList.length === 0) {
        this.$message.warning('请选择上传文件')
        return
      }

      this.loading = true
      try {
        const formData = new FormData();
        formData.append('name', this.taskName);
        formData.append('model_id', this.model_id);
        
        // 修改为正确调用save方法
        const res = await save({
          name: this.taskName,
          model_id: this.model_id
        }, this.fileList);
        
        if (res.data.code === 200) {
          this.$message.success('上传成功');
          this.fetchTasks();
          this.fetchStatusCount();
        } else {
          this.$message.error(res.data.msg || '上传失败');
        }
      } catch (error) {
        this.$message.error('上传失败: ' + (error.response?.data?.msg || error.message || '未知错误'));
      } finally {
        this.loading = false
        this.open = false
        this.taskName = ''
        this.model_id = null
        this.fileList = []
      }
    },
    handleChange(info) {
      
      this.fileList = info.fileList.map(file => file.originFileObj).filter(file => file);
    },
    getTaskImage(uploadImage) {
      if (!uploadImage) {
        return 'null'
      }
      return `${process.env.VUE_APP_FILE_BASE_URL}${uploadImage}`
    },
    handleDatasetChange(value) {
      this.current = 1
      const params = {}
      if (value !== '') {
        params.data_set_id = value
      }
      this.fetchTasks(params)
    },
    async fetchDatasets() {
      try {
        const res = await datasetList() // 调用数据集列表接口
        this.datasetList = res.data.data.record || []
      } catch (error) {
        this.$message.error('获取数据集列表失败')
      }
    },
    async fetchTaskNames() {
      try {
        const res = await task_names()
        console.log(res)
        this.taskNameList = res.data.data || []
      } catch (error) {
        this.$message.error('获取任务名称列表失败')
      }
    },
    handleTaskNameChange(value) {
      this.current = 1
      const params = {}
      if (value !== '') {
        params.name = value
      }
      this.fetchTasks(params)
    },
    async updateTaskDataset(taskId, datasetId) {
      try {
        this.$confirm({
          title: '确认修改数据集',
          content: '确定要修改任务的数据集吗？',
          onOk: async () => {
            await update_data_set({ id: taskId, data_set_id: datasetId });
            this.$message.success('数据集更新成功');
            this.fetchTasks(); // 刷新列表
          },
          onCancel: () => {
            // 取消时恢复原值
            this.$message.info('已取消修改');
            this.fetchTasks(); // 刷新列表
          }
        });
      } catch (error) {
        this.$message.error('数据集更新失败');
      }
    },
  }
}
</script>

<style lang="less" scoped>
.card-list {
  ::v-deep .ant-card-body {
    padding-bottom: 6px;
    padding-top: 6px;
  }
}


.pagination-container {
  clear: both;
  /* 清除浮动 */
  width: 100%;
  text-align: center;
  margin-top: 24px;
  padding: 16px 0;
  background: #fff;
}
</style>