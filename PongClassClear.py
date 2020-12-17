import time
import random
import torch
import numpy as np
import math
import turtle
from threading import Thread
from multiprocessing import Process
import collections
import multiprocessing
# глобальные переменные
# настройки окна
WIDTH = 1000
HEIGHT = 500
 
# настройки ракеток
# ширина ракетки
PAD_W = 10
# высота ракетки
PAD_H = 100

Start_speed = 1
ACCeleraion = 0.1
Rand_K_edge = 1.3
BALL_RADIUS = 20

class Racket(object):
    def __init__(self, coorX, coorY, step, Height, Wigth):
        self.coorX = coorX
        self.coorY = coorY
        self.step = step
        self.Height = Height
        self.Wigth = Wigth
    def gotoXY(self, dir):
        if dir != "Up" and dir != "Down":
            return 1
        if dir == "Up":
            self.coorY = self.coorY + self.step
            return 0
        if dir == "Down":
            self.coorY = self.coorY - self.step
            return 0

class Ball(object):
    def __init__(self, coorX, coorY, radius, step, K, LefRig, speed):
        self.coorX = coorX
        self.coorY = coorY
        self.radius = radius
        self.step = step
        self.K = K
        self.lefrig = LefRig
        self.speed = speed

        self.memcoorX = self.coorX
        self.memcoorY = self.coorY
        self.memstep = self.step
        self.memspeed = self.speed
    def forward(self):
        if self.lefrig == "Left" or self.lefrig == "Right":
            #надо бы еще проверять чтобы мяч вертикально не направляли(предусмотрено в коде почти)
            if self.lefrig == "Right":
                self.coorX = self.coorX + self.step
                self.coorY = self.coorY + self.step*self.K
            if self.lefrig == "Left":
                self.coorX = self.coorX - self.step
                self.coorY = self.coorY + self.step*self.K
        else:
            print("dir - Говно = ", self.K)
    def rand(self):
        self.K = random.uniform(-Rand_K_edge, Rand_K_edge)
        temp = random.randint(0,1)
        if temp == 0: self.lefrig = "Left"
        else: self.lefrig = "Right"
    def reset(self):
        self.coorX = self.memcoorX
        self.coorY = self.memcoorY
        self.step = self.memstep
        self.speed = self.memspeed

#рандомим направление
K = random.uniform(-Rand_K_edge, Rand_K_edge)
LefRig = "Left"
Racket1 = Racket(0, HEIGHT/2, 20, PAD_H, PAD_W)
Racket2 = Racket(WIDTH, HEIGHT/2, 20, PAD_H, PAD_W)

TenBall = Ball(WIDTH/2, HEIGHT/2, BALL_RADIUS, 3, K, LefRig, Start_speed)

