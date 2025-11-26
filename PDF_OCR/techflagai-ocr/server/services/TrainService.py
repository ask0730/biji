# -*- coding: utf-8 -*-
import os
import random
import shutil

from PIL import Image
from ruamel.yaml import YAML

from api import create_app, db
from models.ConfidenceModel import ConfidenceModel
from models.OcrTaskModel import OcrTaskModel
from models.TrainModel import TrainModel
from utils import uuidUtil, tokenUtil, modelUtil
from utils.result import Result
import traceback
from config.otherConfig import OtherConfig

config = OtherConfig()


def find(req):
    target_dir = config.MODEL_PATH
    yaml = YAML()
    res = TrainModel.query.filter(TrainModel.id == req.id).first()
    res = modelUtil.model_to_dict(res, date_format=True)
    # 加载YAML文件
    with open(target_dir + res['rec_yml'], 'r', encoding='utf-8') as file:
        data = yaml.load(file)

    res['epoch_num'] = data['Global']['epoch_num']
    res['learning_rate'] = data['Optimizer']['lr']['learning_rate']
    res['batch_size_per_card'] = data['Eval']['loader']['batch_size_per_card']

    return res


def save(trainModel):
    target_dir = config.MODEL_PATH
    yaml = YAML()
    user_id = tokenUtil.getUser()

    # 使用uuid生成唯一标识符
    unique_id = uuidUtil.getuuid()

    # 创建目标目录，如果不存在
    if not os.path.exists(target_dir + unique_id):
        os.makedirs(target_dir + unique_id, exist_ok=True)

        shutil.copytree(target_dir + 'temp', target_dir + unique_id + '/rec')
        trainModel.rec_yml = unique_id + '/rec/ch_PP-OCRv4_rec.yml'

    # 加载YAML文件
    with open(target_dir + trainModel.rec_yml, 'r', encoding='utf-8') as file:
        data = yaml.load(file)

    # 模型位置
    data['Global']['save_model_dir'] = f'./producte_line/{unique_id}/rec/output'
    data['Global']['save_res_path'] = f'./producte_line/{unique_id}/rec/output/predicts_ppocrv3.txt'
    data['Global']['character_dict_path'] = f'producte_line/{unique_id}/rec/dict.txt'

    # 训练集
    data['Train']['dataset']['data_dir'] = f'./train_data'
    data['Train']['dataset']['label_file_list'] = [
        f'./producte_line/{unique_id}/rec/train.txt'
    ]
    # 验证集
    data['Eval']['dataset']['data_dir'] = f'./train_data'
    data['Eval']['dataset']['label_file_list'] = [
        f'./producte_line/{unique_id}/rec/val.txt'
    ]

    # 将修改后的数据写回YAML文件
    with open(target_dir + trainModel.rec_yml, 'w', encoding='utf-8') as file:
        yaml.dump(data, file)

    trainModel.id = unique_id

    trainModel.create_by = user_id
    trainModel.update_by = user_id
    db.session.add(trainModel)
    db.session.commit()
    # 调用识别接口
    return {
        'id': trainModel.id
    }


def update(trainModel):
    user_id = tokenUtil.getUser()
    update_data = {
        TrainModel.name: trainModel.name,
        TrainModel.producte_line: trainModel.producte_line,
        TrainModel.mission_scene: trainModel.mission_scene,
        TrainModel.customize: trainModel.customize,
        TrainModel.status: trainModel.status,
        TrainModel.train_set: trainModel.train_set,
        TrainModel.val_set: trainModel.val_set,
        TrainModel.step: trainModel.step,
        TrainModel.update_by: user_id
    }
    update_data = {k: v for k, v in update_data.items() if v is not None}

    TrainModel.query.filter(TrainModel.id == trainModel.id).update(
        update_data, synchronize_session='fetch')
    db.session.commit()
    # 调用识别接口
    return {
        'id': trainModel.id
    }


