<template>
  <div class="page-layout">
    <page-header ref="pageHeader" :style="`margin-top: 0px`" >
      <slot name="action"  slot="action"></slot>
      <slot slot="content" name="headerContent"></slot>
      <div slot="content" v-if="!this.$slots.headerContent && desc">
        <p>{{desc}}</p>
        
      </div>
      <slot v-if="this.$slots.extra" slot="extra" name="extra"></slot>
    </page-header>
    <div class="card-list">
      <a-layout>
      
      <a-layout>
        
        <a-layout-content style="padding: 24px; background: #fff; min-height: 280px;">
          <Annotate ref="annotate" />
        </a-layout-content>
      </a-layout>
     
    </a-layout>
  </div>
  </div>

  
</template>

<script>
import PageHeader from '@/components/page/header/PageHeader'
import Annotate from '@/components/ocr/Annotate.vue'  // 添加导入语句
import {
  list,  update_data_set
} from '@/services/tasks'
export default {
  name: 'DatasetLable',
  components: {
    PageHeader,
    Annotate
  },
  data () {
    return {
      annotateComponent: null,  // 添加全局变量
      
      current: 1,
      desc: '标注功能说明：\n1. 标注：在图片上框选区域并添加文本或标签，实现目标内容的精确标注。\n2. 删除标注：选中已添加的标注区域后可进行删除，便于修正错误标注。\n3. 纠偏：对已标注区域的位置、大小等进行调整，确保标注准确。\n4. 保存：一键保存当前所有标注内容，防止数据丢失。\n5. 显示/隐藏背景图：切换图片背景的显示状态，便于专注于标注内容。\n6. 显示/隐藏标注：切换所有标注内容的显示与隐藏，便于对比原图。\n7. 显示/隐藏标注框：单独控制标注框的可见性，提升标注体验和视觉清晰度。',
      form: {
        id: undefined,
        output_excel: '',
        output_image:'',
        output_json:{},
        json_content: {},
        confirm_status: 0,
        
      },
      listLoading : false,
        datasetData: [],
        datasetTotal: 0,
        pageSize: 10,
        page: 1,
        fileList: [],
    }
  },
  created() {
    // 移除这里的调用
    // this.getTaskDetail()
  },
  mounted() {
    // 在组件挂载后初始化全局变量并调用方法
    this.annotateComponent = this.$refs.annotate;
    this.getTaskDetail()
    let params = {
        status: 1,
        rectifye_status: 0,
        data_set_id: this.$route.query.data_set_id,
        page: this.current,
        size: this.pageSize,
      }
    this.fetchUnLabelList(params)
  },
  methods: {
    async fetchUnLabelList(params = {}) {
      this.listLoading = true
      
      try {
        const res = await list({
          
          ...params
        })
        let datasetData = res.data.data
        if (!datasetData || !datasetData.record || datasetData.record.length === 0) {
          this.fileList = []
          this.$message.warning('暂无任务数据')
          return
        }
        this.fileList = datasetData.record
        this.datasetTotal = datasetData.total
        this.current = datasetData.page
      } catch (error) {
        this.$message.error('获取未标注完成列表失败')
      } finally {
        this.listLoading = false
      }
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
      // 添加实际的删除逻辑，使用 item 参数
      console.log('删除项目:', item.title)
      // 这里可以添加确认对话框和实际的删除操作
    },
    onPageChange(page) {
      let params = {
        status: 1,
        rectifye_status: 0,
        data_set_id: this.$route.query.data_set_id,
        page: page,
        size: this.pageSize,
      }
     this.fetchUnLabelList(params)
    },
    handleTypeChange(value) {
      console.log('选择的标签类型:', value)
    },
    handleImageClick(item) {
      if (this.annotateComponent) {
        this.annotateComponent.getDatasetById(item.id);
      }
    },
    
    async getTaskDetail() {
      // 添加空值检查
      if (this.annotateComponent) {
        this.annotateComponent.getDatasetById(this.$route.query.data_id);
      } else {
        console.error('annotateComponent is not initialized');
      }
    }
    // 其他需要使用annotate组件的方法可以直接使用this.annotateComponent
  }
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
    a{
      font-size: 14px;
      margin-right: 32px;
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
    text-overflow: ellipsis;
    display: -webkit-box;
    height: 64px;
    -webkit-line-clamp: 3;
    -webkit-box-orient: vertical;
  }

  .image-list {
    height: calc(100vh - 250px);
    overflow-y: auto;
    
    .ant-card {
      margin-bottom: 8px;
    }
    
    .image-status {
      font-size: 12px;
      color: rgba(0, 0, 0, 0.45);
    }
  }
  
  .sider-header {
    margin-bottom: 16px;
  }
</style>
