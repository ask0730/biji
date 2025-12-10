import {request} from '@/utils/request'

export function showFile(data) {
    return request(
        '/file/showFile',
        'get',
        data,
        {
            responseType: 'blob'
        }
    )
}
export function showFileTxt(data) {
    return request(
         '/file/showFile',
        'get',
         data
    )
}

export function upload(data) {
    return request(
         '/file/upload',
        'post',
        data
    )
}
