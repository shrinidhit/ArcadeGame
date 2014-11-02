# Shrinidhi Thirumalai and Haley Pelletier
# Gold Runner Maze Game

#Imports
from graphics import *
import random
import time

#Global Variables
LEVEL_WIDTH = 35
LEVEL_HEIGHT = 20    
CELL_SIZE = 24
WINDOW_WIDTH = CELL_SIZE*LEVEL_WIDTH
WINDOW_HEIGHT = CELL_SIZE*LEVEL_HEIGHT


#Basic Functions
def screen_pos (x,y):
    return (x*CELL_SIZE+10,y*CELL_SIZE+10)

def screen_pos_index (index):
    x = index % LEVEL_WIDTH
    y = (index - x) / LEVEL_WIDTH
    return screen_pos(x,y)

def pos_index (index):
    x = index % LEVEL_WIDTH
    y = (index-x)/LEVEL_WIDTH
    return (x,y)

def index (x,y):
    return x + (y*LEVEL_WIDTH)

def image (sx,sy,what):
    """Returning Image"""
    return Image(Point(sx+CELL_SIZE/2,sy+CELL_SIZE/2),what)

#Classes
class Character (object):
    def __init__ (self,pic,x,y,window,level):
        (sx,sy) = screen_pos(x,y)
        self._img = Image(Point(sx+CELL_SIZE/2,sy+CELL_SIZE/2+2),pic)
        self._window = window
        self._img.draw(window)
        self._x = x
        self._y = y
        self._level = level

    def loc(self):
        return (self._x, self._y)

    def level(self):
        return self._level

    def level_coord(self,x,y):
        return self._level[index(x,y)]

    def same_loc (self,x,y):
        return (self._x == x and self._y == y)

    def gravity(self):
        #Falling one unit:
        def fall(self):
            self._y = self._y + 1
            self._img.move(0,1*CELL_SIZE)
        #Falls while player is in air or gold and air is below player:
        while self._y < LEVEL_HEIGHT - 1:
            if (self.level_coord(self._x, self._y + 1) in [0,4]) and (self.current_pos() == 0):
                fall(self)
            else: 
                break
        #Falls one unit if a rope is below a player:
        if (self._y < LEVEL_HEIGHT - 1) and (self.level_coord(self._x, self._y + 1) == 3):
            fall(self)


    def current_pos(self):
        return self.level_coord(self._x, self._y)

    def is_move_valid(self,dx,dy):
        #Getting player and transform coordinates
        x, y = self.loc()
        tx = x + dx
        ty = y + dy

        def next_block(x, y, xdir, ydir):
            return self.level_coord(x - xdir, y - ydir)

        #Checking if transformed coord not a brick or air:
        if self.level_coord(tx,ty) not in [1,0]:
            return True
        #If tranfsormed coord is air
        elif self.level_coord(tx,ty) == 0:
            #If brick is below:
            if next_block(tx, ty, 0, -1):
                return True
            #If brick is not below but moving right,left,or down and currently on ground
            if dy != -1:
                return True
        return False

    def move (self,dx,dy):
        tx = self._x + dx
        ty = self._y + dy
        if tx >= 0 and ty >= 0 and tx < LEVEL_WIDTH and ty < LEVEL_HEIGHT:
            if self.level_coord(tx,ty) != 1:
                #Original Move
                self._x = tx
                self._y = ty
                self._img.move(dx*CELL_SIZE,dy*CELL_SIZE)
                #Gravity
                self.gravity()

class Player (Character):
    def __init__ (self,x,y,window,level):
        Character.__init__(self,'android.gif',x,y,window,level)

    def at_exit (self):
        return (self._y == 0)

    def pickup_gold (self,elts):
        if self._level[index(self._x,self._y)] == 4:
            elts[self._x][self._y].undraw()
            self._level[index(self._x,self._y)] = 0

    def dig (self,xd,yd,xn,yn,elts):
        dig_x = self._x + xd
        dig_y = self._y + yd
        near_x = self._x + xn
        near_y = self._y + yn

        dig_loc = self._level[index(dig_x,dig_y)]
        near_loc = self._level[index(near_x,near_y)]

        if dig_loc == 1 and near_loc == 0:
            elts[dig_x][dig_y].undraw()
            self._level[index(dig_x,dig_y)] = 0


