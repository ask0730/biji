# -*- coding: utf-8 -*-
import base64
import json
import os
import uuid
import zipfile
from utils.result import Result

from api import  db
from models.DataSetModel import DataSetModel
from models.OcrTaskHistoryModel import OcrTaskHistoryModel
from models.OcrTaskModel import OcrTaskModel
from models.OcrStructureModel import OcrStructureModel
from models.TrainModel import TrainModel
from models.ConfidenceModel import ConfidenceModel
from utils import modelUtil, uuidUtil, tokenUtil
import datetime
from utils.thirdOcr import ThirdPartyOCR 
from config.otherConfig import OtherConfig

_config = OtherConfig()

def query(ocrTaskModel):
    query = OcrTaskModel.query.filter_by(del_flag=0)

    res = query.paginate(page=ocrTaskModel.page, per_page=ocrTaskModel.limit, error_out=False)
    return modelUtil.page_to_json(res, date_format=True)


def save(ocrTaskModel, file):
    target_dir = _config.FILE_PATH

    # 使用uuid生成唯一标识符
    #data_set_id = ocrTaskModel.data_set_id if ocrTaskModel.data_set_id else _config.DEFAULT_DATASET_ID
    unique_id = uuidUtil.getuuid()
    #上传识别的任务不属于任何数据集，可以在前台将识别的加入到数据集中
    data_set_id = unique_id
    # 创建目标目录，如果不存在
    if not os.path.exists(target_dir + data_set_id):
        os.makedirs(target_dir + data_set_id, exist_ok=True)

    # 获取原始文件扩展名
    extension = file.filename.rsplit('.', 1)[-1].lower()
    # 创建新的文件名
    new_filename = f"{unique_id}.{extension}"

    # 指定保存的完整路径
    save_path = os.path.join(target_dir + data_set_id, new_filename)

    # 保存文件并重命名
    file.save(save_path)

    ocrTaskModel.id = unique_id

    user_id = tokenUtil.getUser().user_id

    ocrTaskModel.upload_image = data_set_id + '/' + new_filename
    ocrTaskModel.create_by = user_id
    ocrTaskModel.update_by = user_id
    # 查询模型
    trainModel = (TrainModel.query
                  .filter(TrainModel.id == ocrTaskModel.model_id)
                  .filter(TrainModel.use_status == 1)
                  .first())

    if trainModel is not None:
        ocrTaskModel.model_id = trainModel.id
   
    if trainModel is not None and trainModel.producte_line == 1:
        db.session.add(ocrTaskModel)
        db.session.commit()
        # 调用识别接口
        # 针对批量处理的，可以作为后台改任务
        # 启动异步任务
        # TODO: 待实现异步任务
        return {
            'id': ocrTaskModel.id
        }
    else:
        rec_yml = trainModel.rec_yml
        _ocr = ThirdPartyOCR(config=rec_yml)
        if trainModel.producte_line == 2:
            res = _ocr._recognize_textin(save_path)
            ocr_resp = _ocr._recognize_textin(save_path)
            ocr_result = ocr_resp.get('result', {})
            if ocr_resp and ocr_resp.get('code') == 200:
                if ocr_result and ocr_result.get('excel'):
                    excel_base64 = ocr_result['excel']
                    excel_path = save_excel_from_base64(excel_base64, target_dir, ocrTaskModel.id)
                    if excel_path is None:
                        print("错误：无法保存excel文件。")
                        return {"code": 500,'msg': "无法保存excel文件。"}
                ocrTaskModel.output_json = ThirdPartyOCR.extract_textin(ocr_resp)
                ocrTaskModel.status = 1
                ocrTaskModel.output_excel = excel_path
                db.session.add(ocrTaskModel)
                db.session.commit()
                return {"code":200,'msg':"识别成功"}
            else:
                ocrTaskModel.status = 2
                db.session.add(ocrTaskModel)
                db.session.commit()
                return {"code":500,'msg':res.get('msg', {})}
        elif trainModel.producte_line == 3:
            res = _ocr._recognize_baidu(save_path)
            if res and 'error_code' not in res: 
                ocrTaskModel.output_json = res.get('result', {}).get('tables', [])
                db.session.add(ocrTaskModel)
                ocrTaskModel.status = 1
                db.session.commit()
                return {"code":200,'msg':"识别成功"}
            else:
                ocrTaskModel.status = 2
                db.session.add(ocrTaskModel)
                db.session.commit()
                return {
                    "code": 500,
                    "msg": res.get('error_msg', '百度OCR识别失败')
                }

