import pygame as p
from Chess import ChessEngine, Compuhter


WIDTH = HEIGHT = 512
DIMENSION = 8
SQ_size = HEIGHT // DIMENSION
MAX_fps = 60
IMAGES = {}


def loadImages():
    pieces = ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR", "wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR", "bP", "wP"]
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("Chess/images/{}.png".format(piece)), (SQ_size, SQ_size))


def main():
    p.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    gs = ChessEngine.Gamestate()
    validMoves = gs.getValidMoves()
    moveMade = False # Отслеживаем когда был сделан не невозможный ход
    NeedAnime = False # надо ли анимировать ходы
    gameover = False # конец игры
    humanWhite = True # Белыми играет человек?
    humanBlack = True # Черными играет человек?
    loadImages()
    running = True  
    sq_selected = () # Отслеживаем выбранную клетку (tuple = (row, col))
    playerclicks = [] #Отслеживаем клики игрока (2 кортежа [(row, col), (row, col)])
    while running:
        isHumanMove = (gs.WhitetoMove and humanWhite) or (not gs.WhitetoMove and humanBlack)
        for e in p.event.get():


            # Нажатия мыши
            if e.type == p.QUIT:
                running  = False
            elif e.type == p.MOUSEBUTTONDOWN:
                if not gameover and isHumanMove:
                    location = p.mouse.get_pos()
                    col = location[0]//SQ_size
                    row = location[1]//SQ_size
                    if sq_selected == (row, col): # deselect
                        sq_selected = ()
                        playerclicks = []
                    elif gs.board[row][col] == "--" and len(playerclicks) < 1: #
                        sq_selected = ()
                        playerclicks = []
                    else:
                        sq_selected = (row, col)
                        playerclicks.append((sq_selected))
                        HighlightSquares(screen, gs, validMoves, sq_selected)
                    if len(playerclicks) == 2:
                        move = ChessEngine.Move(playerclicks[0], playerclicks[1], gs.board)
                        #print(move.getMovesNotation())
                        if move in validMoves:
                            gs.makeMove(move)
                            moveMade = True
                            NeedAnime = True
                        sq_selected = ()
                        playerclicks = []


            # Нажатие кнопок на клавиатуре
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z: # Отмена одного хода
                    gs.undoMove()
                    moveMade = True
                    NeedAnime = False
                    gameover = False
                if e.key == p.K_x: # Отмена двух ходов (для игры компьютером)
                    gs.undoMove()
                    gs.undoMove()
                    moveMade = True
                    NeedAnime = False
                    gameover = False
                if e.key == p.K_r: # reset game
                    gs = ChessEngine.Gamestate()
                    validMoves = gs.getValidMoves()
                    sq_selected = ()
                    playerclicks = []
                    moveMade = False
                    NeedAnime = False
                    gameover = False


    # Ходы компьютера
        if len(validMoves) != 0 and not gameover and not isHumanMove:
            AImove = Compuhter.getRandomMove(validMoves)
            gs.makeMove(AImove)
            moveMade = True
            NeedAnime = True

    # После кадого ходы обновляем список допустимых ходов
        if moveMade:
            if NeedAnime:
                Anime(gs.Log[-1], screen, gs.board, clock)
            validMoves = gs.getValidMoves()
            moveMade = False
            NeedAnime = False


        DrawGameState(screen, gs, validMoves, sq_selected)


        if gs.checkmate:
            gameover = True
            if gs.WhitetoMove:
                drawTEXT(screen, "Black wins by checkmate")
            else:
                drawTEXT(screen, "White wins by checkmate")
        if gs.PAT:
            gameover = True
            if gs.PAT:
                drawTEXT(screen, "Tie by the stalemate")


        clock.tick(MAX_fps)
        p.display.flip()


