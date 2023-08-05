import os
import random
def clear():
    import os
    if os.name == "posix":
        os.system('clear')
    elif os.name in ("nt", "dos", "ce"):
        os.system('CLS')
    else:
        print '\n' * 100
block = []
blockref = {0:" ", 1:"#"}
for i in xrange(50):
    block.append([])
    for j in xrange(30):
        block[i].append("0")
totx=len(block)
toty=len(block[0])
totp=2*(totx+toty)-4
tota=totx*toty
for i in xrange(totx):
    for j in xrange(toty):
        block[i][j] = random.randint(0,1)
class Life:
    def __init__(self, name, x, y, d, sym):
        self.name = name
        self.hp = 10
        self.ammo = 10
        self.x = x
        self.y = y
        self.dir = d
        self.sym = sym
    def __str__(self):
        return self.sym + " | HP: " + str(self.hp) + "/10 | Ammo: " + str(self.ammo) + "/10"
    def move(self, d):
        if d == 0 and self.y < toty-1 and block[self.x][self.y+1] != 1:
            self.y += 1
        if d == 1 and self.x > 0 and block[self.x-1][self.y] != 1:
            self.x -= 1
        if d == 2 and self.y > 0 and block[self.x][self.y-1] != 1:
            self.y -= 1
        if d == 3 and self.x < totx-1 and block[self.x+1][self.y] != 1:
            self.x += 1
    def shoot(self, d):
        if self.ammo > 0:
            self.ammo -= 1
            bullets.append(Bullet(self.x, self.y, d))
    def reload(self):
        self.ammo = 10
    def hurt(self):
        for i in bullets:
            if i.x == self.x and i.y == self.y:
                bullets.remove(i)
                self.hp -= 1
bullets = []
class Bullet:
    def __init__(self, x, y, d):
        self.x = x
        self.y = y
        self.d = d
    def __str__(self):
        return {0:"v", 1:"<", 2:"^", 3:">"}[self.d]
    def move(self):
        if self.d == 0:
            self.y += 1
        if self.d == 1:
            self.x -= 1
        if self.d == 2:
            self.y -= 1
        if self.d == 3:
            self.x += 1
def render():
    clear()
    ren = []
    for i in xrange(toty):
        ren.append([])
        for j in xrange(totx):
            ren[i].append(" ")
    for i in xrange(totx):
        for j in xrange(toty):
            ren[j][i]=blockref[block[i][j]]
    for i in players:
        ren[i.y][i.x] = i.sym
    for i in bullets:
        ren[i.y][i.x] = str(i)
    cn = ''
    for i in xrange(len(ren)):
        for j in ren[i]:
            cn += j
        if i < len(players)*2:
            cn += "  "
            if i%2:
                cn += str(players[(i-1)/2])
            else:
                cn += players[i/2].name
        cn += "\n"
    print cn
fail = 1
playern = 0
while fail == 1 or playern < 2 or playern > toty/2:
    fail = 0
    playern = raw_input("Number of Players: ")
    try:
        playern = int(playern)
    except:
        fail = 1
dis = (totp-4)/playern
cur = 0
players = []
prevname = [""]
prevsym = [" ", "#", ">", "v", "<", "^"]
for i in xrange(playern):
    name = ""
    while name in prevname:
        name = raw_input("Player " + str(i+1) + "'s Name: ")
    prevname.append(name)
    if cur < (totx/2)-1:
        x = totx/2 + cur
        y = 0
        d = 0
    elif cur < (totx/2)+toty-3:
        x = totx-1
        y = cur - (totx/2)
        d = 1
    elif cur < (totx/2)+toty+totx-5:
        x = (totx/2)+toty+totx-5 - cur
        y = toty-1
        d = 2
    elif cur < (totx/2)+(2*toty)+totx-7:
        x = 0
        y = (totx/2)+(2*toty)+totx-7 - cur
        d = 3
    else:
        x = cur - ((totx/2)+(2*toty)+totx-8)
        y = 0
        d = 4
    cur += dis
    sym = " "
    while (sym in prevsym) and len(sym)==1:
        sym = raw_input(name + "'s symbol: ")
    prevsym.append(sym)
    players.append(Life(name, x, y, d, sym))
for i in players:
    block[i.x][i.y] = 0
    if i.dir <> 0:
        block[i.x][i.y-1] = 0
    if i.dir <> 1:
        block[i.x+1][i.y] = 0
    if i.dir <> 2:
        block[i.x][i.y+1] = 0
    if i.dir <> 3:
        block[i.x-1][i.y] = 0
i = 0
while len(players)>1:
    render()
    s = 0
    while s == 0:
        m = raw_input(players[i].name + "'s move: ").lower()
        if m in ("w", "up", "^", "8"):
            players[i].move(2)
            s = 1
        if m in ("d", "right", ">", "6"):
            s = 1
            players[i].move(3)
        if m in ("s", "down", "v", "2"):
            s = 1
            players[i].move(0)
        if m in ("a", "left", "<", "4"):
            players[i].move(1)
            s = 1
        if m in (" ", "5", "shoot"):
            s = 1
            so = 0
            while so == 0:
                mo = raw_input("Direction: ").lower()
                if mo in ("w", "up", "^", "8"):
                    so = 1
                    players[i].shoot(2)
                if mo in ("d", "right", ">", "6"):
                    so = 1
                    players[i].shoot(3)
                if mo in ("s", "down", "v", "2"):
                    so = 1
                    players[i].shoot(0)
                if mo in ("a", "left", "<", "4"):
                    so = 1
                    players[i].shoot(1)
        if m in ("0", "e", "r", "reload"):
            s = 1
            players[i].reload()
        remove = []
    for j in xrange(len(bullets)):
        bullets[j].move()
        if bullets[j].x < 0 or bullets[j].x > totx-1 or bullets[j].y < 0 or bullets[j].y > toty-1:
            remove.append(bullets[j])
            continue
        if block[bullets[j].x][bullets[j].y] == 1:
            block[bullets[j].x][bullets[j].y] = 0
            remove.append(bullets[j])
            continue
        l = range(len(bullets))
        l.remove(j)
        for k in l:
            if bullets[k].x == bullets[j].x and bullets[k].y == bullets[j].y:
                block[bullets[k].x][bullets[k].y] = 0
                remove.append(bullets[k])
                remove.append(bullets[j])
                break
    for j in remove:
        try:
            bullets.remove(j)
        except:
            pass
    for j in players:
        j.hurt()
        if j.hp <= 0:
            players.remove(j)
    i += 1
    if i > len(players)-1:
        i = 0
print players[0].name + " wins!"
raw_input()
