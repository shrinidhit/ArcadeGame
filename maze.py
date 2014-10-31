#
# MAZE
# 
# Example game
#
# Version without baddies running around
#


from graphics import *

LEVEL_WIDTH = 35
LEVEL_HEIGHT = 20    

CELL_SIZE = 24
WINDOW_WIDTH = CELL_SIZE*LEVEL_WIDTH
WINDOW_HEIGHT = CELL_SIZE*LEVEL_HEIGHT


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
        self._y = self._y + 1
        self._img.move(0,1*CELL_SIZE)

    def current_pos(self):
        return self.level_coord(self._x, self._y)

    def move (self,dx,dy):
        tx = self._x + dx
        ty = self._y + dy
        if tx >= 0 and ty >= 0 and tx < LEVEL_WIDTH and ty < LEVEL_HEIGHT:
            if self.level_coord(tx,ty) != 1:
                #Original Move
                self._x = tx
                self._y = ty
                self._img.move(dx*CELL_SIZE,dy*CELL_SIZE)
                #If player is in air and air is below player:
                while self.level_coord(self._x, self._y + 1) == 0 and self.current_pos() == 0:
                    self.gravity()
                #If a rope is below a player:
                if self.level_coord(self._x, self._y + 1) == 3:
                    self.gravity()

class Player (Character):
    def __init__ (self,x,y,window,level):
        Character.__init__(self,'android.gif',x,y,window,level)

    def at_exit (self):
        return (self._y == 0)

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

def build_exit(level):
    level[index(34,0)] = 2
    level[index(34,1)] = 2
    level[index(34,2)] = 2

def is_move_valid(player,dx,dy):
    #Getting player and transform coordinates
    playerx, playery = player.loc()
    tx = playerx + dx
    ty = playery + dy

    def next_block(x, y, xdir, ydir):
        return player.level_coord(x - xdir, y - ydir)

    #Checking if transformed coord not a brick or air:
    if player.level_coord(tx,ty) not in [1,0]:
        return True
    #If tranfsormed coord is air
    elif player.level_coord(tx,ty) == 0:
        #If brick is below:
        if next_block(tx, ty, 0, -1):
            return True
        #If brick is not below but moving right,left,or down and currently on ground
        if dy != -1:
            return True
    return False

#0 == Empty
#1 == Brick
#2 == Ladder
#3 == Rope
#4 == Gold

def create_level (num):
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
    # use this instead of Rectangle below for nicer screen
    brick = 'brick.gif'
    ladder = 'ladder.gif'
    rope = 'rope.gif'
    gold = 'gold.gif'

    #Map:
    Tiles = {1: brick, 2: ladder, 3: rope, 4: gold}

    #Returning image
    def image (sx,sy,what):
        return Image(Point(sx+CELL_SIZE/2,sy+CELL_SIZE/2),what)

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


MOVE = {
    'Left': (-1,0),
    'Right': (1,0),
    'Up' : (0,-1),
    'Down' : (0,1)
}

DIG = {
    'a':(-1,1,-1,0),
    'z':(1,1,1,0)
}

def main ():

    window = GraphWin("Maze", WINDOW_WIDTH+20, WINDOW_HEIGHT+20)

    rect = Rectangle(Point(5,5),Point(WINDOW_WIDTH+15,WINDOW_HEIGHT+15))
    rect.setFill('sienna')
    rect.setOutline('sienna')
    rect.draw(window)
    rect = Rectangle(Point(10,10),Point(WINDOW_WIDTH+10,WINDOW_HEIGHT+10))
    rect.setFill('white')
    rect.setOutline('white')
    rect.draw(window)

    level = create_level(1)

    elements = create_screen(level,window)

    p = Player(10,18,window,level)

    baddie1 = Baddie(5,1,window,level,p)
    baddie2 = Baddie(10,1,window,level,p)
    baddie3 = Baddie(15,1,window,level,p)

    while not p.at_exit():
        key = window.checkKey()
        if key == 'q':
            window.close()
            exit(0)
        if key in MOVE:
            (dx,dy) = MOVE[key]
            if is_move_valid(p, dx, dy):
                p.move(dx,dy)
        if key in DIG:
            (xd,yd,xn,yn) = DIG[key]
            p.dig(xd,yd,xn,yn,elements)

        exit_built = False
        if check_gold(level) == False and exit_built == False:
            exit_built = True
            build_exit(level)
            create_screen(level,window)

        # baddies should probably move here

    won(window)

if __name__ == '__main__':
    main()