class PongGame(object):
    def __init__(self, Racket1, Racket2, TenBall, ISDRAW = False):
        self.Racket1 = Racket1
        self.Racket2 = Racket2
        self.TenBall = TenBall
        self.ISDRAW = ISDRAW
        if ISDRAW:
            initedGameItems = self.DrawwithCanvas_init_(self.Racket1, self.Racket2, self.TenBall)
            self.screen = initedGameItems[0]
            self.DRracket1 = initedGameItems[1]
            self.DRracket2 = initedGameItems[2]
            self.DRBall = initedGameItems[3]
            self.timmi1 = initedGameItems[4]
            self.timmi2 = initedGameItems[5]
    def __Input_1__(self, screen):
        screen.onkeypress(lambda: self.Racket1.gotoXY("Up"), "w")
        screen.onkeypress(lambda: self.Racket1.gotoXY("Down"), "s")
        screen.listen()
        pass
    def __Input_2__(self, screen):
        screen.onkeypress(lambda: self.Racket2.gotoXY("Up"), "Up")
        screen.onkeypress(lambda: self.Racket2.gotoXY("Down"), "Down")
        screen.listen()
        pass
    def __Input_AI_1__(self):
        disttoballfromwall = (self.TenBall.coorX - self.TenBall.radius - self.Racket1.Wigth)/1000
        
        sensor1 = (0, 1)[abs(self.TenBall.coorY - self.Racket1.coorY) < self.TenBall.radius]
        sensor2 = (0, 1)[abs(self.TenBall.coorY - (self.TenBall.coorX + self.Racket1.coorY)) < self.TenBall.radius]
        sensor3 = (0, 1)[abs(self.TenBall.coorY - (-self.TenBall.coorX + self.Racket1.coorY)) < self.TenBall.radius]
        sensor4 = (0, 1)[abs(self.TenBall.coorY - (0.5 * self.TenBall.coorX + self.Racket1.coorY)) < self.TenBall.radius]
        sensor5 = (0, 1)[abs(self.TenBall.coorY - (-0.5 * self.TenBall.coorX + self.Racket1.coorY)) < self.TenBall.radius]
        sensor6 = (0, 1)[abs(self.TenBall.coorY - (2 * self.TenBall.coorX + self.Racket1.coorY)) < self.TenBall.radius]
        sensor7 = (0, 1)[abs(self.TenBall.coorY - (-2 * self.TenBall.coorX + self.Racket1.coorY)) < self.TenBall.radius]

        self.sensors1 = [sensor1,sensor2,sensor3,sensor4,sensor5,sensor6,sensor7,disttoballfromwall]
        
        
        inputs = torch.FloatTensor(self.sensors1)
        outputs = self.net1.forward(inputs)
        
        if outputs[0] >= outputs[1] and outputs[0] >= outputs[2]:
            self.Racket1.gotoXY("Up")
        else:
            if outputs[1] >= outputs[2]:
                self.Racket1.gotoXY("Down")
        pass
    def __Input_AI_2__(self):
        disttoballfromwall = (WIDTH + self.TenBall.radius - self.TenBall.coorX) / 1000
        sensor1 = (0, 1)[abs(self.TenBall.coorY - self.Racket2.coorY) < self.TenBall.radius]
        sensor2 = (0, 1)[abs(self.TenBall.coorY - (-(self.TenBall.coorX - WIDTH) + self.Racket2.coorY )) < self.TenBall.radius]
        sensor3 = (0, 1)[abs(self.TenBall.coorY - ((self.TenBall.coorX - WIDTH) + self.Racket2.coorY )) < self.TenBall.radius]
        sensor4 = (0, 1)[abs(self.TenBall.coorY - (-0.5 * (self.TenBall.coorX - WIDTH) + self.Racket2.coorY)) < self.TenBall.radius]
        sensor5 = (0, 1)[abs(self.TenBall.coorY - (0.5 * (self.TenBall.coorX - WIDTH) + self.Racket2.coorY)) < self.TenBall.radius]
        sensor6 = (0, 1)[abs(self.TenBall.coorY - (-2 * (self.TenBall.coorX - WIDTH) + self.Racket2.coorY)) < self.TenBall.radius]
        sensor7 = (0, 1)[abs(self.TenBall.coorY - (2 * (self.TenBall.coorX - WIDTH) + self.Racket2.coorY)) < self.TenBall.radius]

        self.sensors2 = [sensor1,sensor2,sensor3,sensor4,sensor5,sensor6,sensor7,disttoballfromwall]

        inputs = torch.FloatTensor(self.sensors2)
        outputs = self.net2.forward(inputs)

        if outputs[0] >= outputs[1]:
            self.Racket2.gotoXY("Up")
        else:
            self.Racket2.gotoXY("Down")
        pass
    def DrawwithCanvas_init_(self, Racket1, Racket2, TenBall):
        import turtle

        screen = turtle.Screen()
        screen.clear()
        screen.title('Pong with turtle module')
        screen.bgcolor('pink')
        diffScreen = 50 #чтобы видно было все
        screen.setup(WIDTH + diffScreen, HEIGHT + diffScreen)
        screen.tracer(0)
        screen.setworldcoordinates(-diffScreen, -diffScreen, WIDTH + diffScreen, HEIGHT + diffScreen)

        # draw a game field border
        border = turtle.Turtle()
        border.hideturtle()
        border.penup()
        border.goto(0, 0)
        border.pendown()
        border.goto(0, HEIGHT)
        border.goto(WIDTH, HEIGHT)
        border.goto(WIDTH, 0)
        border.goto(0, 0)

        #создаем ракетки
        DRracket1 = turtle.Turtle()
        DRracket1.shape('square')
        DRracket1.shapesize(Racket1.Height/20, Racket1.Wigth/20)
        #border.goto(0, HEIGHT/2+10)
        #border.goto(10, HEIGHT/2+10)
        DRracket1.penup()
        DRracket1.setpos(Racket1.coorX + Racket1.Wigth / 2, Racket1.coorY)

        DRracket2 = turtle.Turtle()
        DRracket2.shape('square')
        DRracket2.shapesize(Racket2.Height/20, Racket2.Wigth/20)
        DRracket2.penup()
        DRracket2.setpos(Racket2.coorX - Racket2.Wigth / 2, Racket2.coorY)

        DRBall = turtle.Turtle()
        DRBall.shape('circle')
        DRBall.shapesize(TenBall.radius/20)
        DRBall.penup()
        DRBall.setpos(TenBall.coorX, TenBall.coorY)

        timmi1 = turtle.Turtle()
        timmi1.hideturtle()
        timmi1.penup()
        timmi1.setpos(0,HEIGHT+10)
        timmi1.write(str(0), font = ("d",25,"bold"))
        
        timmi2 = turtle.Turtle()
        timmi2.hideturtle()
        timmi2.penup()
        timmi2.setpos(WIDTH-50,HEIGHT+10)
        timmi2.write(str(0), font = ("d",25,"bold"))


        screen.update()
        return [screen, DRracket1, DRracket2, DRBall, timmi1, timmi2]
    def DrawwithCanvas(self, sensor1,sensor2,sensor3,sensor4,sensor5,sensor6,sensor7):

        disttoballfromwall = (self.TenBall.coorX - self.TenBall.radius - self.Racket1.Wigth)/1000
        
        sensor11 = (0, 1)[abs(self.TenBall.coorY - self.Racket1.coorY) < self.TenBall.radius]
        sensor22 = (0, 1)[abs(self.TenBall.coorY - (self.TenBall.coorX + self.Racket1.coorY)) < self.TenBall.radius]
        sensor33 = (0, 1)[abs(self.TenBall.coorY - (-self.TenBall.coorX + self.Racket1.coorY)) < self.TenBall.radius]
        sensor44 = (0, 1)[abs(self.TenBall.coorY - (0.5 * self.TenBall.coorX + self.Racket1.coorY)) < self.TenBall.radius]
        sensor55 = (0, 1)[abs(self.TenBall.coorY - (-0.5 * self.TenBall.coorX + self.Racket1.coorY)) < self.TenBall.radius]
        sensor66 = (0, 1)[abs(self.TenBall.coorY - (2 * self.TenBall.coorX + self.Racket1.coorY)) < self.TenBall.radius]
        sensor77 = (0, 1)[abs(self.TenBall.coorY - (-2 * self.TenBall.coorX + self.Racket1.coorY)) < self.TenBall.radius]

        self.sensors1 = [sensor11,sensor22,sensor33,sensor44,sensor55,sensor66,sensor77,disttoballfromwall]

        self.DRracket1.goto(self.Racket1.coorX, self.Racket1.coorY)
        self.DRracket2.goto(self.Racket2.coorX, self.Racket2.coorY)
        self.DRBall.goto(self.TenBall.coorX, TenBall.coorY)


        # if self.sensors1[0] == 1: sensor1.pencolor('red')
        # else: sensor1.pencolor('black')
        # sensor1.hideturtle()
        # sensor1.penup()
        # sensor1.goto(self.Racket1.coorX, self.Racket1.coorY)
        # sensor1.pendown()
        # sensor1.goto(self.Racket1.coorX + WIDTH, self.Racket1.coorY)


        # if self.sensors1[1] == 1: sensor2.pencolor('red')
        # else: sensor2.pencolor('black')
        # sensor2.hideturtle()
        # sensor2.penup()
        # sensor2.goto(self.Racket1.coorX, self.Racket1.coorY)
        # sensor2.pendown()
        # sensor2.goto(self.Racket1.coorX + WIDTH, (self.Racket1.coorX + WIDTH) + self.Racket1.coorY )


        # if self.sensors1[2] == 1: sensor3.pencolor('red')
        # else: sensor3.pencolor('black')
        # sensor3.hideturtle()
        # sensor3.penup()
        # sensor3.goto(self.Racket1.coorX, self.Racket1.coorY)
        # sensor3.pendown()
        # sensor3.goto(self.Racket1.coorX + WIDTH, -(self.Racket1.coorX + WIDTH) + self.Racket1.coorY )


        # if self.sensors1[3] == 1: sensor4.pencolor('red')
        # else: sensor4.pencolor('black')
        # sensor4.hideturtle()
        # sensor4.penup()
        # sensor4.goto(self.Racket1.coorX, self.Racket1.coorY)
        # sensor4.pendown()
        # sensor4.goto(self.Racket1.coorX + WIDTH, 0.5 * (self.Racket1.coorX + WIDTH) + self.Racket1.coorY )


        # if self.sensors1[4] == 1: sensor5.pencolor('red')
        # else: sensor5.pencolor('black')
        # sensor5.hideturtle()
        # sensor5.penup()
        # sensor5.goto(self.Racket1.coorX, self.Racket1.coorY)
        # sensor5.pendown()
        # sensor5.goto(self.Racket1.coorX + WIDTH, -0.5 * (self.Racket1.coorX + WIDTH) + self.Racket1.coorY )


        # if self.sensors1[5] == 1: sensor6.pencolor('red')
        # else: sensor6.pencolor('black')
        # sensor6.hideturtle()
        # sensor6.penup()
        # sensor6.goto(self.Racket1.coorX, self.Racket1.coorY)
        # sensor6.pendown()
        # sensor6.goto(self.Racket1.coorX + WIDTH, 2 * (self.Racket1.coorX + WIDTH) + self.Racket1.coorY )


        # if self.sensors1[6] == 1: sensor7.pencolor('red')
        # else: sensor7.pencolor('black')
        # sensor7.hideturtle()
        # sensor7.penup()
        # sensor7.goto(self.Racket1.coorX, self.Racket1.coorY)
        # sensor7.pendown()
        # sensor7.goto(self.Racket1.coorX + WIDTH, -2 * (self.Racket1.coorX + WIDTH) + self.Racket1.coorY )

        self.screen.update()
        # sensor1.clear()
        # sensor2.clear()
        # sensor3.clear()
        # sensor4.clear()
        # sensor5.clear()
        # sensor6.clear()
        # sensor7.clear()
    def Logic(self):
        self.TenBall.forward()
        #вышел за ширину ракетки
        if self.TenBall.coorX <= PAD_W or self.TenBall.coorX >= WIDTH - PAD_W:
            #вышел за левую ракетку
            if self.TenBall.coorX <= PAD_W:
                #попал в левую ракетку
                if abs(self.TenBall.coorY - self.Racket1.coorY) < self.Racket1.Height/2:
                    self.TenBall.K = random.uniform(-Rand_K_edge, Rand_K_edge)
                    self.TenBall.step += ACCeleraion
                    self.TenBall.lefrig = "Right"
                    self.touchcount1 += 1
                #не попал
                else:
                    self.PLAYER_2_SCORE += 1
                    self.gameOver = self.isGameOver()
                    self.TenBall.reset()
                    self.TenBall.rand()
                    if self.ISDRAW:
                        self.updateScore()
                        self.screen.bgcolor('red')
                        time.sleep(0.7)
                        self.screen.bgcolor('pink')
            #вышел за правую
            else:
                #попал в правую ракетку
                if abs(self.TenBall.coorY - self.Racket2.coorY) < self.Racket2.Height/2:
                    self.TenBall.K = random.uniform(-Rand_K_edge, Rand_K_edge)
                    self.TenBall.step += ACCeleraion
                    self.TenBall.lefrig = "Left"
                    self.touchcount2 += 1
                #не попал
                else:
                    self.PLAYER_1_SCORE += 1
                    self.gameOver = self.isGameOver()
                    self.TenBall.reset()
                    self.TenBall.rand()
                    if self.ISDRAW:
                        self.updateScore()
                        self.screen.bgcolor('red')
                        time.sleep(0.7)
                        self.screen.bgcolor('pink')

        #стукнулся об полоток и пол
        if self.TenBall.coorY - self.TenBall.radius <= 0 or self.TenBall.coorY + self.TenBall.radius >= HEIGHT:
            self.TenBall.K *= -1

        if self.Racket1.coorY - self.Racket1.Height/2 < 0 or self.Racket1.coorY + self.Racket1.Height/2> HEIGHT:
            if self.Racket1.coorY - self.Racket1.Height/2 < 0:
                self.Racket1.coorY = self.Racket1.Height/2
            else:
                self.Racket1.coorY = HEIGHT - self.Racket1.Height/2
        if self.Racket2.coorY - self.Racket2.Height/2 < 0 or self.Racket2.coorY + self.Racket2.Height/2> HEIGHT:
            if self.Racket2.coorY - self.Racket2.Height/2 < 0:
                self.Racket2.coorY = self.Racket2.Height/2
            else:
                self.Racket2.coorY = HEIGHT - self.Racket2.Height/2
        pass
    def startGame(self):
        # Счет игроков
        self.touchcount1 = 0
        self.touchcount2 = 0
        self.PLAYER_1_SCORE = 0
        self.PLAYER_2_SCORE = 0
        self.gameOver = 0
        isinited = False
        isinited_kostil = False
        while not self.gameOver:
            #если нужно отрисовывать
            if self.ISDRAW:
                #создаем объекты и поток ввода
                if not isinited:
                    #вот такой инпут если нужно рисовать для людей
                    self.__Input_1__(self.screen)
                    self.__Input_2__(self.screen)
                    isinited = True
                #отрисовка    
                self.DrawwithCanvas()
            else:
                #костыльный поток ввода
                if not isinited_kostil:
                    import turtle
                    screen = turtle.Screen()
                    self.__Input_1__(screen)
                    self.__Input_2__(screen)
                    isinited_kostil = True
                screen.update()
            #этот магический инпут еще не написан для сетки
            #MagickInput()
            self.Logic()

        return [self.gameOver, self.PLAYER_1_SCORE, self.PLAYER_2_SCORE, self.touchcount1, self.touchcount2]
    def play_AI(self, net1, net2):
        # Счет игроков
        isinited = False
        self.touchcount1 = 0
        self.touchcount2 = 0
        self.net1 = net1
        self.net2 = net2
        self.PLAYER_1_SCORE = 0
        self.PLAYER_2_SCORE = 0
        self.gameOver = 0
        while not self.gameOver:
            #если нужно отрисовывать
            if self.ISDRAW:
                if not isinited:
                    sensor1 = turtle.Turtle()
                    sensor2 = turtle.Turtle()
                    sensor3 = turtle.Turtle()
                    sensor4 = turtle.Turtle()
                    sensor5 = turtle.Turtle()
                    sensor6 = turtle.Turtle()
                    sensor7 = turtle.Turtle()
                    # pool1 = multiprocessing.Pool()
                    # result = pool1.map(self.__Input_AI_1__, [])
                    # pool2 = multiprocessing.Pool()
                    # result = pool2.map(self.__Input_AI_1__, [])
                    # # thread1 = Process(target=self.__Input_AI_1__)
                    # # thread2 = Process(target=self.__Input_AI_2__)
                    # # thread1.start()
                    # # thread2.start()
                    isinited = True
                self.__Input_AI_1__()
                self.__Input_AI_2__()
                #отрисовка    
                self.DrawwithCanvas(sensor1,sensor2,sensor3,sensor4,sensor5,sensor6,sensor7)
            else:
                #if not isinited:
                    # pool1 = multiprocessing.Pool()
                    # result = pool1.map(self.__Input_AI_1__, [])
                    # pool2 = multiprocessing.Pool()
                    # result = pool2.map(self.__Input_AI_1__, [])
                    # # thread1 = Process(target=self.__Input_AI_1__)
                    # # thread2 = Process(target=self.__Input_AI_2__)
                    # # thread1.start()
                    # # thread2.start()
                    #isinited = True
                self.__Input_AI_1__()
                self.__Input_AI_2__()
            #этот магический инпут еще не написан для сетки
            #MagickInput()
            self.Logic()
            # time.sleep(0)
        # thread1.join()
        # thread2.join()
        return [self.gameOver, self.PLAYER_1_SCORE, self.PLAYER_2_SCORE, self.touchcount1, self.touchcount2]
    def isGameOver(self):
        if self.PLAYER_1_SCORE == 2:
            return 1
        if self.PLAYER_2_SCORE == 2:
            return 2
        else: return 0
    def updateScore(self):
        self.timmi1.clear()
        self.timmi1.write(str(self.PLAYER_1_SCORE), font = ("d",25,"bold"))
        self.timmi2.clear()
        self.timmi2.write(str(self.PLAYER_2_SCORE), font = ("d",25,"bold"))



