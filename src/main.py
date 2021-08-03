import chess
import chess.pgn
import chess.engine
import chess.svg
import os.path              #for reading in the pgn files
import random
import sys

"""
Features to have (Essential):   
    Autoplay response from PGN
    Go to end of PGN (furthest point previously looked at)
    Eval bar/box (with engine installed)
    Display PGN in desired storage folder to swap between
    Add move to current PGN
    Delete move from current PGN
    Add comments to a given move
    Select multiple repertoires learn from at once
    Black/White Repertoire separation
    
Features to have (Desired)
    Select PGN from computer
    Import games/studies from Lichess
    Display possible responses at user request
    Designate starting point in PGN for training
    Bias to selecting responses that are incorrectly responded to
        - May be doable by storing rolling average in PGN
    Display accuracy for a given PGN
    Check if a given response was a mistake/blunder
    
Completed:
    Board Display
    Move back/game start
"""

from PyQt5.QtCore    import *
from PyQt5.QtGui     import *
from PyQt5.QtWidgets import * 
from PyQt5.QtSvg     import *

class Window(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Opening Study Tool")
        self.setGeometry(0, 0, 800, 800)
        #need a move stack to push and pop from
        
        self.board_setup()
        self.create_widgets()

        
    def board_setup(self):
        """
        Initialize the chessboard and, if possible, an engine to evaluate.
        """
        #self.board = chess.Board()
        #self.stack_board = chess.Board()    #used to keep stack to end of game
        self.pgn = open("../repertoires/lichess_study_e4-gotham_by_Emi_xD2_2021.01.17.pgn")
        self.game = chess.pgn.read_game(self.pgn)
        self.current_node = self.game
        self.board = self.game.board()
        #need to initialize engine here, but it hinders closing of PyQt window
    
    def create_widgets(self):
        """
        create all of the elements in the app and connect them to the appropriate functions.
        """
        btn_height = 50
        btn_width = 100
        
        self.hbox = QHBoxLayout()
        self.vbox = QVBoxLayout()
                
        #botton half of screen
        self.game_start_btn = QPushButton("<<", self)
        self.game_start_btn.clicked.connect(self.game_start)
        
        self.move_bck_btn = QPushButton(" <", self)
        self.move_bck_btn.clicked.connect(self.get_prev_move)
        
        self.get_next_move_btn = QPushButton("> ", self)
        self.get_next_move_btn.clicked.connect(self.get_next_mainline_move)
        
        self.game_end_btn = QPushButton(">>", self)
        self.game_end_btn.clicked.connect(self.game_end)
        
        self.move_input = QLineEdit("", self)
        self.move_input.returnPressed.connect(self.move_entered)

        raw_svg = chess.svg.board(self.board)
        f = open("BoardVisualisedFromFEN.SVG", "w")
        f.write(raw_svg)
        f.close()
        
        self.board_svg = QSvgWidget()
        self.board_svg.load("BoardVisualisedFromFEN.SVG")
        
        self.hbox.addWidget(self.game_start_btn)
        self.hbox.addWidget(self.move_bck_btn)
        self.hbox.addWidget(self.get_next_move_btn)
        self.hbox.addWidget(self.game_end_btn)
        self.hbox.addWidget(self.move_input)
        
        self.vbox.addWidget(self.board_svg)
        self.vbox.addLayout(self.hbox)
        self.setLayout(self.vbox)
    
    def update_svg(self):
        """
        write the board to svg and load the file
        """
        #can't fix character case because of bishops and b pawns 
        #(Bc4 vs bc4 mean different things and can both be legal at once)
        print(self.current_node.comment)
        raw_svg = chess.svg.board(self.board)
        f = open("BoardVisualisedFromFEN.SVG", "w")
        f.write(raw_svg)
        f.close()
        self.board_svg.load("BoardVisualisedFromFEN.SVG")

    def get_next_mainline_move(self):
        """
        gets the next mainline move from the current node
        """
        if self.current_node.next() != None:
            self.current_node = self.current_node.next()
            self.board = self.current_node.board()
            self.update_svg()
        
    def get_next_move(self):
        """
        gets a random variation from the current move
        called when user enters a move
        """
        if self.current_node.next() != None:
            self.current_node = self.current_node.variation(random.choice([i for i in self.current_node.variations]))
            self.board = self.current_node.board()
            self.update_svg()
        
    def get_prev_move(self):
        """
        sets board state to the parent of the current node
        """
        if self.current_node.parent != None:
            self.current_node = self.current_node.parent
        self.board = self.current_node.board()
        self.update_svg()

    def game_start(self):
        """
        
        """
        while self.current_node.parent != None:
            self.current_node = self.current_node.parent
        self.board = self.current_node.board()
        self.update_svg()
    
    def game_end(self):
        """
        push all mainline moves to the board
        """

        #print(self.game.variations)
        self.current_node = self.current_node.variation(self.current_node.variations[0])
        print(self.current_node.variations)
        self.current_node = self.current_node.variation(self.current_node.variations[0])
        print(self.current_node.variations)
        
    def move_entered(self):
        """
        take an entered move and push it to the board, then load and update the svg image
        update the pgn if possible
        """
        text = self.move_input.text()
        
        print(self.move_input.text())
        self.move_input.clear()
        try:
            move = self.board.parse_san(text)
            self.current_node = self.current_node.variation(move)
            self.board.push(move)
        except (ValueError, KeyError):
            if text == "":
                #may want to use mainline only in some cases
                self.get_next_move()
        
        self.update_svg()
    
app = QApplication(sys.argv)

window= Window()
window.show()

sys.exit(app.exec())