import {request} from '@/utils/request'

export function find(data) {
  return request(
    '/ocr/dataset/find',
    'get',
    data
  )
}

export function list(data) {
  return request(
    '/ocr/dataset/list',
    'get',
    data
  )
}

export function add(data) {
  return request(
    '/ocr/dataset/save',
    'post',
    data
  )
}

export function deleteDataset(data) {
  return request(
    '/ocr/dataset/delete',
    'post',
    data
  )
}

/**
 * 更新数据集
 * @param {} data 
 * @returns 
 */
export function annotation_update(data) {
  return request(
    '/ocr/dataset/annotation_update',
    'post',
    data
  )
}