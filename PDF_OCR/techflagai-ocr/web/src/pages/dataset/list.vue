<template>
  <div>
    <a-card :bordered="false" class="search-form">
      <a-row>
        <a-col :span="16">
          <a-radio-group default-value="all" button-style="solid"  @change="sampleStautsOnChange">
            <a-radio-button value="all">全部</a-radio-button>
            <a-radio-button value="ext">已提取</a-radio-button>
            <a-radio-button value="lable">已标注</a-radio-button>
          </a-radio-group>
        </a-col>
        <a-col :span="6">
          
        </a-col>
        <a-col :span="2">
          <a-button @click="addNew" type="primary">上传数据</a-button>
        </a-col>
      </a-row>
    </a-card>
    
    <!-- 移除重复的列表，只保留一个 -->
    <a-list :grid='{ gutter: 24, xl: 8, lg: 3, md: 3, sm: 2, xs: 1 }' style="padding: 10px;background: white;"
      :loading="listLoading">
      <a-list-item :key="task.id" v-for="task in datalList" style="padding: 0 4px">
        <a-card class="card-list">
          <img slot="cover" :src="getTaskImage(task.upload_image)" @click="handleCardClick(task.id)" height="154" />
          <a-card-meta :title="task.name">
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
        :total="datasetTotal" show-less-items @change="onPageChange" />
    </div>

    <a-modal 
      v-model="open" 
      title="上传数据" 
      @ok="handleOk" 
      width="700px"
      :destroyOnClose="true"
    >
      <template #footer>
        <a-button key="back" @click="handleCancel">取消</a-button>
        <a-button key="submit" type="primary" :loading="loading" @click="handleOk">提交</a-button>
      </template>
      <a-row>
        <a-col :span="12">
          <div class="dataset-upload">
            <div class="upload-label">
              <span class="label">数据集：</span>
            </div>
            <div class="upload-content">
              <a-select v-model="upload_dataset_id" size="small" style="width: 120px;"
                  @change="upload_dataset_change">
                  <a-select-option v-for="dataset in datasetList" :key="dataset.id" :value="dataset.id">
                    {{ dataset.name }}
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
                    :multiple="false" 
                    :beforeUpload="beforeUpload"
                    @change="handleChange"
                    accept=".zip" 
                  >
                    <p class="ant-upload-drag-icon">
                      <a-icon type="file-zip" theme="twoTone" />
                    </p>
                    <p class="ant-upload-text">点击或拖拽ZIP压缩包到此区域上传</p>
                  </a-upload-dragger>
            </div>
          </div>
        </a-col>
      </a-row>
    </a-modal>
  </div>
  
</template>

