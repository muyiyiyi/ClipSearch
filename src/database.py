'''
Author: muyi
Date: 2023-06-30 20:45:31
LastEditors: muyi
LastEditTime: 2023-07-02 21:26:10
Description: 
'''
from sqlalchemy import create_engine, Column, Integer, String,BLOB
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base
import os
from hashlib import md5 as compute_md5
from .clipmodel import CImageClipModel
from loguru import logger
_Base = declarative_base() #<-元类
class CImageDBModel(_Base):
    __tablename__ = "image"

    faiss_id = Column(Integer)
    MD5 = Column(String(length=32),primary_key=True)
    path = Column(String(length=512))
    feature = Column(BLOB)


class CImageInfoDB(object):
    def __init__(self,sqlite_file_path:str):
        self.engine = create_engine(f"sqlite:///{sqlite_file_path}")
        _Base.metadata.create_all(self.engine)
        logger.info(f"初始化数据库文件 :{sqlite_file_path}")
        self.session = sessionmaker(bind=self.engine)()

    # def __del__(self):
        
    #     if self.session:
    #         if self.session.is_active:
    #             self.session.close()
    #             logger.info("关闭数据库链接")
        
    
    def get_path_by_id(self, query_id:int):
        query_result = self.session.query(CImageDBModel).where(CImageDBModel.faiss_id==query_id).first()
        img_path = f'不存在的id {query_id}'
        if query_result:
            img_path = query_result.path
        return img_path

    def insert_image(self,image_path:str,image_id:int, clip_model:CImageClipModel=None):
        if not os.path.exists(image_path):
            return
        # 计算md5值并查询是否有该条记录
        md5_value = ''
        with open(image_path,'rb') as f:
            byte_data = f.read()
            md5_value = compute_md5(byte_data).hexdigest()
        image_info = self.session.query(CImageDBModel).where(CImageDBModel.MD5==md5_value).first()
        # 数据库不存在该图片 直接新增一条记录
        query_feature = None
        if not image_info:
            img_feature = b''
            if clip_model:
                tensor_feature = clip_model.forward_img(image_path)
                img_feature = tensor_feature.numpy().tobytes()
            print("新的字节流",len(img_feature),type(img_feature))
            query_feature = img_feature
            new_row = CImageDBModel(
                path=image_path,faiss_id=image_id,MD5=md5_value,feature = img_feature
            )

            self.session.add(new_row)
            self.session.commit()
        else: 
            # 数据库存在图片 判断路径和id是不是匹配，不匹配的话更新
            exist_path = image_info.path
            exist_faiss_id = image_info.faiss_id
            query_feature = image_info.feature
            if exist_path != image_path or image_id != exist_faiss_id:
                image_info.path = image_path
                image_info.faiss_id = image_id
                
                self.session.commit()  # 提交更新
        return query_feature


if __name__ == "__main__":
    db = CImageInfoDB("data/img.db")
    path = db.get_path_by_id(0)
    print(path)