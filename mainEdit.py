# -*- coding: utf-8 -*-

# Created by: Raf

import os
import sys
# import time
import threading
from datetime import time

import cv2
import pyautogui

from PyQt5 import QtGui, QtWidgets, QtCore
from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsItem, QGraphicsPixmapItem, QInputDialog, QMessageBox
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import QTime, QEventLoop
from MainWindowUI import Ui_Form

from douzero.env.game import GameEnv
from douzero.evaluation.deep_agent import DeepAgent
import numpy as np

EnvCard2RealCard = {3: '3', 4: '4', 5: '5', 6: '6', 7: '7',
                    8: '8', 9: '9', 10: 'T', 11: 'J', 12: 'Q',
                    13: 'K', 14: 'A', 17: '2', 20: 'X', 30: 'D'}

RealCard2EnvCard = {'3': 3, '4': 4, '5': 5, '6': 6, '7': 7,
                    '8': 8, '9': 9, 'T': 10, 'J': 11, 'Q': 12,
                    'K': 13, 'A': 14, '2': 17, 'X': 20, 'D': 30}

AllEnvCard = [3, 3, 3, 3, 4, 4, 4, 4, 5, 5, 5, 5, 6, 6, 6, 6, 7, 7, 7, 7,
              8, 8, 8, 8, 9, 9, 9, 9, 10, 10, 10, 10, 11, 11, 11, 11, 12,
              12, 12, 12, 13, 13, 13, 13, 14, 14, 14, 14, 17, 17, 17, 17, 20, 30]

AllCards = ['rD', 'bX',
            's2', 'h2', 'c2', 'd2', 'sA', 'hA', 'cA', 'dA',
            'sK', 'hK', 'cK', 'dK', 'sQ', 'hQ', 'cQ', 'dQ', 'sJ', 'hJ', 'cJ', 'dJ',
            'sT', 'hT', 'cT', 'dT', 's9', 'h9', 'c9', 'd9', 's8', 'h8', 'c8', 'd8',
            's7', 'h7', 'c7', 'd7', 's6', 'h6', 'c6', 'd6', 's5', 'h5', 'c5', 'd5',
            's4', 'h4', 'c4', 'd4', 's3', 'h3', 'c3', 'd3']
# 黑桃:S-Spade | 红桃:H-Heart | 梅花:C-Club | 方块:D-Diamond

