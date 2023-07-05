'''
Author: muyi
Date: 2023-06-30 21:54:10
LastEditors: muyi
LastEditTime: 2023-07-02 22:07:39
Description: 
'''
# import cv2
import onnxruntime
import os
from tqdm import tqdm
import time
import onnxruntime
from PIL import Image
import torch
from .utils import image_transform, tokenize
from loguru import logger
# 预处理图片
model_arch = "ViT-B-16" # 这里我们使用的是ViT-B-16规模，其他规模请对应修改
_MODEL_INFO = {
    "ViT-B-16": {
        "struct": "ViT-B-16@RoBERTa-wwm-ext-base-chinese",
        "input_resolution": 224
    },
    "ViT-L-14": {
        "struct": "ViT-L-14@RoBERTa-wwm-ext-base-chinese",
        "input_resolution": 224
    },
    "ViT-L-14-336": {
        "struct": "ViT-L-14-336@RoBERTa-wwm-ext-base-chinese",
        "input_resolution": 336
    },
    "ViT-H-14": {
        "struct": "ViT-H-14@RoBERTa-wwm-ext-large-chinese",
        "input_resolution": 224
    },
    "RN50": {
        "struct": "RN50@RBT3-chinese",
        "input_resolution": 224
    },
}


class CImageClipModel(object):
    _instance = None
    _inited = False

    def __new__(cls, *args, **kw):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, img_model_path:str, txt_model_path:str):
        if self._inited:
            return

        self.m_img_model_path = img_model_path
        self.m_txt_model_path = txt_model_path
        self.preprocess = image_transform(_MODEL_INFO[model_arch]['input_resolution'])
        
        self._inited = self.load_onnx_model()
    
    def load_onnx_model(self) ->bool:
        if not (os.path.exists(self.m_img_model_path) and os.path.exists(self.m_txt_model_path)):
            logger.error(f"模型文件{self.m_img_model_path}和{self.m_txt_model_path}不存在")
            return False
        
        try:
            sess_options = onnxruntime.SessionOptions()
            sess_options.log_severity_level = 3  # 设置日志级别为3 (ORT_LOGGING_LEVEL_ERROR)
            self.img_session = onnxruntime.InferenceSession(self.m_img_model_path,
                                                    sess_options=sess_options,
                                                    providers=["CPUExecutionProvider"])
            logger.info(f"加载图像端模型{self.m_img_model_path}成功")
            self.txt_session = onnxruntime.InferenceSession(self.m_txt_model_path,
                                                    sess_options=sess_options,
                                                    providers=["CPUExecutionProvider"])
            logger.info(f"加载文本端模型{self.m_txt_model_path}成功")
        except Exception as e:
            logger.error(f"加载ONNX模型失败，原因是{e}")
            return False
        return True

    def forward_img(self,img_path:str)->torch.Tensor:
        if not os.path.exists(img_path):
            return None
        
        image = self.preprocess(Image.open(img_path))
        image = image.unsqueeze(0)
        # 用ONNX模型计算图像侧特征
        image_features = self.img_session.run(["unnorm_image_features"], {"image":image.cpu().numpy() })[0] # 未归一化的图像特征

        # 归一化图像特征
        image_features = torch.tensor(image_features)
        image_features /= image_features.norm(dim=-1, keepdim=True)
        return image_features
    
    def forward_txt(self, txt:str):
        text = tokenize(txt, context_length=52)
        text_feature = self.txt_session.run(["unnorm_text_features"], {"text":text.cpu().numpy()})[0] # 未归一化的文本特征
        
        text_feature = torch.tensor(text_feature)
        text_feature = text_feature / text_feature.norm(dim=1, keepdim=True) # 归一化后的Chinese-CLIP文本特征，用于下游任务
        return text_feature