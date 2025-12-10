import {request} from '@/utils/request.js'

export function list(data) {
    return request(
        '/ocr/structure/list',
        'get',
         data
    )
}


export function find(data) {
    return request(
        '/ocr/structure/find',
        'get',
        data
    )
}


export function save_or_update(data) {
    return request(
        '/ocr/structure/save_or_update',
         'post',
         data
    )
}

export function deleteRecord(data) {
    return request(
        '/ocr/structure/delete',
        'post',
        data
    )
}