class MyPyQT_Form(QtWidgets.QWidget, Ui_Form):
    def __init__(self):
        super(MyPyQT_Form, self).__init__()
        self.setupUi(self)
        self.setWindowFlags(QtCore.Qt.WindowMinimizeButtonHint |    # 使能最小化按钮
                            QtCore.Qt.WindowCloseButtonHint |       # 使能关闭按钮
                            QtCore.Qt.WindowStaysOnTopHint)         # 窗体总在最前端
        self.setFixedSize(self.width(), self.height())              # 固定窗体大小
        self.setWindowIcon(QIcon('pics/favicon.ico'))
        window_pale = QtGui.QPalette()
        window_pale.setBrush(self.backgroundRole(), QtGui.QBrush(QtGui.QPixmap("pics/bg.png")))
        self.setPalette(window_pale)

        # 获取屏幕的分辨率，计算窗口右下角的位置
        screen_geometry = QtWidgets.QApplication.desktop().screenGeometry()
        screen_width = screen_geometry.width()
        screen_height = screen_geometry.height()
        x = screen_width - self.width()
        y = screen_height - self.height()
        self.move(x, y-120)                             # 设置窗口移动的位置

        self.Players = [self.RPlayer, self.Player, self.LPlayer]
        self.counter = QTime()

        # 屏幕检测参数设定
        self.MyHandCardsConfidence = 0.97               # 我的手牌的置信度
        self.OtherCardsConfidence = 0.95                # 別人的牌的置信度
        self.playFlagConfidence = 0.80                  # 检测出牌区域是否有牌，检测牌的白块的置信度
        self.passFlagConfidence = 0.80                  # 检测Pass标志的置信度
        self.LandlordFlagConfidence = 0.45              # 检测地主标志的置信度
        self.ThreeLandlordCardsConfidence = 0.80        # 地主牌的置信度
        self.WaitTime = 0.5                             # 等待状态稳定延时
        self.MyFilter = 40                              # 我的牌检测结果过滤参数
        self.OtherFilter = 25                           # 别人的牌检测结果过滤参数

        # 检测屏幕的坐标
        self.MyHandCardsPos = (350, 1050, 1700, 200)        # 我的截图区域
        self.LPlayedCardsPos = (600, 550, 700, 250)         # 左边截图区域
        self.RPlayedCardsPos = (1250, 550, 700, 250)        # 右边截图区域
        self.MPlayedCardsPos = (950, 750, 700, 250)         # 我的出牌区域
        self.LandlordFlagPos = [(2200, 400, 200, 200), (0, 1150, 200, 200),
                                (200, 400, 200, 200)]       # 地主标志截图区域(右-我-左)
        self.ThreeLandlordCardsPos = [(1100, 50, 100, 150), (1200, 50, 100, 150),
                                      (1300, 50, 100, 150)]  # 地主底牌截图区域
        # 信号量
        # self.shouldExit = 0                 # 通知上一轮记牌结束
        # self.canRecord = threading.Lock()   # 开始记牌

        # 模型路径
        self.card_play_model_path_dict = {
            'landlord': "baselines/douzero_WP/landlord.ckpt",
            'landlord_up': "baselines/douzero_WP/landlord_up.ckpt",
            'landlord_down': "baselines/douzero_WP/landlord_down.ckpt"
        }

    def init_display(self):
        self.WinRate.setText("胜率：--%")
        self.InitCard.setText("开始")
        self.UserHandCards.setText("手牌")
        self.LPlayedCard.setText("上家出牌区域")
        self.RPlayedCard.setText("下家出牌区域")
        self.PredictedCard.setText("AI出牌区域")
        self.ThreeLandlordCards.setText("三张底牌")
        for player in self.Players:
            player.setStyleSheet('background-color: rgba(255, 0, 0, 0);')

    def init_cards(self):
        # 玩家手牌，其他玩家出牌，其他玩家手牌（整副牌减去玩家手牌，后续再减掉历史出牌）
        self.user_hand_cards_real = ""
        self.user_hand_cards_env = []
        self.other_played_cards_real = ""
        self.other_played_cards_env = []
        self.other_hand_cards = []
        # 三张地主的底牌
        self.three_landlord_cards_real = ""
        self.three_landlord_cards_env = []
        # 玩家角色代码：0-地主上家, 1-地主, 2-地主下家
        self.user_position_code = None
        self.user_position = ""
        # 开局时三个玩家的手牌
        self.card_play_data_list = {}
        # 出牌顺序：0-玩家出牌, 1-玩家下家出牌, 2-玩家上家出牌
        self.play_order = 0
        # 初始化游戏环境
        self.env = None
        # 识别玩家手牌
        self.user_hand_cards_real = self.find_my_cards(self.MyHandCardsPos)
        self.UserHandCards.setText(self.user_hand_cards_real)
        self.user_hand_cards_env = [RealCard2EnvCard[c] for c in list(self.user_hand_cards_real)]
        # 识别三张底牌
        self.three_landlord_cards_real = self.find_three_landlord_cards(self.ThreeLandlordCardsPos)
        self.ThreeLandlordCards.setText("底牌：" + self.three_landlord_cards_real)
        self.three_landlord_cards_env = [RealCard2EnvCard[c] for c in list(self.three_landlord_cards_real)]
        # 识别玩家的角色
        self.user_position_code = self.find_landlord(self.LandlordFlagPos)
        if self.user_position_code is None:
            items = ("地主上家", "地主", "地主下家")
            item, okPressed = QInputDialog.getItem(self, "选择角色", "未识别到地主，请手动选择角色:", items, 0, False)
            if okPressed and item:
                self.user_position_code = items.index(item)
            else:
                return
        self.user_position = ['landlord_up', 'landlord', 'landlord_down'][self.user_position_code]
        print("user_position==>", self.user_position)
        for player in self.Players:
            player.setStyleSheet('background-color: rgba(255, 0, 0, 0);')
        self.Players[self.user_position_code].setStyleSheet('background-color: rgba(255, 0, 0, 0.1);')

        # 整副牌减去玩家手上的牌，就是其他人的手牌,再分配给另外两个角色（如何分配对AI判断没有影响）
        for i in set(AllEnvCard):
            self.other_hand_cards.extend([i] * (AllEnvCard.count(i) - self.user_hand_cards_env.count(i)))
        self.card_play_data_list.update({
            'three_landlord_cards': self.three_landlord_cards_env,
            ['landlord_up', 'landlord', 'landlord_down'][(self.user_position_code + 0) % 3]:
                self.user_hand_cards_env,
            ['landlord_up', 'landlord', 'landlord_down'][(self.user_position_code + 1) % 3]:
                self.other_hand_cards[0:17] if (self.user_position_code + 1) % 3 != 1 else self.other_hand_cards[17:],
            ['landlord_up', 'landlord', 'landlord_down'][(self.user_position_code + 2) % 3]:
                self.other_hand_cards[0:17] if (self.user_position_code + 1) % 3 == 1 else self.other_hand_cards[17:]
        })
        print("card_play_data_list==>", self.card_play_data_list)
        # 生成手牌结束，校验手牌数量
        if len(self.card_play_data_list["three_landlord_cards"]) != 3:
            QMessageBox.critical(self, "底牌识别出错", "底牌必须是3张！", QMessageBox.Yes, QMessageBox.Yes)
            self.init_display()
            return
        if len(self.card_play_data_list["landlord_up"]) != 17 or \
            len(self.card_play_data_list["landlord_down"]) != 17 or \
            len(self.card_play_data_list["landlord"]) != 20:
            QMessageBox.critical(self, "手牌识别出错", "初始手牌数目有误", QMessageBox.Yes, QMessageBox.Yes)
            self.init_display()
            return
        # 得到出牌顺序
        self.play_order = 0 if self.user_position == "landlord" else 1 if self.user_position == "landlord_up" else 2
        print("play_order==>", self.play_order)

        # 创建一个代表玩家的AI
        ai_players = [0, 0]
        ai_players[0] = self.user_position
        ai_players[1] = DeepAgent(self.user_position, self.card_play_model_path_dict[self.user_position])

        self.env = GameEnv(ai_players)
        self.start()

    def start(self):
        self.env.card_play_init(self.card_play_data_list)
        print("开始出牌\n")
        while not self.env.game_over:
            # 玩家出牌时就通过智能体获取action，否则通过识别获取其他玩家出牌
            if self.play_order == 0:
                self.PredictedCard.setText("...")
                action_message = self.env.step(self.user_position)
                print("玩家出牌：", action_message["action"] if action_message["action"] else "不出", "， 胜率：",)
                # 更新界面
                self.UserHandCards.setText("手牌：" + str(''.join(
                    [EnvCard2RealCard[c] for c in self.env.info_sets[self.user_position].player_hand_cards]))[::-1])

                self.PredictedCard.setText(action_message["action"] if action_message["action"] else "不出")
                self.WinRate.setText("胜率：" + action_message["win_rate"])
                print("\n手牌：", str(''.join(
                        [EnvCard2RealCard[c] for c in self.env.info_sets[self.user_position].player_hand_cards])))
                print("出牌：", action_message["action"] if action_message["action"] else "不出", "， 胜率：",
                      action_message["win_rate"])
                while self.check_player_status(self.MPlayedCardsPos) == 0:
                    print("等待玩家出牌")
                    # 重启计时器，用于测量时间是否超过100毫秒
                    self.counter.restart()
                    while self.counter.elapsed() < 100:     # 在计时器记录的时间小于100毫秒内，持续处理事件
                        # 处理所有事件，但每个事件最多处理50毫秒，以确保程序响应迅速且界面不卡顿
                        QtWidgets.QApplication.processEvents(QEventLoop.AllEvents, 50)
                self.play_order = 1
                print("play_order :", self.play_order)
            elif self.play_order == 1:      # 第二个出牌
                self.RPlayedCard.setText("...")
                while self.check_player_status(self.RPlayedCardsPos) == 0:
                    print("等待下家出牌")
                    self.counter.restart()
                    while self.counter.elapsed() < 500:
                        QtWidgets.QApplication.processEvents(QEventLoop.AllEvents, 50)
                self.counter.restart()
                while self.counter.elapsed() < 500:
                    QtWidgets.QApplication.processEvents(QEventLoop.AllEvents, 50)
                # 未找到 "不出"
                if self.have_passFlag(self.RPlayedCardsPos) == 0 :
                    # 识别下家出牌
                    self.other_played_cards_real = self.find_other_cards(self.RPlayedCardsPos)
                # 找到"不出"
                else:
                    self.other_played_cards_real = ""
                print("\n下家出牌：", self.other_played_cards_real)
                self.other_played_cards_env = [RealCard2EnvCard[c] for c in list(self.other_played_cards_real)]
                self.env.step(self.user_position, self.other_played_cards_env)
                # 更新界面
                self.RPlayedCard.setText(self.other_played_cards_real if self.other_played_cards_real else "不出")
                self.play_order = 2
                print("play_order :", self.play_order)
            elif self.play_order == 2:
                self.LPlayedCard.setText("...")
                while self.check_player_status(self.LPlayedCardsPos) == 0:
                    print("等待上家出牌")
                    self.counter.restart()
                    while self.counter.elapsed() < 500:
                        QtWidgets.QApplication.processEvents(QEventLoop.AllEvents, 50)
                self.counter.restart()
                while self.counter.elapsed() < 500:
                    QtWidgets.QApplication.processEvents(QEventLoop.AllEvents, 50)
                # 未找到 "不出"
                if self.have_passFlag(self.LPlayedCardsPos) == 0:
                    # 识别上家出牌
                    self.other_played_cards_real = self.find_other_cards(self.LPlayedCardsPos)
                # 找到"不出"
                else:
                    self.other_played_cards_real = ""
                print("\n上家出牌：", self.other_played_cards_real)
                self.other_played_cards_env = [RealCard2EnvCard[c] for c in list(self.other_played_cards_real)]
                self.env.step(self.user_position, self.other_played_cards_env)
                self.play_order = 0
                print("play_order :", self.play_order)
                # 更新界面
                self.LPlayedCard.setText(self.other_played_cards_real if self.other_played_cards_real else "不出")
            else:
                pass

            self.counter.restart()
            while self.counter.elapsed() < 100:
                QtWidgets.QApplication.processEvents(QEventLoop.AllEvents, 50)

        print("{}胜，本局结束!\n".format("农民" if self.env.winner == "farmer" else "地主"))
        QMessageBox.information(self, "本局结束", "{}胜！".format("农民" if self.env.winner == "farmer" else "地主"),
                                QMessageBox.Yes, QMessageBox.Yes)
        self.env.reset()
        self.init_display()

    # 对字符串做排序，替换输入字符串中T为10
    def sort_cards(self, cards):
        cards = " ".join(sorted(cards))
        cards = cards.replace("T", "10") #

        return cards

    def calculate_similarity(self, template, image):
        result = cv2.matchTemplate(image, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        return max_val
    def find_landlord(self, landlord_flag_pos):
        highest_similarity = -1
        landlordPic = cv2.imread('pics/landlord_flag.png')
        for pos in landlord_flag_pos:
            # 截取屏幕区域
            screenshot = pyautogui.screenshot(region=pos)
            screenshot_np = np.array(screenshot)
            screenshot_rgb = cv2.cvtColor(screenshot_np, cv2.COLOR_BGR2RGB)

            # 计算相似度
            similarity = self.calculate_similarity(landlordPic, screenshot_rgb)

            if similarity > highest_similarity:
                highest_similarity = similarity
                index = landlord_flag_pos.index(pos)
        return index

    def find_three_landlord_cards(self, pos):
        three_landlord_cards_real = ""
        index = 0
        for onePos in pos:
            for card in AllCards[index:]:   # 设置for循环，从数组AllCards的序号index开始遍历
                try:
                    result = pyautogui.locateOnScreen(image='pics/threeCards/' + card + '.png', region=onePos,
                                                      confidence=self.ThreeLandlordCardsConfidence)
                    print("ThreeCards ==> ", card, AllCards.index(card))
                    three_landlord_cards_real += card[1]
                    index = AllCards.index(card) + 1  # 获取card在数组中的位置
                    break
                # 异常不处理
                except:
                    pass
        print("find_three_landlord_cards ==> ", three_landlord_cards_real)
        return three_landlord_cards_real

    def find_my_cards(self, pos):
        user_hand_cards_real = ""
        img = pyautogui.screenshot(region=pos)
        for card in AllCards:
            try:
                result = pyautogui.locateAll(needleImage='pics/handCards/' + card + '.png', haystackImage=img, confidence=self.MyHandCardsConfidence)
                count = self.cards_filter(list(result), self.MyFilter)
                user_hand_cards_real += card[1] * count
            except:
                pass
        print("user_hand_cards_real==> ", user_hand_cards_real)
        return user_hand_cards_real

    def find_other_cards(self, pos):
        other_played_cards_real = ""
        playLocation = "上家" if pos == self.LPlayedCardsPos else "下家" if pos == self.RPlayedCardsPos else "自己"
        self.counter.restart()
        while self.counter.elapsed() < 300:
            QtWidgets.QApplication.processEvents(QEventLoop.AllEvents, 100)
        img = pyautogui.screenshot(region=pos)
        print("发现其他家出牌: ", playLocation)
        for card in AllCards:
            try:
                result = pyautogui.locateAll(needleImage='pics/otherCards/' + card + '.png', haystackImage=img,
                                            confidence=self.OtherCardsConfidence)
                count = self.cards_filter(list(result), self.OtherFilter)
                print("OtherCards | count ==> ", card, count)
                other_played_cards_real += card[1] * count
            except:
                pass
        print("other_played_cards_real==> ", other_played_cards_real)
        return other_played_cards_real

    def cards_filter(self, location, distance):  # 牌检测结果滤波
        if len(location) == 0:
            return 0
        locList = [location[0][0]]
        count = 1
        for e in location:
            flag = 1  # “是新的”标志
            for have in locList:
                if abs(e[0] - have) <= distance:
                    flag = 0
                    break
            if flag:
                count += 1
                locList.append(e[0])
        return count

    def have_playCards(self, pos):  # 是否已经出牌
        playLocation = "上家" if pos == self.LPlayedCardsPos else "下家" if pos == self.RPlayedCardsPos else "自己"
        try:
            result = pyautogui.locateOnScreen('pics/playFlag.png', region=pos, confidence=self.playFlagConfidence)
            print("识别到==>出牌，位置:", playLocation)
            return 1
        except:
            pass
            return 0

    def have_passFlag(self, pos):  # 是否PASS
        playLocation = "上家" if pos == self.LPlayedCardsPos else "下家" if pos == self.RPlayedCardsPos else "自己"
        try:
            result = pyautogui.locateOnScreen('pics/passFlag.png', region=pos, confidence=self.passFlagConfidence)
            print("识别到==>不出，位置:", playLocation)
            return 1
        except:
            pass
            return 0

    # 检查玩家当前状态，返回等待（0），出牌（1）或不出（2）
    def check_player_status(self, pos):
        if self.have_playCards(pos):
            return 1
        elif self.have_passFlag(pos):
            return 2
        else:
            return 0

    def stop(self):
        try:
            self.env.game_over = True
        except AttributeError as e:
            pass 
            


if __name__ == '__main__':

    # os.environ['KMP_DUPLICATE_LIB_OK'] = 'True'
    # os.environ["CUDA_VISIBLE_DEVICES"] = '0'
    os.environ["GIT_PYTHON_REFRESH"] = 'quiet'

    app = QtWidgets.QApplication(sys.argv)
    app.setStyleSheet("""
    QPushButton{
        text-align : center;
        background-color : white;
        font: bold;
        border-color: gray;
        border-width: 2px;
        border-radius: 10px;
        padding: 6px;
        height : 14px;
        border-style: outset;
        font : 14px;
    }
    QPushButton:hover{
        background-color : light gray;
    }
    QPushButton:pressed{
        text-align : center;
        background-color : gray;
        font: bold;
        border-color: gray;
        border-width: 2px;
        border-radius: 10px;
        padding: 6px;
        height : 14px;
        border-style: outset;
        font : 14px;
        padding-left:9px;
        padding-top:9px;
    }
    QComboBox{
        background:transparent;
        border: 1px solid rgba(200, 200, 200, 100);
        font-weight: bold;
    }
    QComboBox:drop-down{
        border: 0px;
    }
    QComboBox QAbstractItemView:item{
        height: 30px;
    }
    QLabel{
        background:transparent;
        font-weight: bold;
    }
    """)
    my_pyqt_form = MyPyQT_Form()
    my_pyqt_form.show()
    sys.exit(app.exec_())