<script>
import {
  list,  update_data_set, dataSetupload
} from '@/services/tasks'
import { list as datasetList } from '@/services/datasets'
import { upload } from '@/services/file'
export default { 
  name: 'DatasetList',
  
  data () {
    return {
      current: 1,
      form: {
        labelCol: { span: 6 },
        wrapperCol: { span: 12 }
      },
      open: false,
      loading: false,
      fileList:[],
      pageSize: 16,
      datasetList: [],
      datasetTotal: 0,
      upload_dataset_id: '',
      datalList: [],
    }
  },
  created() {
    // 初始化逻辑
    const id = this.$route.query.id
    const params = {
      data_set_id: id
    }
    this.fetchTasks(params)
    this.fetchDatasets()
  },
  methods: {
    addNew() {
      // 处理上传数据的逻辑
      this.open = true
      console.log('上传数据')
    },
    handleOk() {
      this.loading = true;
      console.log('this.fileList', this.fileList)
      dataSetupload(this.upload_dataset_id, this.fileList)
        .then(res => {
          this.loading = false;
          this.open = false;
          if (res.data.code === 200) {
            this.$message.success('上传成功');
            this.onPageChange(1); // 刷新列表
          } else {
            this.$message.error(res.data.msg || '上传失败');
          }
        })
        .catch(error => {
          this.loading = false;
          this.$message.error(error.message || '上传失败');
        });
    },
    handleCancel() {
      this.open = false
    },
    upload_dataset_change() {
      console.log('upload_dataset_id', this.upload_dataset_id)
    },
    beforeUpload(file) {
      // 检查文件类型是否为zip
      if (!file.name.toLowerCase().endsWith('.zip')) {
        this.$message.error('请上传ZIP格式的压缩包');
        return false;
      }
      
      // 清空原有文件列表
      this.fileList = [];
      this.fileList.push(file);
      return false; // 阻止自动上传
    },
    handleChange(info) {
      // 更新fileList状态
      if (info.file.status === 'removed') {
        this.fileList = this.fileList.filter(f => f.uid !== info.file.uid);
      } else {
        this.fileList = info.fileList.map(f => f.originFileObj || f);
      }
    },
    
    sampleStautsOnChange(e) {
      let params = {
        data_set_id: this.$route.query.id
      };
      
      switch(e.target.value) {
        case 'ext':
          params.status = 1;
          break;
        case 'lable':
          params.rectifye_status = 1;
          break;
        case 'all':
          // 不添加额外参数
          break;
      }
      
      this.fetchTasks(params);
    },
    handleCardClick(id) {
      this.$router.push({
        path: '/dataset/labeling',
        query: {
          data_id: id,
          data_set_id: this.$route.query.id
        }
      })
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
          this.datalList = []
          this.$message.warning('暂无任务数据')
          return
        }
        this.datalList = taskdata.record
        this.datasetTotal = taskdata.total
        this.current = taskdata.page
      } catch (error) {
        this.$message.error('获取任务列表失败')
      } finally {
        this.listLoading = false
      }
    },
    getTaskImage(uploadImage) {
      if (!uploadImage) {
        return 'https://gw.alipayobjects.com/zos/rmsportal/iZBVOIhGJiAnhplqjvZW.png'
      }
      return `${process.env.VUE_APP_API_BASE_URL}/file/${uploadImage}`
    },
    getStatusText(status) {
      const statusMap = {
        0: '进行中',
        1: '已完成',
        2: '异常'
      }
      return statusMap[status] || '未知状态'
    },
    async fetchDatasets() {
      try {
        const res = await datasetList() // 调用数据集列表接口
        this.datasetList = res.data.data.record || []
        console.log('数据集列表', this.datasetList)
      } catch (error) {
        this.$message.error('获取数据集列表失败')
      }
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
    onPageChange(page) {
      this.current = page
      const params = {
        data_set_id: this.$route.query.id,
        page: page,
        size: this.pageSize
      };
      this.fetchTasks(params);
    },
  }
}
</script>

<style lang="less" scoped>
  .content{
    display: flex;
    margin-top: 16px;
    margin-bottom: -4px;
    line-height: 20px;
    height: 20px;
    & > span {
      color: @text-color-second;
      flex: 1;
      font-size: 12px;
    }
    .avatarList {
      flex: 0 1 auto;
    }
  }
  
  .list-container {
    position: relative;
    min-height: 200px;
    margin-top: 24px;
  }
  
  .pagination-wrapper {
    text-align: center;
    margin-top: 16px;
    padding: 16px 0;
    background: #fff;
  }
  
  /* 移除之前的list-container相关样式 */
  
  .pagination-container {
    clear: both; /* 清除浮动 */
    width: 100%;
    text-align: center;
    margin-top: 24px;
    padding: 16px 0;
    background: #fff;
  }
  
  .dataset-select {
    display: flex;
    align-items: center;
    
    .label {
      margin-right: 8px;
    }
  }

  .dataset-upload {
    display: flex;
    align-items: flex-start;  // 改为顶部对齐
    
    .upload-label {
      flex: 0 0 80px;  // 固定宽度，不会被挤压或拉伸
      margin-right: 8px;
      padding-top: 8px;  // 稍微向下偏移以对齐上传区域
    }
    
    .upload-content {
      flex: 1;  // 占据剩余空间
      min-width: 0;  // 防止内容溢出
    }

    .label {
      white-space: nowrap;  // 防止文字换行
    }
  }
</style>

