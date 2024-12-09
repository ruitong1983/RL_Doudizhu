# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'MainWindow.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(440, 395)
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(9)
        font.setBold(True)
        font.setItalic(False)
        font.setWeight(75)
        Form.setFont(font)
        self.WinRate = QtWidgets.QLabel(Form)
        self.WinRate.setGeometry(QtCore.QRect(240, 180, 171, 61))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.WinRate.setFont(font)
        self.WinRate.setAlignment(QtCore.Qt.AlignCenter)
        self.WinRate.setObjectName("WinRate")
        self.InitCard = QtWidgets.QPushButton(Form)
        self.InitCard.setGeometry(QtCore.QRect(60, 330, 121, 41))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        self.InitCard.setFont(font)
        self.InitCard.setStyleSheet("")
        self.InitCard.setObjectName("InitCard")
        # 创建一个标签来显示用户手中的牌
        self.UserHandCards = QtWidgets.QLabel(Form)
        # 设置标签的位置和大小
        self.UserHandCards.setGeometry(QtCore.QRect(10, 260, 421, 41))
        # 创建一个字体对象
        font = QtGui.QFont()
        # 设置字体的大小
        font.setPointSize(14)
        # 为标签设置字体
        self.UserHandCards.setFont(font)
        # 设置标签的文本对齐方式为居中
        self.UserHandCards.setAlignment(QtCore.Qt.AlignCenter)
        # 设置标签的名称
        self.UserHandCards.setObjectName("UserHandCards")
        self.LPlayer = QtWidgets.QFrame(Form)
        self.LPlayer.setGeometry(QtCore.QRect(10, 80, 201, 61))
        self.LPlayer.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.LPlayer.setFrameShadow(QtWidgets.QFrame.Raised)
        self.LPlayer.setObjectName("LPlayer")
        self.LPlayedCard = QtWidgets.QLabel(self.LPlayer)
        self.LPlayedCard.setGeometry(QtCore.QRect(0, 0, 201, 61))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.LPlayedCard.setFont(font)
        self.LPlayedCard.setAlignment(QtCore.Qt.AlignCenter)
        self.LPlayedCard.setObjectName("LPlayedCard")
        self.RPlayer = QtWidgets.QFrame(Form)
        self.RPlayer.setGeometry(QtCore.QRect(230, 80, 201, 61))
        font = QtGui.QFont()
        font.setPointSize(16)
        self.RPlayer.setFont(font)
        self.RPlayer.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.RPlayer.setFrameShadow(QtWidgets.QFrame.Raised)
        self.RPlayer.setObjectName("RPlayer")
        self.RPlayedCard = QtWidgets.QLabel(self.RPlayer)
        self.RPlayedCard.setGeometry(QtCore.QRect(0, 0, 201, 61))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.RPlayedCard.setFont(font)
        self.RPlayedCard.setAlignment(QtCore.Qt.AlignCenter)
        self.RPlayedCard.setObjectName("RPlayedCard")
        self.Player = QtWidgets.QFrame(Form)
        self.Player.setGeometry(QtCore.QRect(40, 180, 171, 61))
        self.Player.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.Player.setFrameShadow(QtWidgets.QFrame.Raised)
        self.Player.setObjectName("Player")
        self.PredictedCard = QtWidgets.QLabel(self.Player)
        self.PredictedCard.setGeometry(QtCore.QRect(0, 0, 171, 61))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.PredictedCard.setFont(font)
        self.PredictedCard.setAlignment(QtCore.Qt.AlignCenter)
        self.PredictedCard.setObjectName("PredictedCard")
        self.ThreeLandlordCards = QtWidgets.QLabel(Form)
        self.ThreeLandlordCards.setGeometry(QtCore.QRect(140, 10, 161, 41))
        font = QtGui.QFont()
        font.setPointSize(16)
        self.ThreeLandlordCards.setFont(font)
        self.ThreeLandlordCards.setAlignment(QtCore.Qt.AlignCenter)
        self.ThreeLandlordCards.setObjectName("ThreeLandlordCards")
        self.Stop = QtWidgets.QPushButton(Form)
        self.Stop.setGeometry(QtCore.QRect(260, 330, 111, 41))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        self.Stop.setFont(font)
        self.Stop.setStyleSheet("")
        self.Stop.setObjectName("Stop")

        self.retranslateUi(Form)
        self.InitCard.clicked.connect(Form.init_cards)
        self.Stop.clicked.connect(Form.stop)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        """
        更新界面文本，用于动态加载语言或主题。

        该方法使用Qt的翻译框架来设置窗口和控件的标题和文本。它确保应用程序可以支持多语言环境，
        并在运行时根据需要更改语言设置。

        参数:
        - Form: QWidget对象，代表应用程序的主窗口或表单。

        返回值:
        无
        """
        # 创建一个翻译器对象，用于从资源中查找和检索翻译文本
        _translate = QtCore.QCoreApplication.translate

        # 设置窗口标题，使用翻译后的文本
        Form.setWindowTitle(_translate("Form", "DouZero for 欢乐斗地主"))

        # 为胜率标签设置文本，初始显示为"--%"
        self.WinRate.setText(_translate("Form", "胜率：--%"))

        # 为开始按钮设置文本
        self.InitCard.setText(_translate("Form", "开始"))

        # 为手牌标签设置文本
        self.UserHandCards.setText(_translate("Form", "手牌"))

        # 为上家出牌区域标签设置文本
        self.LPlayedCard.setText(_translate("Form", "上家出牌区域"))

        # 为下家出牌区域标签设置文本
        self.RPlayedCard.setText(_translate("Form", "下家出牌区域"))

        # 为AI出牌区域标签设置文本
        self.PredictedCard.setText(_translate("Form", "AI出牌区域"))

        # 为三张底牌标签设置文本
        self.ThreeLandlordCards.setText(_translate("Form", "三张底牌"))

        # 为停止按钮设置文本
        self.Stop.setText(_translate("Form", "停止"))

