import {request} from '@/utils/request.js'

export function query(data) {
    return request(
        '/ocr/task/query',
        'get',
        data
    )
}

export function recognition(data) {
    return request(
        '/ocr/task/recognition',
        'get',
        data
    )
}

export function save(data, files) {
    const formData = new FormData()
    // 确保files是数组
    const fileArray = Array.isArray(files) ? files : [files]
    // 添加文件字段
    fileArray.forEach(file => {
        formData.append('file', file) // 使用'file'作为字段名
    })
    // 添加其他数据字段
    Object.keys(data).forEach(key => {
        formData.append(key, data[key])
    })
    return request(
        '/ocr/task/save',
        'post',
        formData
    )
}

export function dataSetupload(data, files) {
    const formData = new FormData()
    files.forEach(file => {
        formData.append('file', file)  // 每个文件单独添加
    })
    formData.append('data_set_id', data)
    return request(
        '/ocr/task/dataSetupload',
        'post',
        formData
    )
}

export function read_excel(data) {
    return request(
        '/ocr/task/read_excel',
        'get',
        data
    )
}

/**
 * 更新excel修改后对应的json值
 * @param {g} data 
 * @returns 
 */
export function update_by_excel(data) {
    return request(
        '/ocr/task/update_by_excel',
        'post',
        data
    )
}

export function submit(data) {
    return request(
        '/ocr/task/submit',
        'post',
        data
    )
}

export function test() {
    return request(
        '/ocr/task/test',
        'get'
    )
}

export function list(data) {
    return request(
        '/ocr/task/list',
        'get',
        data
    )
}

export function find(data) {
    return request(
        '/ocr/task/find',
        'get',
        data
    )
}

export function statusCount() {
    return request(
        '/ocr/task/status_count',
        'get'
    )
}

export function update(data) {
    return request(
        '/ocr/confidence/update',
        'post',
         data
    )
}


export function task_names() {
    return request(
        '/ocr/task/names',
        'get'
    )
}

export function update_data_set(data) {
    return request(
        '/ocr/task/update_data_set',
        'post',
         data
    )
}
/**
 * 切割图片为训练用的数据集
 * @param {} data 
 * @returns 
 */
export function cutting_img(data) {
    return request(
        '/train/cutting_img',
        'post',
         data
    )
}

export function save_version(data) {
    return request(
        '/ocr/task/save_version',
        'post',
        data
    )
}