import numpy as np


class Gamestate:
    def __init__(self):
        self.board = np.array([
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bP", "bP", "bP", "bP", "bP", "bP", "bP", "bP"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wP", "wP", "wP", "wP", "wP", "wP", "wP", "wP"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]
        ])
        self.MoveFunctions = {
            "P": self.getPawnMoves,
            "R": self.getRookMoves,
            "N": self.getKnightMoves,
            "B": self.getBishopMoves,
            "Q": self.getQueenMoves,
            "K": self.getKingMoves
        }
        self.WhitetoMove = True
        self.Log = []
        self.WhiteKingLocation = (7, 4)
        self.BlackKingLocation = (0, 4)
        self.checkmate = False
        self.PAT = False
        self.WhiteKingMoved = False
        self.BlackKingMoved = False


    # Делаем ход на доске
    def makeMove(self, move):
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.Log.append(move) # log the moves
        self.WhitetoMove = not self.WhitetoMove
        if move.pieceMoved == "bK":
            self.BlackKingLocation = (move.endRow, move.endCol)
            self.BlackKingMoved = True
        elif move.pieceMoved == "wK":
            self.WhiteKingLocation = (move.endRow, move.endCol)
            self.WhiteKingMoved = True
        if move.isPromotion:
            self.board[move.endRow][move.endCol] = move.pieceMoved[0] + "Q"
        if move.isPassant:
            self.board[move.startRow][move.endCol] = "--"
            self.board[move.endRow][move.endCol] = move.pieceMoved
        if move.isCastling:
            if move.pieceMoved[0] == "w":
                self.WhiteKingMoved = True
            else:
                self.BlackKingMoved = True
            self.board[move.startRow][move.endCol] = "--"
            self.board[move.endRow][move.endCol] = move.pieceMoved
            if (move.startCol - move.endCol) == 2:
                self.board[move.startRow][0] = "--"
                self.board[move.startRow][move.endCol + 1] = move.pieceMoved[0] + "R"
            else:
                self.board[move.startRow][7] = "--"
                self.board[move.startRow][move.endCol - 1] = move.pieceMoved[0] + "R"


    # Отменяем последний ход
    def undoMove(self):
        if len(self.Log) != 0:
            self.checkmate = False
            self.PAT = False
            move = self.Log.pop()
            if move.isCastling:
                if move.pieceMoved[0] == "w":
                    self.WhiteKingMoved = False
                else:
                    self.BlackKingMoved = False
                self.board[move.startRow][move.startCol] = move.pieceMoved
                self.board[move.endRow][move.endCol] = "--"
                if (move.startCol - move.endCol) == 2:
                    self.board[move.startRow][0] = move.pieceMoved[0] + "R"
                    self.board[move.startRow][move.endCol + 1] = "--"
                else:
                    self.board[move.startRow][7] = move.pieceMoved[0] + "R"
                    self.board[move.startRow][move.endCol - 1] = "--"
            elif move.isPassant:
                self.board[move.startRow][move.startCol] = move.pieceMoved
                self.board[move.endRow][move.endCol] = move.pieceCaptured
                if self.WhitetoMove:
                    self.board[move.startRow][move.endCol] = "wP"
                else:
                    self.board[move.startRow][move.endCol] = "bP"
            else:
                self.board[move.startRow][move.startCol] = move.pieceMoved
                self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.WhitetoMove = not self.WhitetoMove
            if move.pieceMoved == "bK":
                self.BlackKingLocation = (move.startRow, move.startCol)
                self.BlackKingMoved = False
            elif move.pieceMoved == "wK":
                self.WhiteKingLocation = (move.startRow, move.startCol)
                self.WhiteKingMoved = False



    # Находим все возможные ходы учитывая шахи
    def getValidMoves(self):
        # Посмотреть все возоможные ходы
        moves = self.getAllPossibleMoves()
        # Сделать каждый
        for i in range(len(moves) - 1, -1 , -1):
            self.makeMove(moves[i])
            self.WhitetoMove = not self.WhitetoMove
            # Посмотреть все ходы противника
            # Проверить может ли он съесть короля, если да, то удалить этот ход из возможных)
            if self.inCheck():
                moves.remove(moves[i])
            self.WhitetoMove = not self.WhitetoMove
            self.undoMove()
        self.LongCastlePossible(moves)
        self.ShortCastlePossible(moves)
        if len(moves) == 0:
            if self.inCheck():
                self.checkmate = True
                #print("MATE")
            else:
                self.PAT = True
                #print("PAT")
        return moves


    # проверить стоит ли шах текущему игроку
    def inCheck(self):
        if self.WhitetoMove:
            return self.squareUnderAttack(self.WhiteKingLocation[0], self.WhiteKingLocation[1])
        else:
            return self.squareUnderAttack(self.BlackKingLocation[0], self.BlackKingLocation[1])


    # Находится ли под ударом клетка (row , col)
    def squareUnderAttack(self , row, col):
        self.WhitetoMove = not self.WhitetoMove
        oppMoves = self.getAllPossibleMoves()
        self.WhitetoMove = not self.WhitetoMove
        for i in range(len(oppMoves)):
            if oppMoves[i].endRow == row and oppMoves[i].endCol == col:
                return True
        return False


    # Оптимизированная функция для проверки рокировок (вместо нескольких раз генерации всех ходов getAllPossibleMoves())
    def squaresUnderAttack(self , squares):
        self.WhitetoMove = not self.WhitetoMove
        oppMoves = self.getAllPossibleMoves()
        self.WhitetoMove = not self.WhitetoMove
        for i in range(len(oppMoves)):
            for j in range(len(squares)):
                if oppMoves[i].endRow == squares[j][0] and oppMoves[i].endCol == squares[j][1]:
                    return True
        return False


    # Находим все возможные ходы не учитывая шахи
    def getAllPossibleMoves(self):
        moves = []
        for row in range(len(self.board)):
            for col in range(len(self.board[row])):
                PieceColor = self.board[row][col][0]
                if (PieceColor == "w" and self.WhitetoMove) or (PieceColor == "b" and not self.WhitetoMove):
                    piece = self.board[row][col][1]
                    self.MoveFunctions[piece](row, col, moves)
        return moves


    # Находим все возможные ходы для пешки в зависимости от положения на доске и добавляем их в массив moves
    def getPawnMoves(self, row, col, moves):
        if self.WhitetoMove:
            # Ходы вперед
            if self.board[row-1][col] == "--":
                moves.append(Move((row, col), (row-1, col), self.board))
                if row == 6 and self.board[row-2][col] == "--":
                    moves.append(Move((row, col), (row-2, col), self.board))
            # Взятие
            if col - 1 >= 0:
                if self.board[row-1][col-1][0] == "b":
                    moves.append(Move((row, col), (row-1, col-1), self.board))
            if col + 1 <= 7:
                if self.board[row-1][col+1][0] == "b":
                    moves.append(Move((row, col), (row-1, col+1), self.board))
            # Взятие на проходе
            if len(self.Log) != 0:
                if self.Log[-1].pieceMoved == "bP" and self.Log[-1].startRow == 1 and self.Log[-1].endRow == 3 and self.Log[-1].endCol == col + 1 and row == 3:
                    moves.append(Move((row, col), (row-1, col+1), self.board))
                if self.Log[-1].pieceMoved == "bP" and self.Log[-1].startRow == 1 and self.Log[-1].endRow == 3 and self.Log[-1].endCol == col - 1 and row == 3:
                    moves.append(Move((row, col), (row-1, col-1), self.board))
        else:
            # Ходы вперед
            if self.board[row+1][col] == "--":
                moves.append(Move((row, col), (row+1, col), self.board))
                if row == 1 and self.board[row+2][col] == "--":
                    moves.append(Move((row, col), (row+2, col), self.board))
            # Взятие
            if col - 1 >= 0:
                if self.board[row + 1][col - 1][0] == "w":
                    moves.append(Move((row, col), (row + 1, col - 1), self.board))
            if col + 1 <= 7:
                if self.board[row + 1][col + 1][0] == "w":
                    moves.append(Move((row, col), (row + 1, col + 1), self.board))
            # Взятие на проходе
            if len(self.Log) != 0:
                if self.Log[-1].pieceMoved == "wP" and self.Log[-1].startRow == 6 and self.Log[-1].endRow == 4 and self.Log[-1].endCol == col + 1 and row == 4:
                    moves.append(Move((row, col), (row+1, col+1), self.board))
                if self.Log[-1].pieceMoved == "wP" and self.Log[-1].startRow == 6 and self.Log[-1].endRow == 4 and self.Log[-1].endCol == col - 1 and row == 4:
                    moves.append(Move((row, col), (row+1, col-1), self.board))


    # Находим все возможные ходы для ладьи в зависимости от положения на доске и добавляем их в массив moves
    def getRookMoves(self, row, col, moves):
        if self.WhitetoMove:
            for ColCounter in range(1,8 - col):
                if self.board[row][col + ColCounter] == "--":
                    moves.append(Move((row, col), (row, col + ColCounter), self.board))
                elif self.board[row][col + ColCounter][0] == "w":
                    break
                elif self.board[row][col + ColCounter][0] == "b":
                    moves.append(Move((row, col), (row, col + ColCounter), self.board))
                    break
            for ColCounter in range(1, col + 1):
                if self.board[row][col - ColCounter] == "--":
                    moves.append(Move((row, col), (row, col - ColCounter), self.board))
                elif self.board[row][col - ColCounter][0] == "w":
                    break
                elif self.board[row][col - ColCounter][0] == "b":
                    moves.append(Move((row, col), (row, col - ColCounter), self.board))
                    break
            for RowCounter in range(1, 8 - row):
                if self.board[row + RowCounter][col] == "--":
                    moves.append(Move((row, col), (row + RowCounter, col), self.board))
                elif self.board[row + RowCounter][col][0] == "w":
                    break
                elif self.board[row + RowCounter][col][0] == "b":
                    moves.append(Move((row , col), (row + RowCounter, col), self.board))
                    break
            for RowCounter in range(1, row + 1):
                if self.board[row - RowCounter][col] == "--":
                    moves.append(Move((row, col), (row - RowCounter, col), self.board))
                elif self.board[row - RowCounter][col][0] == "w":
                    break
                elif self.board[row - RowCounter][col][0] == "b":
                    moves.append(Move((row, col), (row - RowCounter, col), self.board))
                    break
        else:
            for ColCounter in range(1, 8 - col):
                if self.board[row][col + ColCounter] == "--":
                    moves.append(Move((row, col), (row, col + ColCounter), self.board))
                elif self.board[row][col + ColCounter][0] == "b":
                    break
                elif self.board[row][col + ColCounter][0] == "w":
                    moves.append(Move((row, col), (row, col + ColCounter), self.board))
                    break
            for ColCounter in range(1, col + 1):
                if self.board[row][col - ColCounter] == "--":
                    moves.append(Move((row, col), (row, col - ColCounter), self.board))
                elif self.board[row][col - ColCounter][0] == "b":
                    break
                elif self.board[row][col - ColCounter][0] == "w":
                    moves.append(Move((row, col), (row, col - ColCounter), self.board))
                    break
            for RowCounter in range(1, 8 - row):
                if self.board[row + RowCounter][col] == "--":
                    moves.append(Move((row, col), (row + RowCounter, col), self.board))
                elif self.board[row + RowCounter][col][0] == "b":
                    break
                elif self.board[row + RowCounter][col][0] == "w":
                    moves.append(Move((row, col), (row + RowCounter, col), self.board))
                    break
            for RowCounter in range(1, row + 1):
                if self.board[row - RowCounter][col] == "--":
                    moves.append(Move((row, col), (row - RowCounter, col), self.board))
                elif self.board[row - RowCounter][col][0] == "b":
                    break
                elif self.board[row - RowCounter][col][0] == "w":
                    moves.append(Move((row, col), (row - RowCounter, col), self.board))
                    break


    # Находим всевозможные ходы слона
    def getBishopMoves(self, row, col, moves):
        if self.WhitetoMove:
            for ColCounter in range(1, 8 - col):
                if self.FitBoard(row + ColCounter, col + ColCounter):
                    if self.board[row + ColCounter][col + ColCounter] == "--":
                        moves.append(Move((row, col), (row + ColCounter, col + ColCounter), self.board))
                    elif self.board[row + ColCounter][col + ColCounter][0] == "w":
                        break
                    elif self.board[row + ColCounter][col + ColCounter][0] == "b":
                        moves.append(Move((row, col), (row + ColCounter, col + ColCounter), self.board))
                        break
            for ColCounter in range(1, col + 1):
                if self.FitBoard(row - ColCounter, col - ColCounter):
                    if self.board[row - ColCounter][col - ColCounter] == "--":
                        moves.append(Move((row, col), (row - ColCounter, col - ColCounter), self.board))
                    elif self.board[row - ColCounter][col - ColCounter][0] == "w":
                        break
                    elif self.board[row - ColCounter][col - ColCounter][0] == "b":
                        moves.append(Move((row, col), (row - ColCounter, col - ColCounter), self.board))
                        break
            for RowCounter in range(1, 8 - row):
                if self.FitBoard(row + RowCounter, col - RowCounter):
                    if self.board[row + RowCounter][col - RowCounter] == "--":
                        moves.append(Move((row, col), (row + RowCounter, col - RowCounter), self.board))
                    elif self.board[row + RowCounter][col - RowCounter][0] == "w":
                        break
                    elif self.board[row + RowCounter][col - RowCounter][0] == "b":
                        moves.append(Move((row, col), (row + RowCounter, col - RowCounter), self.board))
                        break
            for RowCounter in range(1, row + 1):
                if self.FitBoard(row - RowCounter, col + RowCounter):
                    if self.board[row - RowCounter][col + RowCounter] == "--":
                        moves.append(Move((row, col), (row - RowCounter, col + RowCounter), self.board))
                    elif self.board[row - RowCounter][col + RowCounter][0] == "w":
                        break
                    elif self.board[row - RowCounter][col + RowCounter][0] == "b":
                        moves.append(Move((row, col), (row - RowCounter, col + RowCounter), self.board))
                        break
        else:
            for ColCounter in range(1, 8 - col):
                if self.FitBoard(row + ColCounter, col + ColCounter):
                    if self.board[row + ColCounter][col + ColCounter] == "--":
                        moves.append(Move((row, col), (row + ColCounter, col + ColCounter), self.board))
                    elif self.board[row + ColCounter][col + ColCounter][0] == "b":
                        break
                    elif self.board[row + ColCounter][col + ColCounter][0] == "w":
                        moves.append(Move((row, col), (row + ColCounter, col + ColCounter), self.board))
                        break
            for ColCounter in range(1, col + 1):
                if self.FitBoard(row - ColCounter, col - ColCounter):
                    if self.board[row - ColCounter][col - ColCounter] == "--":
                        moves.append(Move((row, col), (row - ColCounter, col - ColCounter), self.board))
                    elif self.board[row - ColCounter][col - ColCounter][0] == "b":
                        break
                    elif self.board[row - ColCounter][col - ColCounter][0] == "w":
                        moves.append(Move((row, col), (row - ColCounter, col - ColCounter), self.board))
                        break
            for RowCounter in range(1, 8 - row):
                if self.FitBoard(row + RowCounter, col - RowCounter):
                    if self.board[row + RowCounter][col - RowCounter] == "--":
                        moves.append(Move((row, col), (row + RowCounter, col - RowCounter), self.board))
                    elif self.board[row + RowCounter][col - RowCounter][0] == "b":
                        break
                    elif self.board[row + RowCounter][col - RowCounter][0] == "w":
                        moves.append(Move((row, col), (row + RowCounter, col - RowCounter), self.board))
                        break
            for RowCounter in range(1, row + 1):
                if self.FitBoard(row - RowCounter, col + RowCounter):
                    if self.board[row - RowCounter][col + RowCounter] == "--":
                        moves.append(Move((row, col), (row - RowCounter, col + RowCounter), self.board))
                    elif self.board[row - RowCounter][col + RowCounter][0] == "b":
                        break
                    elif self.board[row - RowCounter][col + RowCounter][0] == "w":
                        moves.append(Move((row, col), (row - RowCounter, col + RowCounter), self.board))
                        break


    # Находим всевозможные ходы коня
    def getKnightMoves(self, row, col, moves):
        if self.WhitetoMove:
            for i in [-2, -1, 1, 2]:
                for j in [-2, -1, 1, 2]:
                    if (abs(i + j) % 2 == 1)  and self.FitBoard(row + i, col + j):
                        if self.board[row + i][col + j] == "--" or self.board[row + i][col + j][0] == "b":
                            moves.append(Move((row,col), (row + i, col + j), self.board))
                        elif self.board[row + i][col + j][0] == "w":
                            continue
        else:
            for i in [-2, -1, 1, 2]:
                for j in [-2, -1, 1, 2]:
                    if (abs(i + j) % 2 == 1)  and self.FitBoard(row + i, col + j):
                        if self.board[row + i][col + j] == "--" or self.board[row + i][col + j][0] == "w":
                            moves.append(Move((row,col), (row + i, col + j), self.board))
                        elif self.board[row + i][col + j][0] == "b":
                            continue


    # Находим всевозможные ходы ферзя
    def getQueenMoves(self, row, col, moves):
        self.getBishopMoves(row, col, moves)
        self.getRookMoves(row, col, moves)


    # Находим всевозможные ходы короля
    def getKingMoves(self, row, col, moves):
        if self.WhitetoMove:
            for i in [-1, 0, 1]:
                for j in [-1, 0, 1]:
                    if self.FitBoard(row + i, col + j) and (self.board[row + i][col + j] == "--" or self.board[row + i][col + j][0] == "b"):
                        moves.append(Move((row, col), (row + i, col + j), self.board))
        else:
            for i in [-1, 0, 1]:
                for j in [-1, 0, 1]:
                    if self.FitBoard(row + i, col + j) and (self.board[row + i][col + j] == "--" or self.board[row + i][col + j][0] == "w"):
                        moves.append(Move((row, col), (row + i, col + j), self.board))


    # Рокировки
    def ShortCastlePossible(self, moves):
        if self.WhitetoMove:
            row = self.WhiteKingLocation[0]
            col = self.WhiteKingLocation[1]
            if not self.WhiteKingMoved and not self.inCheck() and self.WhiteKingLocation == (7, 4):
                if not self.squareUnderAttack(row, col + 1) and self.board[row][col + 1] == "--":
                    if not self.squareUnderAttack(row, col + 2) and self.board[row][col + 2] == "--":
                        if self.board[row][col + 3] == "wR":
                            moves.append(Move((row, col), (row, col + 2), self.board))
            return False
        else:
            row = self.BlackKingLocation[0]
            col = self.BlackKingLocation[1]
            if not self.BlackKingMoved and not self.inCheck() and self.BlackKingLocation == (0, 4):
                if not self.squareUnderAttack(row, col + 1) and self.board[row][col + 1] == "--":
                    if not self.squareUnderAttack(row, col + 2) and self.board[row][col + 2] == "--":
                        if self.board[row][col + 3] == "bR":
                            moves.append(Move((row, col), (row, col + 2), self.board))
        return moves


    def LongCastlePossible(self, moves):
        if self.WhitetoMove:
            row = self.WhiteKingLocation[0]
            col = self.WhiteKingLocation[1]
            if not self.WhiteKingMoved and not self.inCheck() and self.WhiteKingLocation == (7, 4):
                if not self.squareUnderAttack(row, col - 1) and self.board[row][col - 1] == "--":
                    if not self.squareUnderAttack(row, col - 2) and self.board[row][col - 2] == "--":
                        if not self.squareUnderAttack(row, col - 3) and self.board[row][col - 3] == "--":
                            if self.board[row][col - 4] == "wR":
                                moves.append(Move((row, col), (row, col - 2), self.board))
        else:
            row = self.BlackKingLocation[0]
            col = self.BlackKingLocation[1]
            if not self.BlackKingMoved and not self.inCheck() and self.BlackKingLocation == (0, 4):
                if not self.squareUnderAttack(row, col - 1) and self.board[row][col - 1] == "--":
                    if not self.squareUnderAttack(row, col - 2) and self.board[row][col - 2] == "--":
                        if not self.squareUnderAttack(row, col - 3) and self.board[row][col - 3] == "--":
                            if self.board[row][col - 4] == "bR":
                                moves.append(Move((row, col), (row, col - 2), self.board))
        return moves





    # Не выходит ля ход за рамки доски?
    def FitBoard(self, row, col):
        if 0 <= row <= 7 and 0 <= col <= 7:
            return True
        else:
            return False