class Baddie (Character):
    def __init__ (self,x,y,window,level,player):
        Character.__init__(self,'red.gif',x,y,window,level)
        self._player = player

    def event(self,queue):
        def compare(x1,x2):
            if x1>x2:
                return 1
            if x1<x2:
                return -1
        #First, prioritize y position to try moving in y direction    
        if self._player._y != self._y:
            ydir = compare(self._player._y, self._y)
            #try y motion
            if self.is_move_valid(0, ydir):
                self.move(0, ydir)
            elif self.is_move_valid(0, -ydir):
                self.move(0, -ydir)
            elif self.is_move_valid(1, 0):
                self.move(1,0)
            else:
                self.move(-1,0)
        #If y position is equal, priorotize x motion
        elif self._player._x != self._x:
            xdir = compare(self._player._x, self._x)
            if self.is_move_valid(xdir, 0):
                self.move(xdir, 0)
            if self.is_move_valid(-xdir, 0):
                self.move(-xdir, 0)
            elif self.is_move_valid(0,1):
                self.move(0,1)
            else:
                self.move(0,-1)
        else:
            lost(self._window)
        #Reads event to list after moving
        time.sleep(.001)
        queue.enqueue(1000,self)


class Event_Queue(object):
    def __init__(self):
        self.queue = {}

    def enqueue(self,when,obj):
        self.queue[obj] = when

    def dequeue_if_ready(self):
        for key,val in self.queue.iteritems():
            if val == 0:
                key.event(self)
            else:
                self.queue[key] -= 1

#Functions
def lost (window):
    t = Text(Point(WINDOW_WIDTH/2+10,WINDOW_HEIGHT/2+10),'YOU LOST!')
    t.setSize(36)
    t.setTextColor('red')
    t.draw(window)
    window.getKey()
    exit(0)

def won (window):
    t = Text(Point(WINDOW_WIDTH/2+10,WINDOW_HEIGHT/2+10),'YOU WON!')
    t.setSize(36)
    t.setTextColor('red')
    t.draw(window)
    window.getKey()
    exit(0)

def check_gold(level):
    gold = False
    for j in range(LEVEL_HEIGHT):
        for i in range(LEVEL_WIDTH):
            if level[index(i,j)] == 4:
                gold = True
                break
    return gold

def build_exit(level,elts,player,win):
    ladder = 'ladder.gif'
    positions = [(34,0), (34,1), (34,2)]
    #Draw Ladder
    for pos in positions:
        level[index(pos[0],pos[1])] = 2
        tile = screen_pos(pos[0], pos[1])
        image(tile[0], tile[1], ladder).draw(win)
    #Redraw Player to be on top
    player._img.undraw()
    player._img.draw(win)

def create_level (num):
    #0 == Empty, 1 == Brick, 2 == Ladder, 3 == Rope, 4 == Gold
    screen = []
    screen.extend([1,1,1,1,1,1,1,1,1,1,1,1,1,2,0,0,0,0,0,0,0,2,1,1,1,1,1,1,1,1,1,1,1,1,0])
    screen.extend([1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0])
    screen.extend([1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,2,1,0,0,0,0,0,0,0,0,0,0,4,0,0,0,0,0])
    screen.extend([1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,2,1,1,1,1,1,1,1,1,1,1,1,1,1,1,2,1,1])
    screen.extend([0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2,0,0,0,0,0,0,0,1,2,1,0,0,0,1,2,0,1])
    screen.extend([0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2,0,0,0,0,0,0,0,0,2,0,0,0,0,1,1,1,1])
    screen.extend([3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,2,0,0,0,0,0,0,0,0,2,0,0,0,0,3,3,3,3])
    screen.extend([2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,2,1,0,0,0,0,0,0,0,2,0,0,0,0,0,0,0,0])
    screen.extend([2,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,2,1,1,1,1,1,1,1,1])
    screen.extend([2,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,0,0,0,0,0,0,2,3,3,3,3,3,3,3,2])
    screen.extend([2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2,0,0,0,0,0,0,0,2])
    screen.extend([2,0,0,0,0,0,3,3,0,0,0,0,0,0,3,3,0,0,0,0,0,0,0,0,0,0,2,0,0,0,0,0,0,0,2])
    screen.extend([2,0,1,1,1,1,0,0,1,1,1,1,1,1,0,0,1,2,1,0,0,0,0,3,3,3,2,0,0,1,1,1,1,1,2])
    screen.extend([2,0,1,0,0,1,0,0,1,0,0,0,0,1,0,0,1,2,1,1,1,1,1,1,0,0,2,0,0,1,0,0,0,1,2])
    screen.extend([2,0,1,4,4,1,0,0,1,0,4,4,4,1,0,0,1,2,0,4,4,4,0,1,0,0,2,0,0,1,4,4,4,1,2])
    screen.extend([2,0,1,1,1,1,0,0,1,2,1,1,1,1,0,0,1,1,1,1,1,1,1,1,0,0,2,0,0,1,1,1,1,1,2])
    screen.extend([2,0,3,3,3,3,3,3,3,2,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,2,3,3,3,3,3,3,3,2])
    screen.extend([1,0,0,0,0,0,0,0,0,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2,0,0,0,0,0,0,0,1])
    screen.extend([1,0,0,0,0,0,0,0,0,2,0,0,0,0,0,0,0,0,0,0,4,0,0,0,0,0,2,0,0,0,0,0,0,0,1])
    screen.extend([1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1])
    return screen