NUM_INPUT = 8
NUM_HIDDEN = 10
class SineNet(torch.nn.Module):
    def __init__(self, n_hidden_neurons):
        super(SineNet, self).__init__()
        self.fc1 = torch.nn.Linear(NUM_INPUT, n_hidden_neurons)
        self.act1 = torch.nn.Tanh()
        self.fc2 = torch.nn.Linear(n_hidden_neurons, 3)
        #self.sm = torch.nn.Sigmoid()
        #self.sm0 = torch.nn.ReLU()
        self.sm = torch.nn.Softmax()

    def forward(self, x):
        x = self.fc1(x)
        x = self.act1(x)
        x = self.fc2(x)
        #x = self.smmm(x)
        #x = self.sm0(x)
        x = self.sm(x)
        return x


sine_net1 = SineNet(NUM_HIDDEN)
sine_net2 = SineNet(NUM_HIDDEN)


def getNeuroNet(osob):
    LovalNEt = SineNet(NUM_HIDDEN)

    A = [osob[i] for i in range(NUM_HIDDEN*NUM_INPUT) ]
    # for i in range(NUM_HIDDEN*NUM_INPUT):
    #     A.append(osob[i])
    B = [osob[i] for i in range(NUM_HIDDEN*NUM_INPUT, NUM_HIDDEN*(NUM_INPUT+1)) ]
    # for i in range(NUM_HIDDEN*NUM_INPUT, NUM_HIDDEN*(NUM_INPUT+1)):
    #     B.append(osob[i])
    C = [osob[i] for i in range(NUM_HIDDEN*(NUM_INPUT+1), (1+NUM_INPUT)*NUM_HIDDEN + 3*NUM_HIDDEN)]
    # for i in range(NUM_HIDDEN*(NUM_INPUT+1), (1+NUM_INPUT)*NUM_HIDDEN + 3*NUM_HIDDEN):
    #     C.append(osob[i])
    D = [osob[i] for i in range((1+NUM_INPUT)*NUM_HIDDEN + 3*NUM_HIDDEN, (1+NUM_INPUT)*NUM_HIDDEN + 3*(NUM_HIDDEN+1)) ]
    # for i in range((1+NUM_INPUT)*NUM_HIDDEN + 3*NUM_HIDDEN, (1+NUM_INPUT)*NUM_HIDDEN + 3*(NUM_HIDDEN+1)):
    #     D.append(osob[i])
    

    A = torch.tensor(A)
    B = torch.tensor(B)
    C = torch.tensor(C)
    D = torch.tensor(D)

    A = torch.reshape(A, (NUM_HIDDEN, NUM_INPUT))
    C = torch.reshape(C, (3, NUM_HIDDEN))

    dic_State = {'fc1.weight': A, 'fc1.bias': B, 'fc2.weight': C, 'fc2.bias': D}
    LovalNEt.load_state_dict(dic_State)
    return LovalNEt


