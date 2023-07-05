'''
Author: muyi
Date: 2023-06-30 20:39:18
LastEditors: muyi
LastEditTime: 2023-07-02 20:23:44
Description: 
'''
import typing
import onnxruntime
import os
import faiss
from .database import CImageInfoDB
from PyQt5.QtCore import QObject,pyqtSlot,pyqtSignal
from .clipmodel import CImageClipModel
from typing import List
import numpy as np
from .utils import get_all_images
from loguru import logger
import threading

class CFeatureManager(QObject):
    sig_get_result = pyqtSignal(list)

    def __init__(self, img_db_path:str, img_onnx_path:str, txt_onnx_path:str, faiss_index_path:str) -> None:
        super().__init__()
        self.m_img_database = CImageInfoDB(img_db_path)
        self.m_clip_model = CImageClipModel(img_onnx_path,txt_onnx_path)
        self._inited = self.m_clip_model._inited
        if not self._inited:
            logger.error("初始化模型信息失败")
            return
        
        self.vector_length = 512
        self.m_faiss_index_path = faiss_index_path
        if os.path.exists(faiss_index_path):
            self.m_faiss_index = faiss.read_index(faiss_index_path)
        else:
            self.m_faiss_index = faiss.IndexFlatL2(512)
        
        self.find_result_num = 5
    
    @pyqtSlot(str)
    def search(self, text:str):
        # "搜索最近"
        print("搜索函数运行在线程",threading.current_thread())
        print(f"搜索相册里可能与“{text}”有关的图像,结果如下：")
        txt_feature = self.m_clip_model.forward_txt(text)
        distance, index = self.m_faiss_index.search(txt_feature,self.find_result_num)
        result_path = []
        for idx in index:
            for i in idx:
                path = self.m_img_database.get_path_by_id(int(i))
                print(path)
                result_path.append(path)
        self.sig_get_result.emit(result_path)

    
    @pyqtSlot(list)
    def update_vector_record(self,image_dirs:List[str]):
        image_paths = []
        for image_dir in image_dirs:
            _path = get_all_images(image_dir)
            image_paths.extend(_path)

        # 移除现有的索引记录重新生成
        self.m_faiss_index.remove_ids(faiss.IDSelectorRange(0,self.m_faiss_index.ntotal))
        
        for image_id, image_path in enumerate(image_paths):
            exist_feature = self.m_img_database.insert_image(image_path,image_id, self.m_clip_model)
            
            if exist_feature:
                print("数据库里存在的feature",type(exist_feature),len(exist_feature))
                feature = np.frombuffer(exist_feature,dtype=np.float32)
                feature = np.reshape(feature, newshape=(1, 512))
                self.m_faiss_index.add(feature)
            else:
                feature = self.m_clip_model.forward_img(image_path)
                self.m_faiss_index.add(np.array(feature))
                print("不存在特征，手动推理",image_path)
        faiss.write_index(self.m_faiss_index,self.m_faiss_index_path)
