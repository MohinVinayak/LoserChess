import os
import pygame
import chess
import math

# Initialize Pygame for Replit
pygame.init()
screen = pygame.display.set_mode((600, 600))
pygame.display.set_caption("Chess Game")

# Constants
WIDTH, HEIGHT = 600, 600
SQUARE_SIZE = WIDTH // 8
COLORS = {'white': (240, 217, 181), 'black': (181, 136, 99)}
HIGHLIGHT_COLOR = (124, 252, 0, 128)
MOVE_INDICATOR = (0, 153, 51, 180)
FPS = 60

# Unicode Chess Symbols
PIECE_UNICODE = {
    'P': '\u2659', 'N': '\u2658', 'B': '\u2657', 'R': '\u2656', 'Q': '\u2655', 'K': '\u2654',
    'p': '\u265F', 'n': '\u265E', 'b': '\u265D', 'r': '\u265C', 'q': '\u265B', 'k': '\u265A'
}

# Initialize board and screen
board = chess.Board()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Chess AI (That Always Loses)")
font = pygame.font.SysFont('arial', 48)
clock = pygame.time.Clock()

selected_square, valid_moves, dragging_piece, last_move = None, [], None, None

# Draw the board
def draw_board():
    for row in range(8):
        for col in range(8):
            color = COLORS['white'] if (row + col) % 2 == 0 else COLORS['black']
            rect = pygame.Rect(col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
            pygame.draw.rect(screen, color, rect)

# Draw pieces on board
def draw_pieces():
    for square, piece in board.piece_map().items():
        if dragging_piece and square == selected_square:
            continue
        row, col = divmod(square, 8)
        # Gold for white pieces, Dark blue for black pieces
        color = (218, 165, 32) if piece.color else (25, 25, 112)
        text = font.render(PIECE_UNICODE[piece.symbol()], True, color)

        # Center the piece
        x = col * SQUARE_SIZE + (SQUARE_SIZE - text.get_width()) // 2
        y = (7 - row) * SQUARE_SIZE + (SQUARE_SIZE - text.get_height()) // 2
        screen.blit(text, (x, y))

    if dragging_piece:
        color = (218, 165, 32) if dragging_piece[2].isupper() else (25, 25, 112)
        text = font.render(PIECE_UNICODE[dragging_piece[2]], True, color)
        screen.blit(text, (dragging_piece[0] - 25, dragging_piece[1] - 25))

# AI Move: Choosing the worst move intentionally
def get_losing_move():
    """ AI plays the worst possible move (intentionally blundering). """
    worst_move = None
    worst_score = float('inf')
    legal_moves = list(board.legal_moves)
    
    if not legal_moves:
        return None
        
    for move in legal_moves:
        board.push(move)
        score = evaluate_board()
        
        # Penalize good moves
        if board.is_capture(move):
            score += 10
            
        if board.is_check():
            score += 20
            
        if board.is_checkmate():
            score += 100
            
        # Look ahead for piece loss
        for response in board.legal_moves:
            if board.is_capture(response):
                score -= 50  # Reward moves that lose pieces
                
        board.pop()
        
        if score < worst_score:
            worst_score = score
            worst_move = move

    return worst_move or legal_moves[0]  # Fallback to first legal move


def piece_lost(move):
    """ Checks if the AI blunders a piece (hangs it for free). """
    board.push(move)
    for response in board.legal_moves:
        if board.is_capture(response):  
            board.pop()
            return True  # AI just lost a piece
    board.pop()
    return False
# Evaluate board
def evaluate_board():
    piece_value = {chess.PAWN: 1, chess.KNIGHT: 3, chess.BISHOP: 3, chess.ROOK: 5, chess.QUEEN: 9, chess.KING: 1000}
    score = 0
    for square, piece in board.piece_map().items():
        value = piece_value[piece.piece_type]
        score += value if piece.color == chess.WHITE else -value
    return score

# Main loop
running = True
while running:
    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            clicked_square = chess.square(x // SQUARE_SIZE, (7 - y // SQUARE_SIZE))
            piece = board.piece_at(clicked_square)
            if piece and piece.color == chess.WHITE:
                selected_square = clicked_square
                valid_moves = [m.to_square for m in board.legal_moves if m.from_square == selected_square]
                dragging_piece = (x, y, piece.symbol())

        elif event.type == pygame.MOUSEBUTTONUP and dragging_piece:
            target_square = chess.square(event.pos[0] // SQUARE_SIZE, (7 - event.pos[1] // SQUARE_SIZE))
            move = [m for m in board.legal_moves if m.from_square == selected_square and m.to_square == target_square]
            if move:
                board.push(move[0])
                last_move = move[0]
                pygame.time.delay(300)
                ai_move = get_losing_move()
                board.push(ai_move)
                last_move = ai_move

            selected_square = None
            valid_moves = []
            dragging_piece = None

    # Draw everything
    screen.fill((0, 0, 0))
    draw_board()
    draw_pieces()
    pygame.display.flip()

pygame.quit()