def f(osob1, osob2):
    a = getNeuroNet(osob1)
    b = getNeuroNet(osob2)
    
    Pong = PongGame(Racket1, Racket2, TenBall, ISDRAW = False)
    results = Pong.play_AI(a, b)
    return -(results[3] - results[2])


def f_visual(osob1, osob2):
    a = getNeuroNet(osob1)
    b = getNeuroNet(osob2)
    
    Pong = PongGame(Racket1, Racket2, TenBall, ISDRAW = True)
    results = Pong.play_AI(a, b)
    return -(results[3] - results[2])




def mutation(x):
    s = random.randint(0, 10)
    for i in range(s):
        m = len(x)
        k = random.randint(0, m-1)
        z = random.randint(0, m-1)
        x[k], x[z] = x[z], x[k]
        # if k%2 == 0:
        #     if x[k] > 0.5:
        #         x[k] = x[k]*0.5
        #     else:
        #         x[k] = x[k]*2

def сrossing(pop, prob):
    n = int(len(pop)/2)
    for i in range(n):
        pop[n+i] = pop[i].copy()
        m = len(pop[i])
        r = random.randint(0, m-1)
        l = random.randint(0, m-1)
        while r==l:
            l = random.randint(0, m-1)
        if l<r:
            l, r = r, l
        for j in range(math.ceil((l-r)/2)):
            pop[n+i][r + j], pop[n+i][l - j] = pop[n+i][l - j], pop[n+i][r + j] 
        if (1+random.randint(0, 99)<=prob):
            mutation(pop[n+i])

