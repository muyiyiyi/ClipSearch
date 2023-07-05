'''
Author: muyi
Date: 2023-07-02 15:20:12
LastEditors: muyi
LastEditTime: 2023-07-02 19:34:53
Description: 
'''

import json
import os
from loguru import logger
from typing import List

class Config:
    def __init__(self,application_dir:str) -> None:
        self.APP_DIR = application_dir
        self.settingfile = os.path.join(self.APP_DIR,'data','setting.json')
        if not os.path.exists(self.settingfile):
            logger.error(f"配置文件{self.settingfile}不存在")
            
            self.cfg_dict = {
                    "description": "配置文件描述，onnx模型的路径，以data的相对路径描述，或者以绝对路径描述",
                    "img_model":"onnx/vit-b-16.img.fp16.onnx",
                    "txt_model":"onnx/vit-b-16.txt.fp16.onnx",
                    "img_dir":[]
            }

        else:
            self.cfg_dict = dict()
            with open(self.settingfile,'r') as f:
                self.cfg_dict = json.load(f)


    def get_model_path(self, text_or_img:str)->str:
        key = ''
        if text_or_img == 'txt':
            key = 'txt_model'
        elif text_or_img == 'img':
            key = 'img_model'
        else:
            logger.error(f"获取模型路径.类型只能是'text'或者'img',然而输入了'{text_or_img}'")
            return ''
        
        return self.cfg_dict.get(key,'')
    
    def set_model_path(self,path:str, text_or_img:str):
        if text_or_img != 'text' or text_or_img !='img':
            logger.error(f"设置模型路径.类型只能是'text'或者'img',然而输入了'{text_or_img}'")
        
        if not os.path.isabs(path): # 如果不是绝对路径
            abs_path = os.path.join(self.APP_DIR,path)
        else:
            abs_path = path
        
        if not os.path.exists(abs_path):
            logger.error(f"模型文件{path}不存在，无法设置")
        else:
            self.cfg_dict[f'{text_or_img}_model'] = path
            with open(self.settingfile, 'w') as f:
                json.dump(self.settingfile,f)

    def get_img_dirs(self):
        return self.cfg_dict.get('img_dir',[])
    
    def set_img_dir(self, img_dirs:List[str]):
        self.cfg_dict['img_dir'] = img_dirs
        with open(self.settingfile, 'w') as f:
                json.dump(self.cfg_dict,f,indent=2,ensure_ascii=False)
    
    def add_img_dir(self, img_dir:str):
        self.cfg_dict['img_dir'].append(img_dir)
        with open(self.settingfile, 'w') as f:
                json.dump(self.cfg_dict,f)