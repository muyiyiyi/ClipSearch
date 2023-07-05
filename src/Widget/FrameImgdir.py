'''
Author: muyi
Date: 2023-07-02 17:51:27
LastEditors: muyi
LastEditTime: 2023-07-02 19:29:49
Description: 
'''
import typing
from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import QMainWindow,QMessageBox, QListWidgetItem,QFileDialog
from src.UI.ui_main import Ui_MainWindow
from src.ConfigTool import Config
from src.featureManager import CFeatureManager
from PyQt5.QtCore import QThread,pyqtSignal,Qt
from loguru import logger
import os
from typing import List


from src.UI.ui_imgsetting import Ui_setImageDirWidget

class ImageDirWidget(Ui_setImageDirWidget):
    img_dir_changed = pyqtSignal(list)
    
    def __init__(self,image_dirs:List[str]) -> None:
        super().__init__()
        self.setupUi(self)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowCloseButtonHint)

        self.m_image_dirs = image_dirs
        self.set_list_widget(self.m_image_dirs)
        self.init_connection()
        self.item_changed = False  # 界面显示过程中是否编辑了 方便判断关闭窗口的时候是否保存

    def set_list_widget(self,image_dirs:List[str]) -> None:
        for img_dir in image_dirs:
            if not os.path.exists(img_dir):
                continue
            item = QListWidgetItem(img_dir)
            self.imgDirListWidget.addItem(item)


    
    def init_connection(self):
        self.cancel_btn.clicked.connect(self.on_cancel_click)
        self.save_btn.clicked.connect(self.on_save_click)
        self.add_btn.clicked.connect(self.on_add_click)
        self.del_btn.clicked.connect(self.on_del_click)

    def check_is_subdir(self,dir):
        cur_imgdirs = [self.imgDirListWidget.item(i).text() for i in range(self.imgDirListWidget.count())]
        for imgdir in cur_imgdirs:
            common_path = os.path.commonpath([imgdir, dir])
            if common_path == imgdir:
                return True, imgdir
        return False, None
    
    def on_add_click(self):
        dirName = QFileDialog.getExistingDirectory(self,"选择图片目录","/home/")
        if dirName:
            is_subdir, common_parent = self.check_is_subdir(dirName)
            if is_subdir:
                messagebox = QMessageBox()
                messagebox.setText(f"选择的路径{dirName}是现有目录{common_parent}的子目录，无需重复添加")
                messagebox.setDefaultButton(QMessageBox.StandardButton.Yes)
                messagebox.setStandardButtons(QMessageBox.StandardButton.Yes)
                ret = messagebox.exec()
            else:
                self.item_changed = True # 表示已经选择了某个目录，发生了变化
                item = QListWidgetItem(dirName)
                self.imgDirListWidget.addItem(item)
            

    def on_del_click(self):
        print(self.imgDirListWidget.count())
        row = self.imgDirListWidget.currentRow()
        print("选择删除行",row)
        if row >= 0:
            print('删除item')
            self.imgDirListWidget.takeItem(row)
            self.item_changed = True
        print(self.imgDirListWidget.count())

    def on_cancel_click(self):
        # 恢复到默认
        if self.item_changed:
            self.item_changed = False
            self.imgDirListWidget.clear()  # 清空列表
            self.set_list_widget(self.m_image_dirs) # 重新设置为默认值
        self.close()
    
    def on_save_click(self):
        # 保存下记录 发出信号

        # 更新存储的目录
        
        if self.item_changed:
            self.m_image_dirs = [self.imgDirListWidget.item(i).text() for i in range(self.imgDirListWidget.count())]
            self.img_dir_changed.emit(self.m_image_dirs)  # 发出变化的信号。主界面 更改
        self.close()
    
    