def сrossing2(pop, prob):
    n = int(len(pop)/2)
    m = len(pop[0])
    for i in range(0,n,2):
        r = random.randint(0, m)
        a = []
        for j in range(r):
            a.append(pop[i][j])
        for j in range(m-r):
            a.append(pop[i+1][j])
        b = []
        for j in range(r):
            b.append(pop[i+1][j])
        for j in range(m-r):
            b.append(pop[i][j])

        pop[i+n] = a.copy()
        
        if (1+random.randint(0, 99)<=prob):
            mutation(pop[i])        

def SBX_crossing(pop, prob):
    n = int(len(pop)/2)
    m = len(pop[0])
    for i in range(0,n-1):

        NN = random.uniform(2,5)

        beta = []
        for _ in range(m):
            U = random.uniform(0,1)
            if U <= 0.5:
                beta.append((2*U) ** (1/(NN+1)))
            else:
                beta.append((0.5 * 1/(1-U)) ** (1/(NN+1)))


        for j in range(m):
            try:
                pop[i+n][j] = 0.5 * ( (1-beta[j])*pop[i][j] + (1+beta[j])*pop[i+1][j] )
                pop[i+n+1][j] = 0.5 * ( (1-beta[j])*pop[i+1][j] + (1+beta[j])*pop[i][j] )
            except Exception:
                print(i, " ", n, " ", i+n," ", j)

        if (1+random.randint(0, 99)<=prob):
            mutation(pop[n+i])



