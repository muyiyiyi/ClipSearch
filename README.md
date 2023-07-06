
# ClipSearch
基于cn-clip模型封装的本地图片搜索工具


!!!   
半成品项目，bug很多。

# 使用说明
`python main.py`即可运行，在`data/onnx/`目录下存放好模型文件即可。img.db文件和img.index可以先删除。在界面上选择相册目录或者配置文件里指定，然后菜单栏生成索引即可生成db和index文件，然后就可以在主界面通过文字搜索匹配图片了。

# 模型
模型与预处理代码来自[Chines-CLIP](https://github.com/OFA-Sys/Chinese-CLIP)项目，没有二次微调。参考 https://github.com/OFA-Sys/Chinese-CLIP/blob/master/deployment.md 即可生成对应的onnx模型。或者直接下载转换好的`Vit-B-16`模型，链接如下：
+ [谷歌云盘](https://drive.google.com/drive/folders/1Yye2ab8T4yNNq2zNhgQzpNJ2eieS-ukX?usp=sharing) 
+ [百度云盘](https://pan.baidu.com/s/1tFRLghHVFajFIdRviviuIA) 提取码: edvn

注: 因为现在手上没有N卡的机器，因此代码中的onnx和faiss都是使用cpu版本。

# 问题
1. 经过测试内存占用，程序启动后内存占用在400~600MB左右，主要占用在clipmodel.py的加载模型部分，`load_onnx_model`加载模型后占用内存较大。但每次搜索调用`forward_txt`，即执行onnxruntime的推理调用后，内存会持续增长，每次搜索会增长200MB内存，多次调用后稳定在1200MB左右。问题有待解决

2. 事实上最开始这个项目是使用C++ Qt实现的，但是开发完成后，发现C++版本调用onnx推理的特征与使用python推理结果有出入，而最终使用faiss进行搜索的结果和python搜索的结果完全不一致，检查了预处理步骤还是没有找到原因，等待排查问题。