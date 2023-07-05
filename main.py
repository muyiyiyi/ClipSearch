'''
Author: muyi
Date: 2023-07-02 14:56:09
LastEditors: muyi
LastEditTime: 2023-07-02 21:09:36
Description: 
'''
from PyQt5.QtWidgets import QApplication,QMessageBox
from PyQt5.QtCore import QLockFile,QDir
import sys
from src.Widget.FrameMain import MainWindow
import traceback
import os

if __name__ == '__main__':
    app = QApplication(sys.argv)
    lockfike_path = QDir.temp().absoluteFilePath("clip_search.lock")
    qtmplock = QLockFile(lockfike_path)
    if not qtmplock.tryLock(10):
        messagebox = QMessageBox()
        messagebox.setText("程序已经启动，请不要重复启动应用")
        messagebox.setDefaultButton(QMessageBox.StandardButton.Yes)
        messagebox.setStandardButtons(QMessageBox.StandardButton.Yes)
        ret = messagebox.exec()
        sys.exit(ret)
        
    try:
        app_path =  app.applicationDirPath()
        print("sys.excued",sys.executable)
        window = MainWindow(os.path.dirname(__file__))
        window.show()
    except Exception as e:
        traceback.print_exc()
    sys.exit(app.exec_())