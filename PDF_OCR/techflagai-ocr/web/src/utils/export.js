/* eslint-disable */

// 文档 https://github.com/exceljs/exceljs/blob/HEAD/README_zh.md
import Excel from 'exceljs'

var setMerge = function (luckyMerge = {}, worksheet) {
    const mergearr = Object.values(luckyMerge);
    mergearr.forEach((elem) => {
        // elem格式：{r: 0, c: 0, rs: 1, cs: 2}
        // 按开始行，开始列，结束行，结束列合并（相当于 K10:M12）,
        // 合并单元格
        worksheet.mergeCells(
            elem.r + 1,
            elem.c + 1,
            elem.r + elem.rs,
            elem.c + elem.cs,
        );
    });
}

/**
 * @description 配置项设置
 * @param {*} configs
 * @param {*} worksheet
 * @returns
 */
var setConfig = function (configs, worksheet) {
    /**
     *  @description luckysheet表格配置项
     *  "rowlen":{}, 表格行高
     *  "columnlen":{}, 表格列宽
     *  "rowhidden":{}, 隐藏行
     *  "colhidden":{}, 隐藏列
     *  "authority":{}, 工作表保护
     */
    // console.log(configs, Object.keys(configs.rowlen), Object.keys(configs.columnlen));
    // 设置隐藏行
    if (configs.rowhidden) {
        Object.keys(configs.rowhidden).forEach((val) => {
            const row = worksheet.getRow(Number(val) + 1);
            row.hidden = true;
        });
    }
    // 设置隐藏列
    if (configs.colhidden) {
        Object.keys(configs.colhidden).forEach((val) => {
            const col = worksheet.getColumn(Number(val) + 1);
            col.hidden = true;
        });
    }
    // 设置显示行
    if (configs.rowlen) {
        Object.keys(configs.rowlen).forEach((val) => {
            // 获取一个行对象。如果尚不存在，则将返回一个新的空对象
            const row = worksheet.getRow((Number(val) + 1));
            // console.log(configs.rowlen[val]);
            // 设置特定的行高
            row.height = configs.rowlen[val] - 10;
        });
    }

    // 设置显示列
    if (configs.columnlen) {
        Object.keys(configs.columnlen).forEach((val) => {
            // 通过键，字母和基于1的列号访问单个列
            const col = worksheet.getColumn((Number(val) + 1));
            // 设置特定的行高
            col.width = (configs.columnlen[val] + 2) / 8;
        });
    }
}

/**
 * @description 表格样式
 * @param {*} borderType
 * @param {*} style
 * @param {*} color
 * @returns
 */
var borderConvert = function (borderType, style = 1, color = '#000') {
    // 对应luckysheet的config中borderinfo的的参数
    if (!borderType) {
        return {};
    }
    const luckyToExcel = {
        type: {
            'border-all': 'all',
            'border-top': 'top',
            'border-right': 'right',
            'border-bottom': 'bottom',
            'border-left': 'left',
        },
        style: {
            0: 'none',
            1: 'thin',
            2: 'hair',
            3: 'dotted',
            4: 'dashDot', // 'Dashed',
            5: 'dashDot',
            6: 'dashDotDot',
            7: 'double',
            8: 'medium',
            9: 'mediumDashed',
            10: 'mediumDashDot',
            11: 'mediumDashDotDot',
            12: 'slantDashDot',
            13: 'thick',
        },
    };
    const template = {
        style: luckyToExcel.style[style],
        color: {argb: color.replace('#', '')},
    };
    const border = {};
    if (luckyToExcel.type[borderType] === 'all') {
        border.top = template;
        border.right = template;
        border.bottom = template;
        border.left = template;
    } else {
        border[luckyToExcel.type[borderType]] = template;
    }
    return border;
}

/**
 *
 * @param {*} borders
 * @param {*} row_index
 * @param {*} col_index
 * @returns
 */
var addborderToCell = function (borders) {
    const border = {};
    const luckyExcel = {
        type: {
            l: 'left',
            r: 'right',
            b: 'bottom',
            t: 'top',
        },
        style: {
            0: 'none',
            1: 'thin',
            2: 'hair',
            3: 'dotted',
            4: 'dashDot', // 'Dashed',
            5: 'dashDot',
            6: 'dashDotDot',
            7: 'double',
            8: 'medium',
            9: 'mediumDashed',
            10: 'mediumDashDot',
            11: 'mediumDashDotDot',
            12: 'slantDashDot',
            13: 'thick',
        },
    };
    Object.keys(borders).forEach((bor) => {
        if (borders[bor].color.indexOf('rgb') === -1) {
            border[luckyExcel.type[bor]] = {
                style: luckyExcel.style[borders[bor].style],
                color: {argb: borders[bor].color.replace('#', '')},
            };
        } else {
            border[luckyExcel.type[bor]] = {
                style: luckyExcel.style[borders[bor].style],
                color: {argb: borders[bor].color},
            };
        }
    });

    return border;
}