# Подсввечиваем возможные ходы
def HighlightSquares(screen, gs, validMoves, sqSelected):
    if sqSelected != ():
        row, col = sqSelected
        if gs.board[row][col][0] == ("w" if gs.WhitetoMove else "b"):
            s = p.Surface((SQ_size, SQ_size))
            s.set_alpha(100)
            s.fill(p.Color("red"))
            screen.blit(s, (col*SQ_size, row*SQ_size))
            s.fill(p.Color("green"))
            for move in validMoves:
                if move.startRow == row and move.startCol == col:
                    p.draw.circle(screen,
                                  "green",
                                  (move.endCol * SQ_size + SQ_size / 2, move.endRow * SQ_size + SQ_size / 2)
                                  , SQ_size / 4
                                  )


# Рисуем доску и фигуры
def DrawGameState(screen, gs, validMoves, sqSelected):
    drawBoard(screen)
    HighlightSquares(screen, gs, validMoves, sqSelected)
    Highlight_last_move(screen, gs)
    drawPieces(screen, gs.board)


# Рисуем доску
def drawBoard(screen):
    global colors
    colors = [p.Color("white"), p.Color("lightblue")]
    for row in range(DIMENSION):
        for col in range(DIMENSION):
            color = colors[((row + col) % 2)]
            p.draw.rect(screen, color, (col*SQ_size, row*SQ_size, SQ_size, SQ_size))


# Рисуем фигуры на доске
def drawPieces(screen, board):
    for row in range(DIMENSION):
        for col in range(DIMENSION):
            piece = board[row][col]
            if piece != "--":
                screen.blit(IMAGES[piece], (col*SQ_size, row*SQ_size, SQ_size, SQ_size))


# Animating a move
def Anime(move, screen, board, clock):
    global colors
    dR = move.endRow - move.startRow
    dC = move.endCol - move.startCol
    FrameperSquare = 10
    frameCount = (abs(dR) + abs(dC)) * FrameperSquare
    for i in range(frameCount + 1):
        row, col = (move.startRow + dR * (i / frameCount), move.startCol + dC * (i / frameCount))
        drawBoard(screen)
        drawPieces(screen, board)
        # Удаляем фигуру из её конечного положения
        color = colors[(move.endRow + move.endCol) % 2]
        endSquare = (move.endCol*SQ_size, move.endRow*SQ_size, SQ_size, SQ_size)
        p.draw.rect(screen, color, endSquare)
        # Рисуем на её месте фигуру, которая там была
        if move.pieceCaptured != "--":
            screen.blit(IMAGES[move.pieceCaptured], endSquare)
        # Рисуем фигуру, которая делает ход на векторе соединяющем начало и конец хода
        screen.blit(IMAGES[move.pieceMoved], (col*SQ_size, row*SQ_size, SQ_size, SQ_size))
        p.display.flip()
        clock.tick(MAX_fps)


# Отрисовка сообщения о конце игры
def drawTEXT(screen, text):
    font = p.font.SysFont("TimesNewRoman", 32, True, True)
    label = font.render(text, True, p.Color("red"))
    labelLocation = p.Rect(0,0,WIDTH,HEIGHT).move(WIDTH/2-label.get_width()/2, HEIGHT/2-label.get_height()/2)
    screen.blit(label, labelLocation)
    label2 = font.render(text, True, p.Color("black"))
    labelLocation2 = p.Rect(0, 0, WIDTH, HEIGHT).move(WIDTH/2-label.get_width()/2, HEIGHT/2-label.get_height()/2)
    labelLocation2 = labelLocation2.move(2,2)
    screen.blit(label2, labelLocation2)

#Подсветка последнего хода
def Highlight_last_move(screen, gs):
    global colors
    if len(gs.Log) != 0:
        move = gs.Log[-1]
        end_col = move.endCol
        end_row = move.endRow
        start_col = move.startCol
        start_row = move.startRow
        s = p.Surface((SQ_size, SQ_size))
        s.fill(p.Color("yellow"))
        s.set_alpha(100)
        screen.blit(s, (end_col * SQ_size, end_row * SQ_size))
        screen.blit(s, (start_col * SQ_size, start_row * SQ_size))

# Точка входа
if __name__ == "__main__":
    main()