def recognition(req):
    query = OcrTaskModel.query

    if req.id is not None:
        query = query.filter_by(id=req.id)
    
    task = query.first()
    
    target_dir = _config.FILE_PATH
   
    save_path = target_dir + task.upload_image    # 你需要提供 save_path 的实际获取逻辑
    model_query = TrainModel.query
    model_query = model_query.filter(TrainModel.id == req.model_id) # 修改此行
    model = model_query.first()

    rec_yml = model.rec_yml  
    producte_line = model.producte_line

    if not model or not model:
        # 处理 trainModel 或 rec_yml 不可用的情况
        return {"code": 500, 'msg': "无法获取模型信息或配置文件。"}

    _ocr = ThirdPartyOCR(config=rec_yml)
    if producte_line == 2:
        ocr_resp = _ocr._recognize_textin(save_path)
        ocr_result = ocr_resp.get('result', {})
        
        if ocr_resp and ocr_resp.get('code') == 200:
            if ocr_result and ocr_result.get('excel'):
                excel_base64 = ocr_result['excel']
                excel_path = save_excel_from_base64(excel_base64, target_dir, req.id)
                if excel_path is None:
                    # 处理保存excel文件失败的情况
                    print("错误：无法保存excel文件。")
                    return {"code": 500,'msg': "无法保存excel文件。"}
                else:
                    update_ocr_task_status(task_id=req.id, status=1, output_excel=excel_path, result=ThirdPartyOCR.extract_textin(ocr_resp))
                    return {"code": 200, "msg": "识别成功", "data": ocr_result}
                
            # 考虑返回成功信息
            return {"code": 200, "msg": "识别成功", "data": ocr_result}
        else:
            return {"code": 500, 'msg': ocr_result.get('msg', 'TextIn OCR 识别失败')}
    elif producte_line == 3:
        ocr_result = _ocr._recognize_baidu(save_path)
        if ocr_result and 'error_code' not in ocr_result:
           
            # 考虑返回成功信息
            return {"code": 200, "msg": "识别成功", "data": ocr_result}
        else:
            return {
                "code": 500,
                "msg": res.get('error_msg', '百度OCR识别失败')
            }
    else:
        # 处理未知的 producte_line
        return {"code": 500, 'msg': f'未知的生产线类型'}


def save_excel_from_base64(excel_base64, target_dir, file_id):
    """将base64格式的excel还原为文件"""
    try:
        excel_bytes = base64.b64decode(excel_base64)
        excel_dir = os.path.join(target_dir, file_id)
        os.makedirs(excel_dir, exist_ok=True)
        excel_path = os.path.join(excel_dir, f"{file_id}.xlsx")
        with open(excel_path, "wb") as f:
            f.write(excel_bytes)
        return file_id + '/' + file_id + '.xlsx'
    except Exception as e:
        print(f"还原excel文件异常: {e}")
        return None

# 识别完成后，更新任务状态
# :param task_id: 任务id
# :param status: 状态
# :param output_excel: 输出excel
# :param result: 结果    
def update_ocr_task_status(task_id, status,output_excel, result):
    """更新OcrTaskModel的识别状态和输出路径"""  
    OcrTaskModel.query.filter(OcrTaskModel.id == task_id).update({
    OcrTaskModel.status: status,
    OcrTaskModel.output_excel: output_excel,
    OcrTaskModel.output_json: result
    }, synchronize_session='fetch')
    db.session.commit()