def randPopulation(pop):
    m = len(pop[0])
    numbers=[random.uniform(-0.5, 0.5) for i in range(m)]
    for i in range (n):
        #random.shuffle(numbers)
        pop[i]=numbers


def read_from_file():
    funk = open('D:/Kek_Kok_Kik/PongAI/Pong_results_суперпупер.txt', mode='r')
    number1 = funk.readline()
    read_pop1 = funk.readline().split()
    number2 = funk.readline()
    number3 = funk.readline()
    number4 = funk.readline()
    read_pop2 = funk.readline().split()
    list_1 = [float(i) for i in read_pop1]
    list_2 = [float(i) for i in read_pop2]

    list1 = [list_1, list_2]
    funk.close()
    return list1

osob = read_from_file()
f_visual(osob[0], osob[1])

# Pong = PongGame(Racket1, Racket2, TenBall, ISDRAW = True)
# Pong.startGame()


start_time = time.time()
n = 20 #число особей в популяции
m = (1+NUM_INPUT)*NUM_HIDDEN + 3*(NUM_HIDDEN+1) #число городов
prob = 20 #вероятность мутации 
if n % 2 != 0: 
    print("think again")
pop = np.zeros((n, m), dtype = np.float32)
T = 10000 # число поколений
randPopulation(pop)
#init_pop(pop)


