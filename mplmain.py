from PyQt5.QtWidgets import *
from PyQt5.uic import loadUi

from matplotlib.backends.backend_qt5agg import (NavigationToolbar2QT as NavigationToolbar)

import numpy as np
import matplotlib.ticker as ticker
import matplotlib.lines


class MatplotlibWidget(QMainWindow):

    def __init__(self):
        QMainWindow.__init__(self)

        loadUi("interface.ui", self)
        self.setWindowTitle("Robot way")
        self.Button_go.setEnabled(False)
        self.Button_go.setToolTip('Enter values of first point and finish point\n(x, y from [0,50], can be divided by 5)')
        self.Button_go.clicked.connect(self.update_graph)
        self.Button_clear.clicked.connect(self.clear_graph)
        self.addToolBar(NavigationToolbar(self.MplWidget.canvas, self))

        self.lineedit_values = [0,0,0,0]       #правильные ли значения в lineedit
        self.lineEdit.textChanged.connect(self.on_lineedit)
        self.lineEdit_2.textChanged.connect(self.on_lineedit2)
        self.lineEdit_3.textChanged.connect(self.on_lineedit3)
        self.lineEdit_4.textChanged.connect(self.on_lineedit4)

        file = open('board.txt', 'r')  # загружаем схему разрешенных, запрещенных точек из файла
        board = np.loadtxt(file, int)
        h,w = board.shape
        self.rows = h
        self.cols = w
        file.close()

        self.board = board  # схема запрещенных, разрешенных точек
        self.set_grid()

    def set_grid(self):
        self.MplWidget.canvas.axes.set_title('Robot way')
        self.MplWidget.canvas.axes.set_xlim([-5, 55])
        self.MplWidget.canvas.axes.set_ylim([-5, 55])
        self.MplWidget.canvas.axes.set_xlabel('X-axis', fontsize=10)
        self.MplWidget.canvas.axes.set_ylabel('Y-axis', fontsize=10)
        self.MplWidget.canvas.axes.xaxis.set_major_locator(ticker.MultipleLocator(5))
        self.MplWidget.canvas.axes.yaxis.set_major_locator(ticker.MultipleLocator(5))
        self.MplWidget.canvas.axes.spines['bottom'].set_color('red')
        self.MplWidget.canvas.axes.spines['left'].set_color('red')
        self.MplWidget.canvas.axes.tick_params(axis='x', colors='red', labelrotation=90)
        self.MplWidget.canvas.axes.tick_params(axis='y', colors='red')
        for i in range(self.rows):
            for j in range(self.cols):
                x = i * 5
                y = j * 5
                if self.board[i][j] == 0:
                    self.MplWidget.canvas.axes.plot(x, y, 'o', color='r')
        self.MplWidget.canvas.axes.grid()

    def check_lineedit(self, text):
        if text.isdigit() and int(text) >= 0 and int(text) <= 50 and int(text)%5==0:
            return True
        else:
            return False

    def on_lineedit(self):
        text= str(self.lineEdit.text())
        if self.check_lineedit(text):
            self.lineEdit.setStyleSheet("color: green;")
            self.lineedit_values[0] = 1
        else:
            self.lineEdit.setStyleSheet("color: red;")
            self.lineedit_values[0] = 0
        if self.lineedit_values == [1,1,1,1]:
            self.Button_go.setEnabled(True)
        else:
            self.Button_go.setEnabled(False)

    def on_lineedit2(self):
        text = str(self.lineEdit_2.text())
        if self.check_lineedit(text):
            self.lineEdit_2.setStyleSheet("color: green;")
            self.lineedit_values[1] = 1
        else:
            self.lineEdit_2.setStyleSheet("color: red;")
            self.lineedit_values[1] = 0
        if self.lineedit_values == [1,1,1,1]:
            self.Button_go.setEnabled(True)
        else:
            self.Button_go.setEnabled(False)

    def on_lineedit3(self):
        text = str(self.lineEdit_3.text())
        if self.check_lineedit(text):
            self.lineEdit_3.setStyleSheet("color: green;")
            self.lineedit_values[2] = 1
        else:
            self.lineEdit_3.setStyleSheet("color: red;")
            self.lineedit_values[2] = 0
        if self.lineedit_values == [1,1,1,1]:
            self.Button_go.setEnabled(True)
        else:
            self.Button_go.setEnabled(False)

    def on_lineedit4(self):
        text = str(self.lineEdit_4.text())
        if self.check_lineedit(text):
            self.lineEdit_4.setStyleSheet("color: green;")
            self.lineedit_values[3] = 1
        else:
            self.lineEdit_4.setStyleSheet("color: red;")
            self.lineedit_values[3] = 0
        if self.lineedit_values == [1,1,1,1]:
            self.Button_go.setEnabled(True)
        else:
            self.Button_go.setEnabled(False)


    def clear_graph(self):
        self.textBrowser.clear()
        self.MplWidget.canvas.axes.clear()
        self.set_grid()
        self.MplWidget.canvas.draw()

    def update_graph(self):
        self.textBrowser.clear()
        self.MplWidget.canvas.axes.clear()
        self.set_grid()
        self.MplWidget.canvas.draw()

        self.start_x = int(int(self.lineEdit.text())/5)
        self.start_y = int(int(self.lineEdit_2.text())/5)
        self.target_x = int(int(self.lineEdit_3.text()) / 5)
        self.target_y = int(int(self.lineEdit_4.text()) / 5)
        self.g0 = (self.start_x, self.start_y)
        self.gt = (self.target_x, self.target_y)

        self.visited = [[False for i in range(self.rows)] for j in
                        range(self.cols)]  # False - узел не посещен. будем ставить True, когда посетим узел
        self.parent = [[() for i in range(self.rows)] for j in
                       range(self.cols)]  # это для хранения данных, откуда пришли в каждую точку пути

        self.search()

    def search(self):
        x = self.start_x
        y = self.start_y
        for dx, dy in np.random.permutation([[-1, 0], [0, -1], [0, 1], [1,0]]):  # случайным образом выбор направления, куда пойти - верх, низ, лево, право
            x_next = x + dx
            y_next = y + dy

            if (x_next > -1 and y_next > -1 and x_next < self.rows and y_next < self.cols):  # проверка, что не вышли за границы поля
                if self.board[x_next][y_next] == 1 and self.visited[x_next][
                    y_next] == 0:  # если точка разрешенная и ее еще не посещали, переходим в нее
                    self.parent[x_next][y_next] = (x, y)  # запоминаем родительскую точку
                    if self.dfs(x_next, y_next):  # идем дальше в рекурсию
                        return
        self.print_path(self.g0, self.gt) # пишем пройденный путь
        self.draw_plt(self.g0, self.gt)  # рисуем

    def dfs(self, x, y):  # рекурсия
        if not self.visited[x][y] and self.board[x][y] == 1:
            self.visited[x][y] = True

            for dx, dy in np.random.permutation([[-1, 0], [0, -1], [0, 1], [1,
                                                                            0]]):  # случайным образом выбор направления, куда пойти - верх, низ, лево, право
                x_next = x + dx
                y_next = y + dy

                if (x_next > -1 and y_next > -1 and x_next < self.rows and y_next < self.cols):  # проверка, что не вышли за границы поля
                    if self.board[x_next][y_next] == 1 and self.visited[x_next][y_next] == 0:  # если точка разрешенная и ее еще не посещали, переходим в нее
                        # print('the next is ({},{})'.format(x_next, y_next))                        # отладочная инфа
                        self.parent[x_next][y_next] = (x, y)  # запоминаем родительскую точку
                        if x_next == self.target_x and y_next == self.target_y:  # если достигли конечной точки
                            self.print_path(self.g0, self.gt)  # пишем пройденный путь
                            self.draw_plt(self.g0, self.gt)  # рисуем сетку

                            return True
                        else:
                            if self.dfs(x_next, y_next):  # отправляем следующую точку в рекурсию
                                return True

    def print_path(self, source, destination):  # после вывода сетки пропишем пройденный путь
        # self.textBrowser.append(self.parent)
        if destination == source:
            self.textBrowser.append("({}, {})".format(destination[0] * 5, destination[1] * 5))
        elif self.parent[destination[0]][destination[1]] == ():
            self.textBrowser.append("No Path")
        else:
            self.print_path(source, self.parent[destination[0]][destination[1]])
            self.textBrowser.append("-> ({}, {})".format(destination[0] * 5, destination[1] * 5))

    def draw_plt(self, source, destination):  # рисование сетки
        if self.parent[destination[0]][destination[1]] == ():
            pass
            # self.textBrowser.append("No Path")
        else:
            x0 = destination[0]
            y0 = destination[1]
            while destination != source:
                destination = self.parent[x0][y0]
                x1 = destination[0]
                y1 = destination[1]
                line = matplotlib.lines.Line2D([x0 * 5, x1 * 5], [y0 * 5, y1 * 5], color="g")
                self.MplWidget.canvas.axes.add_line(line)

                x0 = x1
                y0 = y1

            self.MplWidget.canvas.axes.plot(self.start_x * 5, self.start_y * 5, 'o', color='b')
            self.MplWidget.canvas.axes.plot(self.target_x * 5, self.target_y * 5, 'o', color='y')
            self.MplWidget.canvas.draw()

def main():
    app = QApplication([])
    window = MatplotlibWidget()
    window.show()
    app.exec_()

if __name__=='__main__':
    main()