def data_check(req):
    if req.data_set_id is None:
        return Result.error('数据集错误')
    # 更新切分
    user = tokenUtil.getUser()
    # Extract user_id as string from the user object
    user_id = str(user.user_id)  # Convert user_id to string
    trainModel = TrainModel.query.filter(TrainModel.id == req.id).first()
    if trainModel is None:
        trainModel.data_set_status = -1
        db.session.commit()
        return Result.error(msg='未找到该模型')

    if trainModel.data_set_status == 1:
        return Result.error('请勿重复校验')

    TRAIN_DATA = config.TRAIN_DATA
    MODEL_PATH = config.MODEL_PATH
    INFERENCE_PATH = config.INFERENCE_PATH
    FILE_PATH = config.FILE_PATH
    labels_file_path = os.path.join(TRAIN_DATA, user_id, 'labels.txt')

    trainModel.data_set_id = req.data_set_id
    
    # if True:
    try:
        # 查询数据集
        status__all = (OcrTaskModel.query.filter(OcrTaskModel.data_set_id == req.data_set_id)
                       # .filter(OcrTaskModel.status == 1)
                       .filter(OcrTaskModel.rectifye_status == 1)
                       .all())

        if status__all is None  or len(status__all) == 0:
            return Result.error('当前数据集暂未有纠正过的数据')
        
        trainModel.data_set_status = 1
        db.session.commit()
        # 开始切分
        output_dir = os.path.join(TRAIN_DATA, req.id, 'images')
        labels_file_path = os.path.join(TRAIN_DATA, req.id, 'labels.txt')
        model_path_set = os.path.join(MODEL_PATH, req.id) 
        
        # 确保目录存在
        if not os.path.exists(model_path_set):
            os.makedirs(os.path.join(model_path_set, 'rec'), exist_ok=True)
            
        labels = []
        # 检查输出目录是否存在，若存在则删除
        if os.path.exists(output_dir):
            shutil.rmtree(output_dir)  # 删除目录及其所有内容
        os.makedirs(output_dir, exist_ok=True)  # exist_ok=True 避免目录已存在时报错

        with open(labels_file_path, 'w') as file:
            pass  # 创建了一个空文件

        for ocrTaskModel in status__all:
            print(f'ocrTaskModel.output_image:{ocrTaskModel.output_image}')
            image_path = FILE_PATH + ocrTaskModel.output_image
            if not os.path.exists(image_path):
                continue

            image = Image.open(image_path)

            for matched_item in ocrTaskModel.output_json:
                left, upper, right, lower = matched_item['box']
                width = right - left
                height = lower - upper

                # 计算新尺寸
                new_width = width * 0.99
                new_height = height * 0.99

                # 计算新的坐标，保持中心点不变
                new_left = left + (width - new_width) / 2
                new_upper = upper + (height - new_height) / 2
                new_right = new_left + new_width
                new_lower = new_upper + new_height

                # 使用box坐标切割图片
                cropped_image = image.crop([new_left, new_upper, new_right, new_lower])
                
                # 如果图像是RGBA模式，转换为RGB模式
                if cropped_image.mode == 'RGBA':
                    cropped_image = cropped_image.convert('RGB')

                # 保存切割后的图片到指定路径
                images = str(req.id) + '/images/' + ocrTaskModel.id + str(matched_item['row'][0]) + '_' + str(
                    matched_item['row'][1]) + '_' + str(matched_item['col'][0]) + '_' + str(matched_item['col'][1]) + '.jpg'
                output_image_path = TRAIN_DATA + images

                cropped_image.save(output_image_path)
                labels.append(f"{images}\t{matched_item['text']}")
            # 将标签数据写入 labels.txt 文件
            with open(labels_file_path, 'a', encoding='utf-8') as file:
                for label in labels:
                    file.write(f"{label}\n")


        result_dict = {}
        # 查询 数据集状态
        if os.path.exists(labels_file_path):
            with open(labels_file_path, 'r', encoding='utf-8') as file:
                labels = file.readlines()
                for item in labels:
                    item = item.strip()
                    # 使用split函数根据空格分割字符串，第一个部分作为键，剩下的作为值
                    parts = item.split('\t', 1)  # 限制只分割一次
                    if len(parts) == 2:  # 确保分割成功
                        key, value = parts
                        if os.path.exists(TRAIN_DATA + key) and os.path.isfile(
                                TRAIN_DATA + key):
                            result_dict[key] = value

        else:
            trainModel.data_set_status = -1
            db.session.commit()
            return Result.error('暂无数据集')

        # if len(result_dict) < 100:
        #     trainModel.data_set_status = 0
        #     db.session.commit()
        #     return Result.error('数据集小于100张')

        keys = list(result_dict.keys())
        random.shuffle(keys)  # 随机打乱键的顺序
        split_idx = int(len(keys) * (req.train_set * 0.01))
        dict1_keys = keys[:split_idx]
        dict2_keys = keys[split_idx:]

        train_set_data = {k: result_dict[k] for k in dict1_keys}
        val_set_data = {k: result_dict[k] for k in dict2_keys}
        dict_txt = list(set(char for value in result_dict.values() for char in value))
        # 读取元字典
        with open(f'{TRAIN_DATA}/dict.txt', 'r', encoding='utf-8') as file:
            original_chars = [line.strip() for line in file]  # 关键修改：用 strip() 去除换行符

        # 2. 找出新增字符（不在原字典中的）
        existing_chars_set = set(original_chars)
        new_chars = [char for char in dict_txt if char not in existing_chars_set]

        # 3. 如果有新字符，才更新文件
        if new_chars:
            # 合并（原始顺序 + 新增字符）
            original_chars = original_chars + new_chars  # 或者 new_chars_sorted 如果需要排序

        train_list = []
        val_list = []

        with open(model_path_set + '/rec/train.txt', 'w', encoding='utf-8') as f:
            for k, value in train_set_data.items():
                f.write(f'{k}\t{value}\n')
                train_list.append(k)

        with open(model_path_set + '/rec/val.txt', 'w', encoding='utf-8') as f:
            for k, value in val_set_data.items():
                f.write(f'{k}\t{value}\n')
                val_list.append(k)

        with open(model_path_set + '/rec/dict.txt', 'w', encoding='utf-8') as file:
            for dict in original_chars:
                file.write(f"{dict}\n")

    except Exception as e:
        
        error_msg = f'数据校验异常:\n类型: {type(e).__name__}\n详情: {str(e)}\n堆栈: {traceback.format_exc()}'
        print(error_msg)  # 控制台输出
        # 如果有日志系统，建议同时写入日志
        # logger.error(error_msg)
        trainModel.data_set_status = -1
        db.session.commit()
        return Result.error(str(e))

    trainModel.train_set = req.train_set
    trainModel.val_set = req.val_set
    trainModel.data_set_status = 2
    db.session.commit()

    
    res = {
        'train_num': len(train_list),  # 训练集总数
        'val_num': len(val_list),      # 验证集总数
        'train_list': train_list[:10], # 训练集前10条
        'val_list': val_list[:10]      # 验证集前10条
    }
    return Result.success(res)


