'''
Author: muyi
Date: 2023-07-02 15:08:26
LastEditors: muyi
LastEditTime: 2023-07-02 21:07:48
Description: 
'''


import os
import threading
from PyQt5.QtGui import QDesktopServices,QPixmap
from PyQt5.QtWidgets import QMainWindow,QListWidgetItem,QMessageBox,QLabel,QDialog,QVBoxLayout,QMenu,QAction
from src.UI.ui_main import Ui_MainWindow
from src.ConfigTool import Config
from src.featureManager import CFeatureManager
from PyQt5.QtCore import QThread,Qt,QMetaObject,Q_ARG,pyqtSlot,QUrl,pyqtSignal,QEvent,QObject
from loguru import logger
import sys
from typing import List
from .FrameImgdir import ImageDirWidget


class ImageViewer(QDialog):
    def __init__(self, file_path):
        super().__init__()

        # 创建布局
        layout = QVBoxLayout()
        # 创建标签用于显示图片
        label = QLabel()
        label.setAlignment(Qt.AlignCenter)
        pixmap = QPixmap(file_path)
        label.setScaledContents(True)  # 设置内容按比例缩放
        label.setMaximumSize(400, 400)  # 设置最小大小
        label.setContentsMargins(0, 0, 0, 0)  # 设置边距为0

        label.setPixmap(pixmap)
        # 将标签添加到布局
        layout.addWidget(label)
        # 设置布局
        self.setLayout(layout)
        layout.setContentsMargins(0,0,0,0)
        # 设置窗口标题
        self.setWindowTitle("Image Viewer")