class Move:
    # Перевод столбцов в шахматный язык для записи ходов
    RankToRow = {
        "1": 7, "2": 6, "3": 5, "4": 4,
        "5": 3, "6": 2, "7": 1, "8": 0
    }
    RowToRank = {key: value for value, key in RankToRow.items()}
    LettertoCol = {
        "a": 0, "b": 1, "c": 2, "d": 3,
        "e": 4, "f": 5, "g": 6, "h": 7
    }
    ColtoLetter = {key: value for value, key in LettertoCol.items()}


    # Конструктор
    def __init__(self, startSQ, endSQ, board):
        self.startRow = startSQ[0]
        self.startCol = startSQ[1]
        self.endRow = endSQ[0]
        self.endCol = endSQ[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        self.isPromotion = False
        self.isPassant = False
        self.isCastling = False
        if self.pieceMoved == "wP" and self.endRow == 0 or self.pieceMoved == "bP" and self.endRow == 7:
            self.isPromotion = True
        if self.pieceCaptured == "--" and self.startCol != self.endCol and self.pieceMoved[1] == "P":
            self.isPassant = True
        if self.pieceMoved[1] == "K" and self.pieceCaptured == "--" and abs(self.startCol - self.endCol) > 1:
            self.isCastling = True
        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol
        #print(self.moveID)


    # Overriding equals method
    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False


    # Выводим ход, записанный в шахматном виде
    def getMovesNotation(self):
        piece = self.pieceMoved[1]
        if piece != "P" and piece != "-":
            piece = piece
        elif piece == "P":
            piece = ""
        elif piece == "-":
            piece = ""
        return piece + self.getMove(self.startRow, self.startCol)+ " - " + self.getMove(self.endRow, self.endCol)


    # Переводим ход из массивного представления в шахматное для записи партии
    def getMove(self, row, col):
        return self.ColtoLetter[col] + self.RowToRank[row]
