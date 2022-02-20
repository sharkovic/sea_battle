from random import randint


class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __str__(self):
        return f"({self.x}, {self.y})"


class BoardException(Exception):
    pass


class BoardOutExcept(BoardException):
    def __str__(self):
        return "Вы пытаетесь выстрелить за пределы доски"


class ShootRepeatExcept(BoardException):
    def __str__(self):
        return "Вы сюда уже стреляли"


class BoardWrongShipException(BoardException):
    pass


class Ship:
    def __init__(self, length_and_health, nose, orient):
        self.length_and_health = length_and_health
        self.nose = nose
        self.orient = orient

    @property
    def coord(self):
        coord_list = []
        for i in range(self.length_and_health):
            x = self.nose.x
            y = self.nose.y
            if self.orient == 1:
                x += i
            elif self.orient == 0:
                y += i
            coord_list.append(Dot(x, y))
        return coord_list

    def shooten(self, shot):
        return shot in self.coord


class Board:
    def __init__(self, hid=False, size_board=6):
        self.size_board = size_board
        self.status = [["0"] * self.size_board for _ in range(self.size_board)]
        self.list_boards = []
        self.list_busy_boards = []
        self.hid = hid
        self.boards_life = 0

    def add_ship(self, ship):

        for coord in ship.coord:
            if self.out(coord) or coord in self.list_busy_boards:
                raise BoardWrongShipException()

        for coord in ship.coord:
            self.status[coord.x][coord.y] = "■"
            self.list_busy_boards.append(coord)

        self.list_boards.append(ship)
        self.contour(ship)

    def contour(self, ship, verb=False):
        near = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]
        for coord in ship.coord:
            for dx, dy in near:
                cur = Dot(coord.x + dx, coord.y + dy)
                if not (self.out(cur)) and cur not in self.list_busy_boards:
                    if verb:
                        self.status[cur.x][cur.y] = "."
                    self.list_busy_boards.append(cur)

    def __repr__(self):
        board = "  |"
        for i in range(self.size_board):
            board += f" {i + 1} |"
        for i, row in enumerate(self.status):
            board += f"\n{i + 1} | " + " | ".join(row) + " |"

        if self.hid:
            board = board.replace("■", "0")
        return board

    def out(self, coord):
        return not ((0 <= coord.x < self.size_board) and (0 <= coord.y < self.size_board))

    def shot(self, coord):
        if self.out(coord):
            raise BoardOutExcept()

        if coord in self.list_busy_boards:
            raise BoardOutExcept()

        self.list_busy_boards.append(coord)

        for ship in self.list_boards:
            if coord in ship.coord:
                ship.length_and_health -= 1
                self.status[coord.x][coord.y] = "X"
                if ship.length_and_health == 0:
                    self.boards_life += 1
                    self.contour(ship, verb=True)
                    print("Корабль уничтожен!")
                    return False
                else:
                    print("Корабль ранен!")
                    return True

        self.status[coord.x][coord.y] = "T"
        print("Мимо!")
        return False

    def begin(self):
        self.list_busy_boards = []


class Player:
    def __init__(self, board, enemy):
        self.board = board
        self.enemy = enemy

    def ask(self):
        raise NotImplementedError()

    def move(self):
        while True:
            try:
                target = self.ask()
                repeat = self.enemy.shot(target)
                return repeat
            except BoardOutExcept as e:
                print(e)


class AI(Player):
    def ask(self):
        coord = Dot(randint(0, 5), randint(0, 5))
        print(f"Ход компьютера: {coord.x + 1} {coord.y + 1}")
        return coord


class User(Player):
    def ask(self):
        while True:
            cords = input("Ваш ход: ").split()

            if len(cords) != 2:
                print(" Введите 2 координаты! ")
                continue

            x, y = cords

            if not (x.isdigit()) or not (y.isdigit()):
                print(" Введите числа! ")
                continue

            x, y = int(x), int(y)

            return Dot(x - 1, y - 1)


class Game:
    def __init__(self, size=6):
        self.size = size
        player = self.random_board()
        comp = self.random_board()
        comp.hid = True

        self.ai = AI(comp, player)
        self.us = User(player, comp)

    def random_board(self):
        board = None
        while board is None:
            board = self.random_place()
        return board

    def random_place(self):
        lens = [3, 2, 2, 1, 1, 1, 1]
        board = Board(size_board=self.size)
        attempts = 0
        for length in lens:
            while True:
                attempts += 1
                if attempts > 2000:
                    return None
                ship = Ship(length, Dot(randint(0, self.size), randint(0, self.size)), randint(0, 1))
                try:
                    board.add_ship(ship)
                    break
                except BoardWrongShipException:
                    pass
        board.begin()
        return board

    def greet(self):
        print("-------------------")
        print("  Приветсвуем вас  ")
        print("      в игре       ")
        print("    морской бой    ")
        print("-------------------")
        print(" формат ввода: x y ")
        print(" x - номер строки  ")
        print(" y - номер столбца ")

    def loop(self):
        num = 0
        while True:
            print("-" * 20)
            print("Доска пользователя:")
            print(self.us.board)
            print("-" * 20)
            print("Доска компьютера:")
            print(self.ai.board)
            if num % 2 == 0:
                print("-" * 20)
                print("Ходит пользователь!")
                repeat = self.us.move()
            else:
                print("-" * 20)
                print("Ходит компьютер!")
                repeat = self.ai.move()
            if repeat:
                num -= 1

            if self.ai.board.boards_life == 7:
                print("-" * 20)
                print("Пользователь выиграл!")
                break

            if self.us.board.boards_life == 7:
                print("-" * 20)
                print("Компьютер выиграл!")
                break
            num += 1

    def start(self):
        self.greet()
        self.loop()


game = Game()
print(game.start())