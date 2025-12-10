import {request}  from '@/utils/request.js'


export function page(data) {
    return request(
        '/ocr/confidence/page',
        'get',
        data
    )
}

export function update(data) {
    return request(
        '/ocr/confidence/update',
        'post',
         data
    )
}
