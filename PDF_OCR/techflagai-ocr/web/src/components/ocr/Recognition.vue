<template>
    <div class="ann_main" ref="annContainer">
      <div id="image-container" ref="imageContainer">
        <svg id="ocr-svg" ref="ocrSvg" class="ocrsvg" v-show="showSvgImage"></svg>
        <img id="image" ref="imageElement" :src="imgsrc" v-show="showBackgroundImage" style="height: auto;width: 100%"
             alt="Image to OCR"/>
      </div>
    </div>
    <!-- 可拖动的工具条 -->
  </template>
  
  <script>

  import {page} from "@/services/confidence.js";
  
  export default {
  
    props: {
      imgsrc: {
        type: String,
        default: ''
      },
      ocrData: {
        type: [Object, Array],
        default() {
          return null;
        }
      }
    },
    computed: {},
    components: {},
    data() {
      return {
        newText: '',
        selectedBoxIndex: null,
        selectedType: null,
        dragging: false,
        currentPoint: null,
        scaleX: null,
        scaleY: null,
        imgWidth: null,
        imgHeight: null,
        isDrawing: false,
        startX: 0,
        startY: 0,
        polygon: null,
        points: '',
        self_uniqueId: '',
        showDeleteButton: false,
        toolPosition: {
          top: window.innerHeight - 100,  // 工具条初始距离页面底部的距离
          left: window.innerWidth / 2 - 300,
        },
        isDragging: false,  // 是否正在拖动
        offsetX: 0,  // 拖动时的横向偏移量
        offsetY: 0,  // 拖动时的纵向偏移量,
        dsindex: '',
        dsid: '',
        base_ann_resp: null,
        imageElement: null,
        svg: null,
        annotation_id: '',
        annotation_list: [],
        annotation: null,
        showBackgroundImage: true,
        showSvgImage: true,
        confidence_list: [
        ],
        showPolygons: true, // 用于控制 polygon 的显示或隐藏
        // ocrData: null, // 初始化 ocrData
      };
    },
    created() {
      // this.loadOcrData();
    },
    mounted() {
      if (!this.ocrData) {
        console.error('Failed to load OCR data.');
        return;
      }
      this.getConfidence()
  
      this.getDatasetById();
  
      this.imageElement = this.$refs.imageElement;
      this.svg = this.$refs.ocrSvg;
      // 确保图片加载完毕
      if (this.imageElement) {
        this.setupImageLoad(this.imageElement, this.svg);
      } else {
        console.error('Image element with id "image" not found!');
      }
  
      // 添加 SVG 事件监听器
      this.addSvgEventListeners(this.svg);
  
      // 确保页面加载完成后再赋值，防止拖动时获取到 undefined
      this.toolPosition = {
        top: window.innerHeight - 100,
        left: window.innerWidth / 2 - 300,
      };
    },
    methods: {
        
      async getConfidence() {
        //var res = await page()
        //this.confidence_list = res.data.list
        this.confidence_list = [
            {
                "id": 1,
                "conf_color": "rgba(255, 99, 71, 0.2)",
                "conf_value": "0.8",
                "conf_name": "需要纠错",
                "del_flag": 0,
                "create_by": "1",
                "create_time": "2025-04-25T08:16:43",
                "update_by": "1",
                "update_time": "2025-04-25T08:16:43"
            },
            {
                "id": 2,
                "conf_color": "rgba(255, 165, 0, 0.2)",
                "conf_value": "0.9",
                "conf_name": "需要确认",
                "del_flag": 0,
                "create_by": "1",
                "create_time": "2025-04-25T08:16:43",
                "update_by": "1",
                "update_time": "2025-04-25T08:16:43"
            }
        ]
      },
      async getDatasetById() {
        await this.getConfidence()
        this.imageElement = this.$refs.imageElement;
        this.svg = this.$refs.ocrSvg;
  
        // 确保图片加载完毕
        if (this.imageElement) {
          this.setupImageLoad(this.imageElement, this.svg);
        } else {
          console.error('Image element with id "image" not found!');
        }
  
        // 添加 SVG 事件监听器
        this.addSvgEventListeners(this.svg);
      },
      // 更新/保存标注的信息
  
      // 处理图片加载的逻辑
      setupImageLoad(imageElement, svg) {
        const onLoadHandler = () => {
          this.imgWidth = imageElement.naturalWidth;
          this.imgHeight = imageElement.naturalHeight;
  
          this.scaleX = imageElement.clientWidth / this.imgWidth;
          this.scaleY = imageElement.clientHeight / this.imgHeight;
  
          svg.setAttribute('height', imageElement.clientHeight);
          this.initializeOCRData();
          this.renderBoxes(this.ocrData, this.scaleX, this.scaleY);
        };
  
        // 检查图片是否已经加载完成
        if (imageElement.complete) {
          onLoadHandler();
        } else {
          imageElement.onload = onLoadHandler;
        }
      },
      // 添加 SVG 事件监听器
      addSvgEventListeners(svg) {
        // svg.addEventListener('mousedown', this.handleMouseDown);
        // svg.addEventListener('mousemove', this.handleMouseMove);
        // svg.addEventListener('mouseup', this.handleMouseUp);
        // svg.addEventListener('mouseleave', this.handleMouseLeave);
      },
      initializeOCRData() {
        this.addUniqueIdToNodesWithScore(this.ocrData);
      },
      addUniqueIdToNodesWithScore(node) {
        if (node.score !== undefined) {
          if (!node.uniqueId) {
            node.uniqueId = Math.random().toString(36).substr(2, 9);
          } else {
            node.uniqueId = Math.random().toString(36).substr(2, 9);
          }
        }
  
        for (let key in node) {
          if (Array.isArray(node[key])) {
            node[key].forEach((element) => {
              if (element && typeof element === 'object') {
                this.addUniqueIdToNodesWithScore(element);
              }
            });
          }
        }
      },
      renderBoxes(data, scaleX, scaleY) {
        const svg = this.$refs.ocrSvg;
        svg.innerHTML = '';
        data.forEach((item) => {
          item.uniqueId = this.uniqueId_gen();
          this.renderCellOrLine(item, scaleX, scaleY, item.uniqueId, svg, true);
        });
      },
      renderCellOrLine(item, scaleX, scaleY, uniqueId, svg, isLine = false) {
        const position = item.position;
        const score = item.score;
  
        if (position.length !== 8) {
          console.error('Invalid position data:', position);
          return;
        }
  
        // 计算位置坐标
        let x1 = position[0] * scaleX;
        let y1 = position[1] * scaleY;
        let x2 = position[2] * scaleX;
        let y2 = position[3] * scaleY;
        let x3 = position[4] * scaleX;
        let y3 = position[5] * scaleY;
        let x4 = position[6] * scaleX;
        let y4 = position[7] * scaleY;
  
        // 创建 SVG 多边形元素
        const points = `${x1},${y1} ${x2},${y2} ${x3},${y3} ${x4},${y4}`;
        const box = document.createElementNS('http://www.w3.org/2000/svg', 'polygon');
  
        // 设置多边形样式
        var fillColor = null
        for (const item of this.confidence_list) {
          if (score <= item.conf_value) {
            fillColor =  item.conf_color;
             break
          }
        }
        const strokeColor = score !== null && fillColor  != null ? fillColor : 'rgba(0, 0, 255, 0.2)';
  
        if (fillColor == null){
          fillColor  = isLine ? 'rgba(255, 255, 255, 0)'
              : 'rgba(173, 216, 230, 0.5)'
        }
  
  
        box.setAttribute('points', points);
        box.setAttribute('fill', fillColor);
        box.setAttribute('stroke', strokeColor);
        box.setAttribute('stroke-width', 2);
        box.setAttribute('draggable', true);
        box.setAttribute('data-type', isLine ? 'line' : 'table_cell');
        box.setAttribute('data-box-index', uniqueId);
  
        // 绑定双击事件
        box.addEventListener('click', (event) => {
          event.stopPropagation();
          event.preventDefault();
          if (event.target.tagName === 'polygon') {
            this.$emit('boxClick', item)
            this.handleBoxDoubleClick(event, item, svg, x1, y1, x2, y2, x3, y3, x4, y4, uniqueId, position, isLine, box);
          } else {
            console.log(`点击到其他区域了`);
          }
        });
  
        // 添加到 SVG
        svg.appendChild(box);
  
        // 计算文字的中心位置
        const centerX = (x1 + x2 + x3 + x4) / 4;
        const centerY = (y1 + y2 + y3 + y4) / 4;
  
        // 创建 SVG 文本元素
        const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        const textContent = item.text || ''; // 假设 item 包含一个 label 属性
  
        // 设置文本样式
        text.textContent = '';
        text.setAttribute('x', centerX);
        text.setAttribute('y', centerY);
        text.setAttribute('font-family', 'Arial');
        text.setAttribute('font-size', '12px');
        text.setAttribute('fill', 'black');
        text.setAttribute('text-anchor', 'middle'); // 水平居中
        text.setAttribute('dominant-baseline', 'middle'); // 垂直居中
        text.setAttribute('data-box-index', uniqueId);
        text.addEventListener('click', (event) => {
          event.stopPropagation();
          event.preventDefault();
          if (event.target.tagName === 'text') {
            // console.log(`点击到其他区域了`);
            // this.handleBoxDoubleClick(event, item, svg, x1, y1, x2, y2, x3, y3, x4, y4, uniqueId, position, isLine, box);
          } else {
            console.log(`点击到其他区域了`);
          }
        });
        // 添加到 SVG
        svg.appendChild(text);
      },
      handleBoxDoubleClick(event, item, svg, x1, y1, x2, y2, x3, y3, x4, y4, uniqueId, position, isLine, box) {
        event.stopPropagation();
        // 移除所有控制点并设置当前选中的 box
        this.removeAllControlPoints();
        this.selectedBoxIndex = uniqueId;
        this.selectedType = isLine ? 'line' : 'table_cell';
        this.newText = item.text;
        // 添加四个控制点
        this.addControlPoint(svg, x1, y1, uniqueId, 0, isLine, box);
        this.addControlPoint(svg, x2, y2, uniqueId, 1, isLine, box);
        this.addControlPoint(svg, x3, y3, uniqueId, 2, isLine, box);
        this.addControlPoint(svg, x4, y4, uniqueId, 3, isLine, box);
  
        // 更新文本内容并显示删除按钮
        this.$nextTick(() => {
          this.showDeleteButton = true;
        });
      },
      addControlPoint(svg, x, y, boxIndex, pointIndex, isLine, box) {
        const controlPoint = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
        controlPoint.setAttribute('cx', x);
        controlPoint.setAttribute('cy', y);
        controlPoint.setAttribute('r', 5);
        controlPoint.setAttribute('data-box-index', boxIndex);
        controlPoint.setAttribute('data-point-index', pointIndex);
        controlPoint.setAttribute('data-type', isLine ? 'line' : 'table_cell');
        controlPoint.setAttribute('class', 'corner');
        controlPoint.setAttribute('fill', 'rgba(0, 0, 255, 0.5)'); // 添加 fill 属性设置淡蓝色
        svg.appendChild(controlPoint);
  
      },
      startDragControlPoint(e, controlPoint, boxIndex, box) {
        let startX = e.clientX;
        let startY = e.clientY;
        let startCx = parseFloat(controlPoint.getAttribute('cx'));
        let startCy = parseFloat(controlPoint.getAttribute('cy'));
  
        const onMouseMove = (e) => {
          const dx = e.clientX - startX;
          const dy = e.clientY - startY;
  
          controlPoint.setAttribute('cx', startCx + dx);
          controlPoint.setAttribute('cy', startCy + dy);
  
          this.updatePolygonPosition(boxIndex, box);
        };
  
      },
      updatePolygonPosition(boxIndex, polygon) {
        const corners = document.querySelectorAll(`circle[data-box-index='${boxIndex}']`);
        const newPoints = [];
        corners.forEach((corner) => {
          const cx = parseFloat(corner.getAttribute('cx'));
          const cy = parseFloat(corner.getAttribute('cy'));
          newPoints.push(`${cx},${cy}`);
        });
  
        polygon.setAttribute('points', newPoints.join(' '));
  
        const position = newPoints.map((point) => {
          const [cx, cy] = point.split(',');
          return [(parseFloat(cx) / this.scaleX).toFixed(2), (parseFloat(cy) / this.scaleY).toFixed(2)];
        });
  
        const positionText = `Position: [${position[0].join(', ')}], [${position[1].join(', ')}], [${position[2].join(', ')}], [${position[3].join(', ')}]`;
        this.$nextTick(() => {
          this.$refs.dragPosition.textContent = positionText;
        });
  
        this.updateOcrData(boxIndex, position);
      },
      updateOcrData(uniqueId, position) {
        this.ocrData.forEach((item) => {
          this.findAndUpdate(item, uniqueId, position);
        });
      },
      findAndUpdate(obj, uniqueId, position) {
        for (let key in obj) {
          if (obj[key] && typeof obj[key] === 'object') {
            this.findAndUpdate(obj[key], uniqueId, position);
          } else if (key === 'uniqueId' && obj[key] === uniqueId) {
            obj.position = position.flat().map(Number);
          }
        }
      },
      updateOcrDataByText(uniqueId, text) {
        this.ocrData.forEach((item) => {
          this.findAndUpdateByText(item, uniqueId, text);
        });
        this.newText = '';
      },
      findAndUpdateByText(obj, uniqueId, text) {
        for (let key in obj) {
          if (obj[key] && typeof obj[key] === 'object') {
            this.findAndUpdateByText(obj[key], uniqueId, text);
          } else if (key === 'uniqueId' && obj[key] === uniqueId) {
            obj.text = text;
          }
        }
      },
      removePolygonAndData(uniqueId) {
  
        const polygons = document.querySelectorAll(`polygon[data-box-index='${uniqueId}']`);
        polygons.forEach((polygon) => polygon.remove());
  
        const controlPoints = document.querySelectorAll(`circle[data-box-index='${uniqueId}']`);
        controlPoints.forEach((point) => point.remove());
  
        const textPoints = document.querySelectorAll(`text[data-box-index='${uniqueId}']`);
        textPoints.forEach((point) => point.remove());
  
        this.ocrData = this.ocrData.filter((item) => item.uniqueId !== uniqueId);
      },
      removeAllControlPoints() {
        const controlPoints = document.querySelectorAll('.corner');
        controlPoints.forEach((point) => point.remove());
      },
      handleDeleteButtonClick() {
        if (this.selectedBoxIndex !== null) {
          this.removePolygonAndData(this.selectedBoxIndex, this.selectedType);
          this.selectedBoxIndex = null;
          this.selectedType = null;
        }
      },
      //纠偏
      handleNewTextButtonClick() {
        const inputValue = this.newText;
        if (this.selectedBoxIndex !== null && this.selectedType) {
          this.updateOcrDataByText(this.selectedBoxIndex, inputValue);
  
          const overlaySvg = document.getElementById('ocr-svg');
          const textElement = overlaySvg.querySelector(`text[data-box-index="${this.selectedBoxIndex}"]`);
          const polygonElement = overlaySvg.querySelector(`polygon[data-box-index="${this.selectedBoxIndex}"]`);
  
          if (textElement) {
            textElement.textContent = inputValue;
            textElement.setAttribute('fill', 'green'); // 更新字体颜色
            textElement.setAttribute('font-weight', 'bold'); // 设置字体加粗
            polygonElement.setAttribute('stroke', 'green'); // 设置字体颜色
            this.updateOcrDataScore(this.selectedBoxIndex, 1.0);
          } else {
            console.error('Text element not found for uniqueId:', this.selectedBoxIndex);
          }
          this.$message.success('纠偏更新成功！')
        } else {
            this.$message.error('纠偏更新失败！');
        }
  
      },
      // 格式化为训练模型训练需要的数据
      formatAnnotationTrain() {
        const result = [];
        const visited = new Set();  // 用来记录已访问过的对象，避免循环引用
        // 递归遍历函数
        function processItem(item) {
          // 如果 item 是数组，递归遍历每个子项
          if (Array.isArray(item)) {
            item.forEach(subItem => processItem(subItem));
          }
          // 如果 item 是对象
          else if (item && typeof item === 'object') {
            // 避免循环引用，使用 visited 集合进行判断
            if (visited.has(item)) return; // 如果已经处理过这个对象，则返回
            visited.add(item);  // 将当前对象添加到 visited 中
  
            // 如果 item 有 lines 数组且该数组不为空
            //console.log(item.lines)
            if (item.lines && Array.isArray(item.lines) && item.lines.length > 0) {
              item.lines.forEach((line) => {
                // 确保有 position 和 text
                if (line.position && line.position.length > 0 && line.text) {
                  const transcription = line.text;
                  const points = [];
  
                  for (let i = 0; i < line.position.length; i += 2) {
                    points.push([line.position[i], line.position[i + 1]]);
                  }
  
                  result.push({
                    transcription: transcription,
                    points: points,
                  });
                }
              });
            } else {
              // 递归遍历对象的其他属性
              Object.keys(item).forEach((key) => {
                processItem(item[key]);
              });
            }
          }
        }
  
        // 从 ocrData.result.pages 开始递归遍历
        this.ocrData.forEach((page) => {
          processItem(page);
        });
  
        return result;
      },
      
      handleDownloadButtonFormatClick() {
        let result = this.formatAnnotationTrain();
  
        // 下载处理后的数据
        const dataStr = 'data:text/json;charset=utf-8,' + encodeURIComponent(JSON.stringify(result, null, 2));
        const downloadAnchorNode = document.createElement('a');
        downloadAnchorNode.setAttribute('href', dataStr);
        downloadAnchorNode.setAttribute('download', 'updated_ocr_data_formart.json');
        document.body.appendChild(downloadAnchorNode);
        downloadAnchorNode.click();
        downloadAnchorNode.remove();
      },
  
  
      handleDrawButtonClick() {
        this.isDrawing = !this.isDrawing;
        this.self_uniqueId = 'self_' + this.uniqueId_gen();
      },
      handleMouseDown(event) {
        if (!this.isDrawing) {
          // 检查点击事件是否发生在任何 polygon 或相关的 text 元素内部
          const target = event.target;
          if (target.tagName === 'polygon' || target.tagName === 'text') {
            const uniqueId = target.getAttribute('data-box-index');
            const polygon = this.$refs.ocrSvg.querySelector(`polygon[data-box-index="${uniqueId}"]`);
            if (polygon) {
              this.selectPolygon(polygon);
            }
          } else {
            this.removeAllControlPoints();
            this.selectedBoxIndex = null;
            this.selectedType = null;
            this.showDeleteButton = false;
          }
        }
  
        if (!this.isDrawing) return;
  
        this.startX = event.offsetX * this.scaleX;
        this.startY = event.offsetY * this.scaleY;
  
        this.polygon = document.createElementNS('http://www.w3.org/2000/svg', 'polygon');
        this.points = `${this.startX},${this.startY}`;
        this.polygon.setAttribute('points', this.points);
        this.polygon.setAttribute('fill', 'rgba(255, 255, 255, 0.5)');
        this.polygon.setAttribute('stroke', 'green');
        this.polygon.setAttribute('stroke-width', 2);
        this.$refs.ocrSvg.appendChild(this.polygon);
      },
      selectPolygon(polygon) {
        const uniqueId = polygon.getAttribute('data-box-index');
        const type = polygon.getAttribute('data-type');
  
        // 移除所有控制点并设置当前选中的 box
        this.removeAllControlPoints();
        this.selectedBoxIndex = uniqueId;
        this.selectedType = type;
  
        // 添加四个控制点
        const points = polygon.getAttribute('points').split(' ');
        points.forEach((point, index) => {
          const [x, y] = point.split(',').map(Number);
          this.addControlPoint(this.$refs.ocrSvg, x, y, uniqueId, index, type, polygon);
        });
  
        // 更新文本内容并显示删除按钮
        this.$nextTick(() => {
          const position = points.map((point) => point.split(',').map(Number));
          if(this.$refs.originalPosition){
            this.$refs.originalPosition.textContent = `Position: [${position[0].join(', ')}], [${position[1].join(', ')}], [${position[2].join(', ')}], [${position[3].join(', ')}]`;
          }
          this.showDeleteButton = true;
        });
      },
      handleMouseMove(event) {
        if (!this.isDrawing || !this.polygon) return;
  
        const currentX = event.offsetX;
        const currentY = event.offsetY;
        const bottomRight = `${currentX},${currentY}`;
        const bottomLeft = `${this.startX},${currentY}`;
        const topRight = `${currentX},${this.startY}`;
  
        this.points = `${this.startX},${this.startY} ${topRight} ${bottomRight} ${bottomLeft}`;
        this.polygon.setAttribute('points', this.points);
      },
      handleMouseUp() {
        if (!this.isDrawing || !this.polygon) return;
  
        this.isDrawing = false;
  
        const scaledPoints = this.points
            .split(' ')
            .map((point) => {
              const [x, y] = point.split(',');
              return `${parseFloat(x)},${parseFloat(y)}`;
            })
            .join(' ');
  
        const position = scaledPoints
            .split(' ')
            .flatMap((p) => p.split(',').map(Number));
  
        this.selectedBoxIndex = this.self_uniqueId;
        const tableData = this.createTableData(position, this.self_uniqueId);
        this.ocrData.push(tableData);
  
        this.polygon.addEventListener('click', (event) => {
          event.stopPropagation();
          this.removeAllControlPoints();
          this.polygon.setAttribute('data-box-index', this.self_uniqueId);
          this.selectedBoxIndex = this.self_uniqueId;
  
          for (let i = 0; i < position.length; i += 2) {
            this.addControlPoint(this.$refs.ocrSvg, position[i], position[i + 1], this.self_uniqueId, i / 2, 'line', this.polygon);
          }
  
        });
  
        this.polygon.removeEventListener('mousemove', this.handleMouseMove);
        this.polygon.removeEventListener('mouseup', this.handleMouseUp);
      },
      handleMouseLeave() {
        if (!this.isDrawing || !this.polygon) return;
        this.isDrawing = false;
      },
      createTableData(position, uniqueId) {
        const x1 = position[0];
        const y1 = position[1];
        const x2 = position[2];
        const y2 = position[3];
        const x3 = position[4];
        const y3 = position[5];
        const x4 = position[6];
        const y4 = position[7];
  
        return {
          height_of_rows: [],
          type: 'self',
          table_cells: [],
          table_rows: 0,
          width_of_cols: [],
          position: [x1, y1, x2, y2, x3, y3, x4, y4],
          lines: [
            {
              text: this.newText,
              position: [x1, y1, x2, y2, x3, y3, x4, y4],
              score: 0.999,
              uniqueId: uniqueId,
            },
          ],
          table_cols: 0,
        };
      },
      // 开始拖动
      startDrag(event) {
        this.isDragging = true;
        this.offsetX = event.clientX - this.toolPosition.left; // 获取横向偏移量
        this.offsetY = event.clientY - this.toolPosition.top;  // 获取纵向偏移量
        window.addEventListener("mousemove", this.dragMove);
        window.addEventListener("mouseup", this.stopDrag);
      },
      // 拖动过程中
      dragMove(event) {
        if (this.isDragging) {
          // 更新工具条的位置
          this.toolPosition.left = event.clientX - this.offsetX;
          this.toolPosition.top = event.clientY - this.offsetY;
        }
      },
      // 停止拖动
      stopDrag() {
        this.isDragging = false;
        window.removeEventListener("mousemove", this.dragMove);
        window.removeEventListener("mouseup", this.stopDrag);
      },
      handleImageView() {
        if (this.imageSrc) {
          window.open(this.imageSrc, '_blank'); // 使用 _blank 在新标签页打开
        } else {
          this.$message.error('图片地址无效！');
        }
      },
      toggleBackgroundImage() {
        this.showBackgroundImage = !this.showBackgroundImage;
        this.adjustMainHeight();
      },
      toggleSvgImage() {
        this.showSvgImage = !this.showSvgImage;
        this.adjustMainHeight();
      },
      adjustMainHeight() {
        //const backgroundImage = this.$refs.imageElement;
        
      },
      updateOcrDataScore(uniqueId, score) {
        this.ocrData.forEach((item) => {
          this.findAndUpdateScore(item, uniqueId, score);
        });
      },
      findAndUpdateScore(obj, uniqueId, score) {
        for (let key in obj) {
          if (obj[key] && typeof obj[key] === 'object') {
            this.findAndUpdateScore(obj[key], uniqueId, score);
          } else if (key === 'uniqueId' && obj[key] === uniqueId) {
            obj.score = score;
          }
        }
      },
  
      //显示/隐藏标注框
      togglePolygons() {
        this.showPolygons = !this.showPolygons;
        const polygons = this.$refs.ocrSvg.querySelectorAll('polygon');
        polygons.forEach((polygon) => {
          polygon.style.display = this.showPolygons ? 'block' : 'none';
        });
      },
  
      //构建svg格唯一ID
      uniqueId_gen() {
        return Math.random().toString(36).substr(2, 9);
      },
      
    },
  };
  </script>
  
  <style scoped>
  body {
    font-family: Arial, sans-serif;
    margin: 0;
    padding: 20px;
  }
  
  #image-container {
    position: relative;
    width: 100%;
    margin: 0 auto;
    height: 100%;
  }
  
  #image-container img {
    width: 100%;
    height: auto;
    display: block;
    position: relative;
  }
  
  .ocrsvg {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    z-index: 7;
    overflow: visible;
  }
  
  .table-cell .resizable-border {
    position: absolute;
    background: #333;
    z-index: 8;
    box-sizing: border-box;
  }
  
  #position-display span {
    font-weight: bold;
  }
  
  /* 工具条样式 */
  .footer-tools {
    font-size: smaller;
    position: absolute;
    width: 60%;
    background-color: white;
    padding: 5px 10px;
    box-sizing: border-box;
    display: flex;
    flex-direction: column; /* 使用 column 来让子元素垂直排列 */
    justify-content: flex-start; /* 控制子元素从顶部开始排列 */
    align-items: flex-start; /* 左对齐 */
    cursor: move;
    border: 2px solid #409eff;
    border-radius: 2px;
    z-index: 8;
  }
  
  ::v-deep .ann_main {
    padding-top: 10px;
    padding-left: 10px;
    padding-right: 10px;
    padding-bottom: 10px;
  }
  
  .center-container {
    display: flex;
    justify-content: center; /* 水平居中对齐 */
    align-items: center; /* 垂直居中对齐（如果需要） */
  }
  
  #image-container img {
    pointer-events: none;
  }
  </style>
  