def create_screen (level,window):
    #Intializing images
    brick = 'brick.gif'
    ladder = 'ladder.gif'
    rope = 'rope.gif'
    gold = 'gold.gif'
    #Map:
    Tiles = {1: brick, 2: ladder, 3: rope, 4: gold}
    #List of screen elements:
    elements = [[None for i in range(20)] for j in range(35)]
    #Loop to create map
    for (index,cell) in enumerate(level):
        if cell != 0:
            (sx,sy) = screen_pos_index(index)
            (px,py) = pos_index(index)
            elt = image (sx,sy,Tiles[cell])
            elements[px][py] = elt
            elt.draw(window)
    return elements

def create_baddies(window, level, player):
    positions = [(5,2),(10,2), (15,2)]
    baddies = []
    for pos in positions:
        baddies.append(Baddie(pos[0],pos[1],window,level,player))
    return baddies

def create_window():
    #Create Window
    window = GraphWin("Maze", WINDOW_WIDTH+20, WINDOW_HEIGHT+20)
    #Sienna Border
    rect = Rectangle(Point(5,5),Point(WINDOW_WIDTH+15,WINDOW_HEIGHT+15))
    rect.setFill('sienna')
    rect.setOutline('sienna')
    rect.draw(window)
    #White Inside
    rect = Rectangle(Point(10,10),Point(WINDOW_WIDTH+10,WINDOW_HEIGHT+10))
    rect.setFill('white')
    rect.setOutline('white')
    rect.draw(window)
    return window

#Main Game:
def main ():
    #Initializing Variables:
    MOVE = {'Left': (-1,0), 'Right': (1,0), 'Up' : (0,-1), 'Down' : (0,1)}
    DIG = {'a':(-1,1,-1,0), 'z':(1,1,1,0)}
    exit_built = False

    #Starting Level:
        #Creating Window:
    window = create_window()
        #Creating Level
    level = create_level(1)
    elements = create_screen(level,window)
        #Creating Event Queu
    queue = Event_Queue()
        #Creating Characters
    p = Player(10,18,window,level)
    baddies = create_baddies(window, level, p)
        #Adding objects to Queu
    for baddie in baddies:
        queue.enqueue(1000,baddie)

    #Running Game Loop:
    while not p.at_exit():
        #Get Key Input:
        key = window.checkKey()
        #dig, move, or quit:
        if key == 'q':
            window.close()
            exit(0)
        if key in MOVE:
            (dx,dy) = MOVE[key]
            if p.is_move_valid(dx, dy):
                p.move(dx,dy)
        if key in DIG:
            (xd,yd,xn,yn) = DIG[key]
            p.dig(xd,yd,xn,yn,elements)
        #Pick up Gold:
        p.pickup_gold(elements)  
        #Performes Queu Action:  
        queue.dequeue_if_ready()
        #Building Exit:
        if check_gold(level) == False and exit_built == False:
            exit_built = True
            build_exit(level,elements,p,window)

    #Win Sequence:        
    won(window)

if __name__ == '__main__':
    main()
