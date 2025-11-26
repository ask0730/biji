<template>
  <div class="page-layout">
    <page-header ref="pageHeader" :style="`margin-top: 0px`" >
      <slot name="action"  slot="action"></slot>
      <slot slot="content" name="headerContent"></slot>
      <div slot="content" v-if="!this.$slots.headerContent && desc">
        <p>{{desc}}</p>
        <div class="link">
          <span @click="showCreateModal">
            <a-icon type="plus-circle" />创建数据集
          </span>
          
          <span @click="openDoc">
            <a-icon type="file-text" />使用说明
          </span>
        </div>
      </div>
      
      <slot v-if="this.$slots.extra" slot="extra" name="extra"></slot>
    </page-header>
    <div class="card-list">

    <a-list
      :grid="{gutter: 24, lg: 4, md: 2, sm: 1, xs: 1}"
      :loading="listLoading"
      :dataSource="datasetList"
    >
  <a-list-item slot="renderItem" slot-scope="item">
    <a-card :hoverable="true">
      <a-card-meta @click="handleCardClick(item)">
        <div style="margin-bottom: 3px" slot="title">{{item.name}}</div>
       
        <div class="meta-content" slot="description">
          <div class="status-item">
            <a-icon type="database" /> 总数量: <span class="status-value">{{item.total_count}}</span>
          </div>
          <div class="status-item">
            <a-icon type="check-circle" theme="twoTone" two-tone-color="#52c41a" /> 已纠偏: 
            <span class="status-value">{{item.rectify_count}}</span>
          </div>
          <div class="status-item">
            <a-icon type="exclamation-circle" theme="twoTone" two-tone-color="#faad14" /> 未纠偏: 
            <span class="status-value">{{item.status_count}}</span>
          </div>
          <div class="status-item">
            <a-icon type="clock-circle" /> 更新时间: <span class="status-value">{{item.update_time}}</span>
          </div>
        </div>
      </a-card-meta>
      <a slot="actions" @click="handleDetail(item)">详情</a>
      <a slot="actions" @click="handleDelete(item)">删除</a>
    </a-card>
  </a-list-item>
</a-list>

  </div>
  <div class="pagination-container">
    <a-pagination v-model="current" :total="datasetLisTotal" :show-total="total => `共 ${total} 条记录`"  @change="onPageChange" show-less-items />
  </div>

  <a-modal 
      v-model="open" 
      title="新增数据集" 
      @ok="handleOk" 
      width="700px"
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
                v-model="datasetForm.name" 
                placeholder="请输入数据集名称" 
                style="width: 100%"
                :maxLength="20"
                :rules="[{ required: true, message: '请输入名称', trigger: 'blur' }]"
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
import {  list, add, deleteDataset } from '@/services/datasets'

export default {
  name: 'DatasetMain',
  components: {PageHeader},
  data () {
    return {
      current:1,
      desc: '数据集是 OCR 模型训练和评估的基础，支持多种类型的文档图像数据集管理，包括表格、发票、合同等。您可以创建、导入、编辑和管理不同类型的数据集，用于模型训练和性能评估。',
      pageSize: 10,
      listLoading: false,
      datasetLisTotal: 0,
      datasetList: [],
      open: false,
      loading: false,
      datasetForm: {
        name: ''
      }
    }
  },
  created() {
    this.fetchDatasets()
  },
  methods: {
    async fetchDatasets() {
      this.listLoading = true
      try {
        const res = await list({
          page: this.current,
          size: this.pageSize
        })
        this.datasetList = res.data.data.record || []
        this.datasetLisTotal = res.data.data.total || 0
      } catch (error) {
        this.$message.error('获取数据集列表失败')
      }finally {
        this.listLoading = false
      }
    },
    onPageChange(page) {
      this.current = page
      this.fetchDatasets()
    },
    handleCardClick(item) {
      this.$router.push({
        path: '/dataset/list',
        query: {
          id: item.id,
          title: item.title
        }
      })
    },
    handleDetail(item) {
      this.$router.push({
        path: '/dataset/list',
        query: {
          id: item.id,
          mode: 'detail'
        }
      })
    },
    handleDelete(item) {
      this.$confirm({
        title: '确认删除',
        content: '确定要删除这个数据集吗？',
        onOk: () => {
          deleteDataset({id: item.id}).then(res => {
            if (res.data.code === 200) {
              this.$message.success('删除成功')
              this.fetchDatasets()
            } else {
              this.$message.error(res.data.msg || '删除失败')
            }
          }).catch(error => {
            this.$message.error('删除失败')
          })
        },
        onCancel: () => {
          this.$message.info('已取消删除')
        }
      })
  },
  showCreateModal() {
    this.open = true
  },
  handleOk() {
    if (!this.datasetForm.name || this.datasetForm.name.trim().length === 0) {
      this.$message.error('请输入数据集名称')
      return
    }
    if (this.datasetForm.name.length > 20) {
      this.$message.error('数据集名称不能超过20个字符')
      return
    }
    
    this.$confirm({
      title: '确认创建',
      content: '确定要创建这个数据集吗？',
      onOk: () => {
        this.loading = true
        add(this.datasetForm).then(res => {
          this.loading = false
          this.open = false
          this.$message.success('添加数据集成功')
          this.fetchDatasets()
        }).catch(() => {
          this.loading = false
        })
      },
      onCancel: () => {
        this.$message.info('已取消创建')
      }
    })
  },
  handleCancel() {
    this.open = false
    this.datasetForm = {
      name: ''
    }
  },
  
  openDoc() {
    window.open(process.env.VUE_APP_WEBSITE + '/help', '_blank')
  }
  },
  
  
}
</script>

<style lang="less" scoped>
 .card-list{
    margin-top: 24px;
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
  .page-content{
    position: relative;
    padding: 24px 0 0;
    &.side{
    }
    &.head.fixed{
      margin: 0 auto;
      max-width: 1400px;
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
  .meta-content{
    position: relative;
    overflow: hidden;
    display: -webkit-box;
    height: 80px;
    -webkit-box-orient: vertical;
  }
.status-item {
  margin-bottom: 6px;
  display: flex;
  align-items: center;
  
  .anticon {
    margin-right: 8px;
  }
  
  .status-value {
    margin-left: 4px;
    font-weight: 500;
  }
}

.pagination-container {
    clear: both; /* 清除浮动 */
    width: 100%;
    text-align: center;
    padding: 16px 0;
    background: #fff;
  }
</style>