class MainWindow(QMainWindow,Ui_MainWindow):
    
    sig_rebuild_index = pyqtSignal(list)
    def __init__(self, application_dir:str) -> None:

        super().__init__()
        self.APP_DIR = application_dir
        logger.info(f"初始化窗口，程序启动路径={self.APP_DIR}")
        self.setupUi(self)
        self.init_params()
                
        self.imgdir_widget = ImageDirWidget(self.m_config.get_img_dirs())
        self.imgdir_widget.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.init_connection()
        self.current_search_text = ''

    
    """_summary_
    初始化参数
    """
    def init_params(self):
        # 1.读取配置文件设置相关路径
        self.m_config = Config(self.APP_DIR)
        img_sqlite_path = os.path.join(self.APP_DIR,'data','img.db')
        img_faiss_vector_path = os.path.join(self.APP_DIR,'data','img.index')
        img_model_path = self.m_config.get_model_path('img')
        txt_model_path = self.m_config.get_model_path('txt')
        if not os.path.isabs(img_model_path):
            img_model_path = os.path.join(self.APP_DIR,'data',img_model_path)
        if not os.path.isabs(txt_model_path):
            txt_model_path = os.path.join(self.APP_DIR,'data',txt_model_path)
        self.m_feature_manager = CFeatureManager(
            img_db_path=img_sqlite_path,
            img_onnx_path=img_model_path,
            txt_onnx_path=txt_model_path,
            faiss_index_path=img_faiss_vector_path
        )
        if not self.m_feature_manager._inited:
            sys.exit(0)

        self.m_backend_thread = QThread(self)
        self.m_feature_manager.moveToThread(self.m_backend_thread)

        

        self.m_backend_thread.start()

    def on_imgdir_changed(self,imgdir:List[str]):
        self.m_config.set_img_dir(imgdir)
    
    @pyqtSlot()
    def on_search_result(self):
        query_text = self.searchLine.text()
        if self.current_search_text != query_text:
            self.current_search_text = query_text # 记录下这一次查询的结果，防止下一次没有变化但是按下了回车
            #self.m_feature_manager.search(query_text)
            if query_text == '':
                self.result_listwidget.clear()
            else:
                QMetaObject.invokeMethod(self.m_feature_manager,'search',Qt.ConnectionType.QueuedConnection,Q_ARG('QString',query_text))
    
    @pyqtSlot(list)
    def on_get_result(self,img_results:List[str]):
        print(threading.currentThread())
        self.result_listwidget.clear()
        for img_path in img_results:
            item = QListWidgetItem(img_path)
            self.result_listwidget.addItem(item)

    @pyqtSlot(str)
    def on_query_changed(self,query_text:str):
        if query_text == '':
            self.result_listwidget.clear()

    @pyqtSlot()
    def on_click_result(self):
        item = self.result_listwidget.currentItem()
        if not item: return

        path = item.text()
        url = QUrl.fromLocalFile(path)
        QDesktopServices.openUrl(url)

    @pyqtSlot()
    def on_rebuild_index(self):
        msgbox = QMessageBox()
        msgbox.setText("是否重新构建图像目录下的特征索引信息")
        msgbox.setDefaultButton(QMessageBox.Cancel)
        msgbox.setStandardButtons(QMessageBox.Cancel | QMessageBox.Yes)
        ret = msgbox.exec()
        if ret == QMessageBox.Yes:
            self.sig_rebuild_index.emit(self.m_config.get_img_dirs())

    def eventFilter(self, obj: QObject, event: QEvent) -> bool:
        if obj == self.result_listwidget and event.type() == QEvent.KeyPress and event.key() == Qt.Key_Space:
            print("列表项目按下了空格")
            item = self.result_listwidget.currentItem()
            if item:
                path = item.text()
                if os.path.exists(path):
                    img_show_window = ImageViewer(path)
                    img_show_window.show()
                    img_show_window.exec()
        return super().eventFilter(obj,event)

    def show_resultlist_menu(self,pos):
        # 获取点击的项
        item = self.result_listwidget.itemAt(pos)
        img_path = item.text()
        img_dir = os.path.dirname(img_path)
        # 创建右键菜单
        context_menu = QMenu(self)

        # 创建打开图片的菜单项
        open_image_action = QAction("打开图片", self)
        open_image_action.triggered.connect(lambda: QDesktopServices.openUrl(QUrl(img_path)))

        # 创建打开图片所在目录的菜单项
        open_directory_action = QAction("打开图片所在目录", self)
        open_directory_action.triggered.connect(lambda: QDesktopServices.openUrl(QUrl(img_dir)))

        # 将菜单项添加到右键菜单
        context_menu.addAction(open_image_action)
        context_menu.addAction(open_directory_action)
        # 显示右键菜单
        context_menu.exec_(self.result_listwidget.mapToGlobal(pos))

    def init_connection(self):
        # 菜单栏点击添加图像目录：显示窗口。结束后如果保存了，触发目录变化的信号
        self.action_addfolder.triggered.connect(self.imgdir_widget.show)
        self.imgdir_widget.img_dir_changed.connect(self.on_imgdir_changed)

        # 搜索框输入后按下回车
        self.searchLine.returnPressed.connect(self.on_search_result)
        # 子线程搜索到了结果
        self.m_feature_manager.sig_get_result.connect(self.on_get_result)
        # 搜索框内容被删除了
        self.searchLine.textChanged.connect(self.on_query_changed)
        # 查找的图片结果双击打开图片
        self.result_listwidget.doubleClicked.connect(self.on_click_result)
        # 搜索结果的list重载事件。按下空格预览
        self.result_listwidget.installEventFilter(self)
        # 搜索结果的右键菜单 打开图片或所在目录
        self.result_listwidget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.result_listwidget.customContextMenuRequested.connect(self.show_resultlist_menu)
    

        # 确认重新构建索引
        self.action_rebuildIndex.triggered.connect(self.on_rebuild_index)
        self.sig_rebuild_index.connect(self.m_feature_manager.update_vector_record)
        


        # connect(ui_settingImgDir,SIGNAL(sig_saved_img_dirs(QList<QString>)),this, SLOT(slot_on_image_dir_changed(QList<QString>)));
        # connect(this,SIGNAL(rebuild_index(QList<QString>)),
        #         m_pfeatureManager,SLOT(update_image_record(QList<QString>))
        #         );

    def closeEvent(self, a0) -> None:
        logger.info("关闭窗口，停止后台线程")
        self.m_backend_thread.quit()
        self.m_backend_thread.wait()
        return super().closeEvent(a0)
