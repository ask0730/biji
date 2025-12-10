<template>
  <div class="page-layout">
    <page-header ref="pageHeader" :style="`margin-top: 0px`" >
      <slot name="action"  slot="action"></slot>
      <slot slot="content" name="headerContent"></slot>
      <div slot="content" v-if="!this.$slots.headerContent && desc">
        <p>{{desc}}</p>
        <div class="link">
          <span @click="addNew">
            <a-icon type="plus-circle" />创建新规则
          </span>
          <span @click="openDoc">
            <a-icon type="file-text" />使用说明
          </span>
        </div>
      </div>
      
      <slot v-if="this.$slots.extra" slot="extra" name="extra"></slot>
    </page-header>
    <a-card class="card-list">
    
    <div>
      
      <standard-table
        :columns="columns"
        :dataSource="structureList"
        :selectedRows.sync="selectedRows"
        @clear="onClear"
        @change="onChange"
        :pagination="{...pagination, onChange: onPageChange}"
      >
        <div slot="description" slot-scope="{text}">
          {{text}}
        </div>
        <div slot="action" slot-scope="{text, record}">
          
          <a style="margin-right: 8px" @click="handleEdit(record)">
            <a-icon type="edit"/>编辑
          </a>
          <a @click="deleteRecord(record.key)">
            <a-icon type="delete" />删除
          </a>
          <router-link :to="`structure/detail?id=${record.key}`" >详情</router-link>
        </div>
        <template slot="statusTitle">
          <a-icon @click.native="onStatusTitleClick" type="info-circle" />
        </template>
      </standard-table>
    </div>
  </a-card>

  <a-modal 
      v-model="open" 
      title="新增数据转换规则" 
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
                v-model="formData.name" 
                placeholder="请输入名称" 
                style="width: 100%"
                :rules="[{ required: true, message: '请输入名称', trigger: 'blur' }]"
              />
            </div>
          </div>
        </a-col>
      </a-row>
      <a-row style="margin-top: 16px">
        <a-col :span="24">
          <div class="dataset-upload">
            <div class="upload-label">
              <span class="label">模板文件：</span>
            </div>
            <div class="upload-content">
              <a-textarea 
                v-model="formData.output_excel" 
                placeholder="请输入模板文件路径"
                :rows="4"
                style="width: 100%"
                :rules="[{ required: true, message: '请输入模板文件路径', trigger: 'blur' }]"
              />
            </div>
          </div>
        </a-col>
      </a-row>
      <a-row style="margin-top: 16px">
        <a-col :span="24">
          <div class="dataset-upload">
            <div class="upload-label">
              <span class="label">类型：</span>
            </div>
            <div class="upload-content">
              <a-select 
                v-model="formData.type" 
                placeholder="请选择类型" 
                style="width: 100%"
                @change="handleTypeChange"
              >
                <a-select-option :value="1">原料进厂</a-select-option>
                <a-select-option :value="2">原料检验</a-select-option>
                <a-select-option :value="3">产品检验</a-select-option>
              </a-select>
            </div>
          </div>
        </a-col>
      </a-row>
      
    </a-modal>
  </div>

  
</template>

<script>
import PageHeader from '@/components/page/header/PageHeader'
import StandardTable from '@/components/table/StandardTable'
import { list, save_or_update ,deleteRecord} from '@/services/structure'

const columns = [
  {
    title: '名称',
    dataIndex: 'name'
  },
  {
    title: '模板文件',
    dataIndex: 'output_excel',
    scopedSlots: { customRender: 'description' }
  },
  {
    title: '类型',
    dataIndex: 'type',
    customRender: (text) => {
      const typeMap = {
        1: '原料进厂',
        2: '原料检验',
        3: '产品检验'
      }
      return typeMap[text] || text
    }
  },
  {
    title: '更新时间',
    dataIndex: 'update_time',
    sorter: true
  },
  {
    title: '操作',
    scopedSlots: { customRender: 'action' }
  }
]

export default {
  name: 'StructureList',
  components: {PageHeader,StandardTable},
  data () {
    return {
      current:1,
      desc: '数据结构化转换是OCR识别后的关键环节。本功能支持将OCR识别后的Excel文件，通过灵活的JSON规则映射，实现数据的智能提取和结构化转换。可处理多种类型的文档，包括表格、发票、合同等，并可自定义转换规则，确保数据能高效、准确地对接到第三方系统。',
      structureList:[],
      advanced: true,
      columns: columns,
      selectedRows: [],
      pagination: {
        current: 1,
        pageSize: 10,
        total: 0
      },
      open: false,
      loading: false,
      formData: {
        name: '',
        output_excel: '',
        type: undefined
      }
    }
  },
  
  mounted() {
    this.getData()
  },
  methods: {
    onPageChange(page, pageSize) {
      this.pagination.current = page
      this.pagination.pageSize = pageSize
      this.getData()
    },
    async getData() {
      try {
        const res = await list({
          page: this.pagination.current,
          size: this.pagination.pageSize
        })
        const structureRes = res.data
        if (structureRes.code === 200) {
          const { total, record } = structureRes.data
          this.structureList = record.map(item => ({
            ...item,
            key: item.id
          }))
          this.pagination.total = total
        }
      } catch (error) {
        this.$message.error('获取结构化规则列表失败')
      }
    },
  deleteRecord(key) {
    this.$confirm({
      title: '确认删除',
      content: '确定要删除这条记录吗？',
      okText: '确认',
      cancelText: '取消',
      onOk: () => {
        deleteRecord({id: key}).then(res => {
          if (res.data.code === 200) {
            this.$message.success('删除成功')
            this.getData()
          } else {
            this.$message.error('删除失败')
          }
        })
      },
      onCancel: () => {
        this.$message.info('已取消删除')
      }
    })
  },


    onClear() {
      this.$message.info('您清空了勾选的所有行')
    },
    onStatusTitleClick() {
      this.$message.info('你点击了状态栏表头')
    },
    onChange() {
      this.$message.info('表格状态改变了')
    },

    addNew () {
      this.formData = {'json_content':{}}
      this.open = true
    },
    handleOk() {
      if (!this.formData.name) {
        this.$message.error('请输入名称')
        return
      }
      if (!this.formData.output_excel) {
        this.$message.error('请输入模板文件路径')
        return
      }
      
      this.loading = true;
      save_or_update(this.formData).then(res => {
        if (res.data.code === 200) {
          this.$message.success('保存成功')
          this.getData()
        } else {
          this.$message.error(res.data.msg)
        }
      })
      this.loading = false;
      this.open = false;
    },
    handleCancel() {
      this.open = false
    },
   
  openDoc() {
    window.open(process.env.VUE_APP_WEBSITE + '/help', '_blank')
  },
  handleEdit(record) {
    this.formData = {
      ...record
    }
    this.open = true
  },
  handleTypeChange(value) {
   this.formData.type = value
  },
    
    
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
  .search{
    margin-bottom: 54px;
  }
  .fold{
    width: calc(100% - 216px);
    display: inline-block
  }
  .operator{
    margin-bottom: 18px;
  }
  @media screen and (max-width: 900px) {
    .fold {
      width: 100%;
    }
  }

</style>