var addCellImages = function (images, workbook, worksheet) {
    // 通过 base64  将图像添加到工作簿
    Object.keys(images).forEach((el) => {
        const myBase64Image = images[el];
        const imageId2 = workbook.addImage({
            base64: myBase64Image.src,
            extension: 'png',
        });
        worksheet.addImage(imageId2, {
            tl: {col: myBase64Image.fromCol, row: myBase64Image.fromRow},
            br: {col: myBase64Image.toCol, row: myBase64Image.toRow},
            editAs: 'oneCell', // undefined, oneCell, absolute
            // ext: { width: 500, height: 200 },
        });
    });
}

/**
 * @description 设置边框
 * @param {*} luckyBorderInfo
 * @param {*} worksheet
 * @returns
 */
var setBorder = function (luckyBorderInfo, worksheet) {
    if (!Array.isArray(luckyBorderInfo)) return;
    luckyBorderInfo.forEach((elem) => {
        // 现在只兼容到borderType 为range的情况
        if (elem.rangeType === 'range') {
            const border = borderConvert(elem.borderType, elem.style, elem.color);
            const rang = elem.range[0];
            const {row, column} = rang;
            for (let i = row[0] + 1; i < row[1] + 2; i++) {
                for (let y = column[0] + 1; y < column[1] + 2; y++) {
                    worksheet.getCell(i, y).border = border;
                }
            }
        }
        if (elem.rangeType === 'cell') {
            const {col_index: colIndex, row_index: rowIndex} = elem.value;
            const borderData = Object.assign({}, elem.value);
            delete borderData.col_index;
            delete borderData.row_index;
            const border = addborderToCell(borderData, rowIndex, colIndex);
            // console.log('bordre', border, borderData)
            worksheet.getCell(rowIndex + 1, colIndex + 1).border = border;
        }
        // console.log(rang.column_focus + 1, rang.row_focus + 1)
        // worksheet.getCell(rang.row_focus + 1, rang.column_focus + 1).border = border
    });
}

/**
 * @description 背景色填充
 * @param {*} bg
 * @returns
 */
var fillConvert = function (bg) {
    if (!bg) {
        return {};
    }
    // const bgc = bg.replace('#', '')
    const fill = {
        type: 'pattern',
        pattern: 'solid',
        fgColor: {argb: bg.replace('#', '')},
    };
    return fill;
}

/**
 * @description 字体设置
 * @param {*} ff
 * @param {*} fc
 * @param {*} bl
 * @param {*} it
 * @param {*} fs
 * @param {*} cl
 * @param {*} ul
 * @returns
 */
var fontConvert = function (
    ff = 0,
    fc = '#000000',
    bl = 0,
    it = 0,
    fs = 10,
    cl = 0,
    ul = 0
) {
    // luckysheet：ff(样式), fc(颜色), bl(粗体), it(斜体), fs(大小), cl(删除线), ul(下划线)
    const luckyToExcel = {
        0: '微软雅黑',
        1: '宋体（Song）',
        2: '黑体（ST Heiti）',
        3: '楷体（ST Kaiti）',
        4: '仿宋（ST FangSong）',
        5: '新宋体（ST Song）',
        6: '华文新魏',
        7: '华文行楷',
        8: '华文隶书',
        9: 'Arial',
        10: 'Times New Roman ',
        11: 'Tahoma ',
        12: 'Verdana',
        num2bl: (num) => num !== 0,
    };
    // 出现Bug，导入的时候ff为luckyToExcel的val

    const font = {
        name: typeof ff === 'number' ? luckyToExcel[ff] : ff,
        family: 1,
        size: fs,
        color: {argb: fc.replace('#', '')},
        bold: luckyToExcel.num2bl(bl),
        italic: luckyToExcel.num2bl(it),
        underline: luckyToExcel.num2bl(ul),
        strike: luckyToExcel.num2bl(cl),
    };

    return font;
}

/**
 * @description 单元格排列方式
 * @param {*} vt
 * @param {*} ht
 * @param {*} tb
 * @param {*} tr
 * @returns
 */
