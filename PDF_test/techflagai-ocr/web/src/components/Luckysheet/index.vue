<template>
  <div class="box">
    <a-button  type="primary"
               size="small"
               style="z-index: 99999;position: absolute;right: 30px;top: -40px"
               @click="saveExcel"
    >
      {{ save_txt }}
    </a-button>
    <div id="luckysheet"></div>
  </div>
</template>

<script>
import LuckyExcel from 'luckyexcel'
import {exportExcel} from "@/utils/export"

export default {
name: 'Luckysheet',
props: {
  name: {
    type: String,
    default: null
  },
  save_txt: {
    type: String,
    default: '暂存'
  },
  save_flag: {
    type: Boolean,
    default: true
  },
  allowEdit: {
    type: Boolean,
    default: true
  },
  watch_name: {
    type: Boolean,
    default: true
  },
  config: {
    type: Object,
    default: () => ({
      showtoolbar: true,
      showsheetbar: false,
      showstatisticBar: true,
      sheetBottomConfig: true,
      showsheetbarConfig: {
        add: false,
        menu: false,
        sheet: false,
      },
    })
  }
},

watch: {
  name: {
    handler(newName) {
      if (newName && this.watch_name) {
        this.downloadExcel()
      }
    }
  }
},

data() {
  return {
    isInitialized: false,  // 添加初始化状态标记
    options: {
      container: 'luckysheet',
      title: 'luckysheet',
      lang: 'zh',
      data: [{
        name: 'Sheet1'
      }]
    },
    showUrl : process.env.VUE_APP_FILE_BASE_URL || '',
  }
},
methods: {
  initLuckysheet() {
    if (this.isInitialized && window.luckysheet && typeof window.luckysheet.destroy === 'function') { // 更严谨的检查
        // 如果已经初始化，并且 luckysheet 对象存在且功能正常，可以考虑是否需要重新创建或直接返回
        // 为了简单起见，如果只是确保创建，可以 return Promise.resolve(window.luckysheet);
        // 但如果 props (如 config) 可能变化并需要重新创建，则继续执行销毁和创建
    }
    
    return new Promise((resolve, reject) => {
      if (typeof window.luckysheet === 'undefined') {
        const err = new Error('Luckysheet library not loaded');
        console.error(err);
        reject(err);
        return;
      }
      
      try {
        if (window.luckysheet.destroy) {
          window.luckysheet.destroy();
        }
        // 合并传入的 config 和默认的 options
        const createOptions = {
          ...this.options, // 包含 container, title, lang, 初始data等
          ...this.config,  // 用户传入的配置，如 showtoolbar 等
          allowEdit: this.allowEdit, // 确保 allowEdit 生效
          showinfobar: false, // 强制不显示信息栏，如果这是全局期望
          // data: this.options.data, // 确保初始 data 存在，除非 loadExcel 会覆盖
        };
        window.luckysheet.create(createOptions);
        this.isInitialized = true;
        resolve(window.luckysheet);
      } catch (error) {
        console.error('Luckysheet初始化失败:', error);
        this.isInitialized = false; // 初始化失败，重置标记
        reject(error);
      }
    });
  },

  async saveExcel() {
    const data = window.luckysheet.getAllSheets()
    const exportData = await exportExcel(data)
    const blob = new Blob([exportData])
    const file = new File([blob], this.name, {
      type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    })
    this.$emit('saveExcel', file)
    return file
  },

  async downloadExcel() {
    try {
      // 直接使用 this.showUrl 和 this.name 构建请求 URL
      let requestUrl = this.name; // 默认情况下，如果 showUrl 为空，则 name 可能已是完整路径或相对路径
      if (this.showUrl) {
          const baseUrl = this.showUrl.endsWith('/') ? this.showUrl.slice(0, -1) : this.showUrl;
          const relativeUrl = this.name.startsWith('/') ? this.name.slice(1) : this.name;
          requestUrl = `${baseUrl}/${relativeUrl}`;
      }

      if (!requestUrl) {
        throw new Error('文件名或路径无效，无法下载文件。');
      }

      console.log(`Fetching Excel file from: ${requestUrl}`);
      const fileResponse = await fetch(requestUrl); 

      if (!fileResponse.ok) {
        throw new Error(`下载文件失败: ${fileResponse.status} ${fileResponse.statusText} (URL: ${requestUrl})`);
      }
      
      const rawData = await fileResponse.blob(); // 获取Blob数据
  
      // 创建blob对象
      const blob = rawData instanceof Blob ? rawData : new Blob([rawData], {
        type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
      });
  
      // 检查blob是否有效
      if (blob.size === 0) {
        throw new Error('文件内容为空');
      }
      if (blob.size < 50) { // Excel文件通常至少有几KB
        console.warn(`文件数据大小为 ${blob.size} bytes，可能不完整或格式不正确。文件名: ${this.name}`);
      }
  
      await this.loadExcel(blob);
    } catch(error) {
      console.error(`文件下载或处理失败 (文件名: ${this.name}):`, error);
      this.$emit('error', {
        type: 'download',
        message: `文件下载或处理失败: ${error.message}`,
        detail: {
          fileName: this.name,
          error: error.stack || error.toString()
        }
      });
    }
  },

  loadExcel(files) {
    return new Promise((resolve, reject) => {
      try {
        if (!(files instanceof Blob)) {
          throw new Error('文件类型必须是Blob');
        }
        
        LuckyExcel.transformExcelToLucky(files, (exportJson, luckysheetfile) => {
          try {
            if (!exportJson || !exportJson.sheets || exportJson.sheets.length === 0) {
              throw new Error('Excel文件解析失败：未获取到有效工作表');
            }

            if (window.luckysheet.destroy) {
              window.luckysheet.destroy();
            }

            exportJson.sheets.forEach(item => {
              item.zoomRatio = 0.85; // 设置缩放比例
            });
            
            // 创建Luckysheet实例时合并配置
            window.luckysheet.create({
              container: 'luckysheet',
              ...this.config, // 用户传入的配置
              allowEdit: this.allowEdit,
              showinfobar: false, // 通常在展示数据时隐藏
              data: exportJson.sheets, // 加载Excel数据
              lang: 'zh', // 语言
              title: exportJson.info?.name || this.name || '在线表格', // 表格标题
              hook: {
                cellMousedownBefore: (cell, position) => {
                  this.$emit('cellMousedownBefore', cell, position);
                },
                cellUpdated: (r, c, oldValue, newValue, isRefresh) => {
                  this.$emit('cellUpdated', r, c, oldValue, newValue, isRefresh);
                }
              }
            });
            this.isInitialized = true; // 确保在成功创建后标记为已初始化
            resolve();
          } catch (error) {
            reject(error);
          }
        });
      } catch (error) {
        reject(error);
      }
    });
  }
},

mounted() {
  if (typeof window.luckysheet === 'undefined') {
    console.error('Luckysheet library not loaded');
    this.$emit('error', { type: 'initialization', message: 'Luckysheet library not loaded' });
    return;
  }
  this.$nextTick(() => {
    this.initLuckysheet().then(() => {
      if (this.name) { // 确保name有效再尝试下载
        this.downloadExcel();
      }
    }).catch(error => {
      console.error("Luckysheet 初始化失败 (mounted):", error);
      this.$emit('error', { type: 'initialization', message: `Luckysheet 初始化失败: ${error.message}` });
    });
  });
},
}
</script>


  <style scoped>
  .download {
    position: absolute;
    z-index: 99;
    left: 10px;
  }
  
  #luckysheet {
    width: 100%;
    height: 100%;
  
    ::v-deep(.luckysheet_info_detail_back) {
      display: none !important;
    }
  
    ::v-deep(.luckysheet-share-logo) {
      display: none !important;
    }
  }
  
  </style>
  