def data_check_data(req):
    user_id = tokenUtil.getUser()
    trainModel = TrainModel.query.filter(TrainModel.id == req.id).first()
    if trainModel is None:
        trainModel.data_set_status = -1
        db.session.commit()
        return Result.error(msg='未找到该模型')

    if trainModel.data_set_status == 1:
        return Result.error('请勿重复校验')

    TRAIN_DATA = config.TRAIN_DATA
    MODEL_PATH = config.MODEL_PATH
    with open(MODEL_PATH + req.id + '/rec/train.txt', "r", encoding="utf-8") as f:
        train_list = [f'{item.split()[0]}' for item in f.read().splitlines()]

    with open(MODEL_PATH + req.id + '/rec/val.txt', "r", encoding="utf-8") as f:
        val_list = [f'{item.split()[0]}' for item in f.read().splitlines()]
    random.shuffle(train_list)  # 打乱列表顺序
    train_size = min(10, len(train_list))  # 自动确定抽样数量

    random.shuffle(val_list)  # 打乱列表顺序
    val_size = min(10, len(val_list))  # 自动确定抽样数量

    res = {
        'train_num': len(train_list),
        'val_num': len(val_list),
        'train_list': train_list[:train_size],
        'val_list': val_list[:val_size],
    }
    return Result.success(res)


def update_yml(trainModel):
    target_dir = config.MODEL_PATH
    yaml = YAML()

    query = trainModel.query.filter_by(id=trainModel.id)
    res = query.first()
    if res is None:
        return Result.error(msg='未找到该模型')

    # 加载YAML文件
    with open(target_dir + res.rec_yml, 'r', encoding='utf-8') as file:
        data = yaml.load(file)

    if trainModel.use_gpu is not None:
        data['Global']['use_gpu'] = trainModel.use_gpu

    if trainModel.pretrained_model is not None:
        data['Global']['pretrained_model'] = trainModel.pretrained_model

    if trainModel.pretrained_model is not None:
        data['Global']['character_dict_path'] = trainModel.character_dict_path

    if trainModel.epoch_num is not None:
        data['Global']['epoch_num'] = trainModel.epoch_num

    if trainModel.learning_rate is not None:
        data['Optimizer']['lr']['learning_rate'] = trainModel.learning_rate

    if trainModel.batch_size_per_card is not None:
        data['Eval']['loader']['batch_size_per_card'] = trainModel.batch_size_per_card

    # 将修改后的数据写回YAML文件
    with open(target_dir + res.rec_yml, 'w', encoding='utf-8') as file:
        yaml.dump(data, file)

    # 调用识别接口
    return Result.success()


def cutting_img(trainModel):
    try:
        TRAIN_DATA = config.TRAIN_DATA
        FILE_PATH = config.FILE_PATH

        query = OcrTaskModel.query.filter_by(id=trainModel.task_id)
        ocrTaskModel = query.first()
        if not ocrTaskModel:
            return Result.error("未找到对应的OCR任务")

        # 修改获取用户ID的方式
        user = tokenUtil.getUser()
        if not user or not hasattr(user, 'user_id'):
            return Result.error("无效的用户信息")
        user_id = user.user_id  # 获取实际的用户ID值

        # 新的列表，用于存储符合条件的output_json项
        matched_items = []
        all_scores_higher = False
        # 检查modify_the_value中的每一项是否在output_json中有对应的row和col完全相等
        for modify_item in trainModel.modify_the_value:
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

        return Result.success(matched_items)
    except Exception as e:
        db.session.rollback()
        return Result.error(f"图片切割处理失败: {str(e)}")