var alignmentConvert = function (
    vt = 'default',
    ht = 'default',
    tb = 'default',
    tr = 'default'
) {
    // luckysheet:vt(垂直), ht(水平), tb(换行), tr(旋转)
    const luckyToExcel = {
        vertical: {
            0: 'middle',
            1: 'top',
            2: 'bottom',
            default: 'top',
        },
        horizontal: {
            0: 'center',
            1: 'left',
            2: 'right',
            default: 'left',
        },
        wrapText: {
            0: false,
            1: false,
            2: true,
            default: false,
        },
        textRotation: {
            0: 0,
            1: 45,
            2: -45,
            3: 'vertical',
            4: 90,
            5: -90,
            default: 0,
        },
    };

    const alignment = {
        vertical: luckyToExcel.vertical[vt],
        horizontal: luckyToExcel.horizontal[ht],
        wrapText: luckyToExcel.wrapText[tb],
        textRotation: luckyToExcel.textRotation[tr],
    };
    return alignment;
}

/**
 * @description 单元格创建
 * @param {*} n
 * @returns
 */
var createCellPos = function (n) {
    const ordA = 'A'.charCodeAt(0);

    const ordZ = 'Z'.charCodeAt(0);
    const len = ordZ - ordA + 1;
    let s = '';
    while (n >= 0) {
        s = String.fromCharCode((n % len) + ordA) + s;

        n = Math.floor(n / len) - 1;
    }
    return s;
}

/**
 * @description 设置单元格格式，样式和值
 * @param {*} cellArr
 * @param {*} worksheet
 * @returns
 */
var setStyleAndValue = function (cellArr, worksheet) {
    if (!Array.isArray(cellArr)) return;
    cellArr.forEach((row, rowid) => {
        row.every((cell, columnid) => {
            if (!cell) return true;
            const fill = fillConvert(cell.bg, cell.mc);

            const font = fontConvert(
                cell.ff,
                cell.fc,
                cell.bl,
                cell.it,
                cell.fs,
                cell.cl,
                cell.ul,
            );
            const alignment = alignmentConvert(cell.vt, cell.ht, cell.tb, cell.tr);
            let value = '';

            if (cell.f) {
                value = {formula: cell.f, result: cell.v};
            } else if (!cell.v && cell.ct && cell.ct.s) {
                // xls转为xlsx之后，内部存在不同的格式，都会进到富文本里，即值不存在与cell.v，而是存在于cell.ct.s之后
                // value = cell.ct.s[0].v
                cell.ct.s.forEach(arr => {
                    value += arr.v;
                });
            } else {
                value = cell.v;
            }
            //  style 填入到_value中可以实现填充色
            const letter = createCellPos(columnid);
            const target = worksheet.getCell(letter + (rowid + 1));
            Object.keys(fill).forEach(() => {
                target.fill = fill;
            });
            target.font = font;
            target.alignment = alignment;
            target.value = value;
            return true;
        });
    });
}

const exportExcel = function (luckysheet, value) {
    // 参数为luckysheet.getluckysheetfile()获取的对象
    // 1.创建工作簿，可以为工作簿添加属性
    const workbook = new Excel.Workbook();
    // 2.创建表格，第二个参数可以配置创建什么样的工作表
    if (Object.prototype.toString.call(luckysheet) === '[object Object]') {
        luckysheet = [luckysheet];
    }
    luckysheet.forEach((table) => {
        if (table.data.length === 0) return true;
        // ws.getCell('B2').fill = fills.
        // console.log(table, '+++++++++++');
        const worksheet = workbook.addWorksheet(table.name);
        const merge = (table.config && table.config.merge) || {};
        const borderInfo = (table.config && table.config.borderInfo) || {};
        const configs = table.config || {};
        // 3.设置单元格合并,设置单元格边框,设置单元格样式,设置值
        // 创建单元格并计算单元格内部内容样式及格式
        setStyleAndValue(table.data, worksheet);
        // 是否包含除merge和borderInfo外的luckysheet多余配置项
        if (Object.keys(configs).length > 2) setConfig(configs, worksheet);
        // 合并单元格
        setMerge(merge, worksheet);
        // 计算单元格自身样式
        setBorder(borderInfo, worksheet);
        // 是否包含图片
        if (table.images) addCellImages(table.images, workbook, worksheet);
        return true;
    });

    // 4.写入 buffer
    const buffer = new Promise((resolve) => {
        workbook.xlsx.writeBuffer().then(data => {
            const blob = new Blob([data], {
                type: 'application/vnd.ms-excel;charset=utf-8',
            });
            const File = new window.File([blob], `${value}.xlsx`, {type: 'application/vnd.ms-excel;charset=utf-8'});
            File.uid = File.size + new Date().getTime(); // 文件大小+时间戳
            resolve(File);
            // console.log('导出成功！');
            // FileSaver.saveAs(blob, `${value}.xlsx`);
        });
    });
    return buffer;
}

export {
    exportExcel
}