def dataSetupload(req, file):
    target_dir = _config.FILE_PATH
    user_id = tokenUtil.getUser().user_id

    count = 0
    dataSetupload = DataSetModel()
    data_set_id = req.data_set_id if req.data_set_id else _config.DEFAULT_DATASET_ID
    if req.id is None:
        dataSetupload.name = req.name
        dataSetupload.id = uuid.uuid4().hex
        dataSetupload.create_by = user_id
        dataSetupload.update_by = user_id
        db.session.add(dataSetupload)
        db.session.commit()
    else:
        dataSetupload.id = req.id

    with zipfile.ZipFile(file, 'r') as zip_ref:  # 安全打开ZIP文件
        for file_info in zip_ref.infolist():  # 遍历ZIP内每个文件
            try:
                # 跳过目录和非图片文件
                if file_info.is_dir():
                    continue

                filename = file_info.filename.lower()  # 统一转小写判断
                # 仅处理.jpg/.jpeg/.png文件
                if not (filename.endswith(('.jpg', '.png'))):
                    continue

                # 生成唯一文件名（UUID + 原扩展名）
                file_ext = os.path.splitext(filename)[1]  # 获取文件扩展名
                filename = os.path.splitext(filename)[0]  # 获取文件扩展名

                # 使用uuid生成唯一标识符
                unique_id = uuidUtil.getuuid()

                # 创建目标目录，如果不存在
                if not os.path.exists(target_dir + data_set_id):
                    os.makedirs(target_dir + data_set_id, exist_ok=True)

                # 创建新的文件名
                new_filename = f"{unique_id}{file_ext}"

                ocrTaskModel = OcrTaskModel()
                ocrTaskModel.name = filename
                ocrTaskModel.data_set_id = data_set_id
                # 指定保存的完整路径
                save_path = os.path.join(target_dir + data_set_id, new_filename)

                # 保存文件并重命名
                with zip_ref.open(file_info) as src_file, \
                        open(save_path, 'wb') as dst_file:
                    dst_file.write(src_file.read())

                ocrTaskModel.id = unique_id
                ocrTaskModel.data_type = 1

                ocrTaskModel.upload_image = data_set_id + '/' + new_filename
                ocrTaskModel.create_by = user_id
                ocrTaskModel.update_by = user_id

                # 查询模型
                trainModel = (TrainModel.query
                              .filter(TrainModel.create_by == user_id)
                              .filter(TrainModel.use_status == 1)
                              .first())

                if trainModel is not None:
                    ocrTaskModel.model_id = trainModel.id

                db.session.add(ocrTaskModel)
                db.session.commit()
                count += 1
            except Exception as e:
                print(f'数据集失败：{e}')

    # 调用识别接口
    print('启动异步任务')
    # 启动异步任务
    

    return {
        'suc_count': count
    }



def image_to_base64(image_path):
    """
    将图片文件转换为 Base64 编码字符串
    :param image_path: 图片文件的路径
    :return: Base64 编码字符串
    """
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"图片文件不存在: {image_path}")

    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
    return encoded_string



def update_by_excel(ocrTaskModel):
    user_id = tokenUtil.getUser().user_id
    try:
        ocrTaskModel = OcrTaskModel.query.filter_by(id=ocrTaskModel.id).first()
        if ocrTaskModel is None:
            return '任务不存在'
        # 新的列表，用于存储符合条件的output_json项
        matched_items = []
        all_scores_higher = False
        # 检查modify_the_value中的每一项是否在output_json中有对应的row和col完全相等
        for modify_item in ocrTaskModel.modify_the_value:
            for output_item in ocrTaskModel.output_json:
                # 检查row和col是否完全相等
                if modify_item['row'] == output_item['row'] and modify_item['col'] == output_item['col']:
                    output_item['text'] = modify_item['value']
                    output_item['score'] = 1.0
                    matched_items.append(output_item)
        value__all = ConfidenceModel().query.filter(ConfidenceModel.create_by == user_id).order_by(
            ConfidenceModel.conf_value.desc()).first()
        if value__all is not None:
            # 假设 value__all 是 ConfidenceModel 的实例，获取 conf_value
            highest_conf_value = float(value__all.conf_value)

            # 遍历 output_json 中的所有 output_item 并检查 score 是否都大于 highest_conf_value
            all_scores_higher = all(float(output_item['score']) > highest_conf_value
                                    for output_item in ocrTaskModel.output_json)

        if len(matched_items) != 0:
            OcrTaskModel.query.filter(OcrTaskModel.id == trainModel.task_id).update(
                {
                    OcrTaskModel.output_json: ocrTaskModel.output_json,
                    OcrTaskModel.rectifye_status: 0 if not all_scores_higher else 1
                }, synchronize_session='fetch')
            db.session.commit()

        return Result.success()
    except Exception as e:
        db.session.rollback()
        return Result.error(f"数据处理失败: {str(e)}")

