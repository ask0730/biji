import {request} from '@/utils/request.js'

export function find(data) {
  return request(
    '/ocr/model/find',
    'get',
    data
  )
}


export function list(data) {
  return request(
    '/ocr/model/list', 
    'get',
    data
  )
}
// 保存新模型
export function save_model(data) {
  return request(
      '/ocr/model/save',
      'post',
      data)
}

/**
 * 测试第三方模型配置的信息是否有效
 * @param {} data 
 * @returns 
 */
export function rec_model_test(data) {
  return request(
      '/ocr/model/model_test',
      'post',
      data)
}

// 获取文件
export function data_check_data(data) {
  return request(
      '/ocr/train/data_check_data',
      'post',
      data)
}

export function data_check(data) {
  return request(
      '/ocr/train/data_check',
      'post',
      data
  )
}