listik = []
listik.append((f(pop[0],pop[1]),0))
minn = listik[0][0]

for t in range(T):
    if minn>listik[0][0]:
        minn = listik[0][0]
        print(t, "-", minn)
    if random.randint(0,2) == 0:
        SBX_crossing(pop, prob)
    else:
        сrossing(pop, prob)
    print("Поколение",t)

    listik.clear()
    for i in range(len(pop)-1):
        listik.append((f(pop[i], pop[i+1]),i))
        #print(listik[len(listik)-1][0])
    listik.append((f(pop[len(pop)-1], pop[0]),len(pop)-1))
    listik.sort(key=lambda x: x[0])
    #print(listik)
    #print(listik)
    print(listik[0][0])
    newpop = []
    for i in range(len(pop)):
        newpop.append(pop[listik[i][1]].copy())
    for i in range(len(pop)):
        pop[i] = newpop[i].copy()
    #k = f_visual(pop[0])

    if t>0 and t % 15 == 0:
        with open('D:/StudiaCODEEEE/сохры/Pong_results.txt', mode='w') as f2:
            for sss in range(len(pop)):
                f2.write("%s       " % sss)
                f2.write("\n")
                f2.writelines("%s   " % i for i in pop[sss])
                f2.write("\n")
                f2.write("\n")
                f2.write("\n")
        f2.close()
    

    if t >= 10000:
        print("--- %s seconds ---" % (time.time() - start_time))
        while True:
            input("Введите что-то: ")
            gg = f_visual(pop[0], pop[1])
            if (gg == 0):
                print("Смерть от удара в стену")
            if (gg == 1):
                print("Смерть по времени")
    #qsort(pop, len(pop))