def page(req):

    user_id = tokenUtil.getUser().user_id
    query = OcrTaskModel.query

    if req.name is not None:
        query = query.filter(OcrTaskModel.name == req.name)

    if req.status is not None:
        query = query.filter(OcrTaskModel.status == req.status)


    if req.rectifye_status is not None:
        query = query.filter(OcrTaskModel.rectifye_status == req.rectifye_status)


    if req.confirm_status is not None:
        query = query.filter(OcrTaskModel.confirm_status == req.confirm_status)

    if req.start_time is not None:
        query = query.filter(OcrTaskModel.create_time >= req.start_time)

    if req.end_time is not None:
        query = query.filter(OcrTaskModel.create_time <= req.end_time)

    if req.no_data_type is  None and req.data_type is  None:
        query = query.filter(OcrTaskModel.data_type == 0)

    if req.data_type is  not None:
        query = query.filter(OcrTaskModel.data_type == req.data_type)

    if req.data_set_id is  not None:
        query = query.filter(OcrTaskModel.data_set_id == req.data_set_id)
        # 添加关联查询
    
    query = query.join(DataSetModel, OcrTaskModel.data_set_id == DataSetModel.id, isouter=True)
    query = query.with_entities(OcrTaskModel, DataSetModel.name.label('data_set_name'))

    query = query.filter(OcrTaskModel.create_by ==  user_id)

    query = query.filter(OcrTaskModel.del_flag == 0)
    query = query.order_by(OcrTaskModel.create_time.desc())
    res = query.paginate(page=int(req.page), per_page=int(req.size), error_out=False)
    # 手动处理分页结果
    items = []
    for item in res.items:
        task_data = {c.key: getattr(item[0], c.key) for c in OcrTaskModel.__table__.columns}
        task_data.update({
            'create_time': item[0].create_time.strftime('%Y-%m-%d %H:%M:%S') if item[0].create_time else None,
            'update_time': item[0].update_time.strftime('%Y-%m-%d %H:%M:%S') if item[0].update_time else None,
            'data_set_name': item.data_set_name
        })
        items.append(task_data)
    
    
    return {
        'page': res.page,
        'pages': res.pages,
        'size': res.per_page,
        'total': res.total,
        'record': items
    }




def find(req):
    query = OcrTaskModel.query

    if req.id is not None:
        query = query.filter_by(id=req.id)
    query = query.filter(OcrTaskModel.del_flag == 0)
    query = query.order_by(OcrTaskModel.create_time)
    res = query.first()
    return res


def status_count():
    query = OcrTaskModel.query.with_entities(
        OcrTaskModel.status,
        db.func.count(OcrTaskModel.id)
    ).filter(
        OcrTaskModel.del_flag == 0
    ).group_by(
        OcrTaskModel.status
    )
    
    result = {
        "0": 0,  # 识别中
        "1": 0,  # 成功
        "2": 0   # 失败
    }
    
    for status, count in query.all():
        result[str(status)] = count
        
    return result


def get_unique_names():
    """
    获取所有不重复的name列表
    :return: 去重后的name列表
    """
    names = db.session.query(OcrTaskModel.name).filter(
        OcrTaskModel.del_flag == 0
    ).distinct().all()
    return [name[0] for name in names if name[0] is not None]


def update_data_set_id(task_id, data_set_id):
    """
    更新OcrTaskModel的data_set_id
    :param task_id: 任务ID
    :param data_set_id: 数据集ID
    :return: 更新结果
    """
    try:
        affected_rows = OcrTaskModel.query.filter_by(id=task_id).update({
            'data_set_id': data_set_id,
            'update_time': datetime.datetime.now()
        })
        db.session.commit()
        return affected_rows > 0
    except Exception as e:
        db.session.rollback()
        return False
