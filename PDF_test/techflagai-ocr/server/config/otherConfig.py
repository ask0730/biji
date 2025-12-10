# -*- coding: utf-8 -*-
import os
class OtherConfig:
    def __init__(self):
        self.reload_config()
    
    def reload_config(self):

        #必须指定，存储上传的图片和识别后的Excel
        self.FILE_PATH = os.getenv('OCR_FILE_PATH', 'D:/project_data/ocr/file/')
        
        #仅限于本地训练的模型，如果调用第三方即不需要
        self.MODEL_PATH = os.getenv('OCR_MODEL_PATH', 'D:/project_data/ocr/model')
        
        #仅限于本地训练的模型，如果调用第三方即不需要
        self.TRAIN_DATA = os.getenv('OCR_TRAIN_DATA', 'D:/project_data/ocr/train_data/')
        
        #仅限于本地训练的模型，如果调用第三方即不需要
        self.INFERENCE_PATH = os.getenv('OCR_INFERENCE_PATH', 'D:/project_data/ocr/inference/')

        # Redis配置
        self.REDIS_CONFIG = {
            'host': os.getenv('REDIS_HOST', '127.0.0.1'),
            'port': int(os.getenv('REDIS_PORT', '6379')),
            'password': os.getenv('REDIS_PASSWORD', '')
        }

        #如果没有指定数据集id，则使用默认的数据集id
        self.DEFAULT_DATASET_ID = os.getenv('DEFAULT_DATASET_ID', 'f47ac10b58cc4372a5670e02b2c3d479')

        self.OCR_OPEN_FILE_PATH = os.getenv('OCR_OPEN_FILE_PATH', 'D:/project_data/ocr/file/')
        
        self.STATIC_URL=os.getenv('STATIC_URL','127.0.0.1:8090/api/static/')
    
        
   
