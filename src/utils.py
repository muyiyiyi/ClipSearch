'''
Author: muyi
Date: 2023-06-30 22:04:42
LastEditors: muyi
LastEditTime: 2023-07-02 16:22:41
Description: 
'''

from torchvision.transforms import Compose, ToTensor, Normalize, Resize, InterpolationMode
from .bert_tokenizer import FullTokenizer
import torch
import os
"""----------图像处理相关---------"""
def _convert_to_rgb(image):
    return image.convert('RGB')

def image_transform(image_size=224):
    transform = Compose([
        Resize((image_size, image_size), interpolation=InterpolationMode.BICUBIC),
      _convert_to_rgb,
      ToTensor(),
       Normalize((0.48145466, 0.4578275, 0.40821073), (0.26862954, 0.26130258, 0.27577711)),
    ])
    return transform

def get_all_images(path):
    file_list = []
    for root, dirs, files in os.walk(path):
        for file in files:
            if '.jpg' in file or '.png' in file:
                file_path = os.path.join(root, file)
                file_list.append(file_path)
    return file_list
"""------------文本处理相关----------------"""
_tokenizer = FullTokenizer()

# 原始版本是可以对多个句子计算，这里只需要输入一次，因此不需要处理texts是列表的清空
def tokenize(texts:str, context_length: int = 52) -> torch.LongTensor:

    # TODO :查询常量字符串 可以提前记录下来
    all_tokens = [_tokenizer.vocab['[CLS]']] + _tokenizer.convert_tokens_to_ids(_tokenizer.tokenize(texts))[
                                                        :context_length - 2] + [_tokenizer.vocab['[SEP]']]
    assert len(all_tokens) <= context_length
    expand_zeros = context_length - len(all_tokens)
    all_tokens.extend([0 for _ in range(expand_zeros)])
    result = torch.tensor([all_tokens])# torch.zeros(1, context_length, dtype=torch.long)
    return result