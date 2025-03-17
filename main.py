import pygame
import chess

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((800, 800))  # Increased size for better readability
pygame.display.set_caption("Chess AI (That Always Loses)")

# Constants
WIDTH, HEIGHT = 800, 800
SQUARE_SIZE = WIDTH // 8
COLORS = {'white': (240, 217, 181), 'black': (181, 136, 99)}
HIGHLIGHT_COLOR = (255, 255, 0, 120)  # Yellow transparent highlight
SELECTED_COLOR = (0, 255, 0)  # Green for selected square
FPS = 60

# Unicode Chess Symbols
PIECE_UNICODE = {
    'P': '\u2659', 'N': '\u2658', 'B': '\u2657', 'R': '\u2656', 'Q': '\u2655', 'K': '\u2654',
    'p': '\u265F', 'n': '\u265E', 'b': '\u265D', 'r': '\u265C', 'q': '\u265B', 'k': '\u265A'
}

# Initialize board
board = chess.Board()
font = pygame.font.SysFont('arial', 48)
clock = pygame.time.Clock()

selected_square, dragging_piece = None, None
game_over = False
winner = ""

# Draw the board
def draw_board():
    for row in range(8):
        for col in range(8):
            color = COLORS['white'] if (row + col) % 2 == 0 else COLORS['black']
            rect = pygame.Rect(col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
            pygame.draw.rect(screen, color, rect)

            # Highlight selected piece
            if selected_square is not None:
                sel_row, sel_col = divmod(selected_square, 8)
                if row == 7 - sel_row and col == sel_col:
                    pygame.draw.rect(screen, SELECTED_COLOR, rect, 6)

# Draw pieces on the board
def draw_pieces():
    for square, piece in board.piece_map().items():
        if dragging_piece and square == selected_square:
            continue
        row, col = divmod(square, 8)
        color = (218, 165, 32) if piece.color else (25, 25, 112)
        text = font.render(PIECE_UNICODE[piece.symbol()], True, color)
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
        return None  # No legal moves left (game is over)

    for move in legal_moves:
        board.push(move)
        score = evaluate_board()

        if board.is_capture(move): score += 10  
        if board.is_check(): score += 20  
        if board.is_checkmate(): score += 100  

        for response in board.legal_moves:
            if board.is_capture(response): score -= 50  

        board.pop()

        if score < worst_score:
            worst_score = score
            worst_move = move

    return worst_move if worst_move else legal_moves[0]  

# Evaluate board position
def evaluate_board():
    """ Returns a score based on material count. """
    piece_value = {chess.PAWN: 1, chess.KNIGHT: 3, chess.BISHOP: 3, chess.ROOK: 5, chess.QUEEN: 9, chess.KING: 1000}
    score = 0
    for square, piece in board.piece_map().items():
        value = piece_value[piece.piece_type]
        score += value if piece.color == chess.WHITE else -value
    return score

# Display Game Over Screen
def display_game_over():
    screen.fill((0, 0, 0))
    text = font.render(winner, True, (255, 255, 255))
    quit_text = font.render("QUIT", True, (255, 0, 0))
    quit_rect = quit_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50))

    screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - 50))
    pygame.draw.rect(screen, (255, 0, 0), quit_rect.inflate(20, 10), border_radius=5)
    screen.blit(quit_text, quit_rect)

    pygame.display.flip()
    return quit_rect  # Return the quit button rect for collision detection

# Check if the game is over
def check_game_over():
    global game_over, winner

    if board.is_checkmate():
        winner = "YOU WIN!" if board.turn == chess.BLACK else "YOU LOSE!"
        game_over = True
    elif board.is_stalemate():
        winner = "DRAW (Stalemate)!"
        game_over = True
    elif board.is_insufficient_material():
        winner = "DRAW (Insufficient Material)!"
        game_over = True
    elif board.can_claim_threefold_repetition():
        winner = "DRAW (Threefold Repetition)!"
        game_over = True
    elif board.can_claim_fifty_moves():
        winner = "DRAW (50-Move Rule)!"
        game_over = True

# Main loop
running = True
quit_rect = None
while running:
    clock.tick(FPS)

    # Process events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if game_over:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if quit_rect and quit_rect.collidepoint(event.pos):
                    running = False
        else:
            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                clicked_square = chess.square(x // SQUARE_SIZE, 7 - (y // SQUARE_SIZE))
                piece = board.piece_at(clicked_square)
                if piece and piece.color == chess.WHITE:
                    selected_square = clicked_square
                    dragging_piece = (x, y, piece.symbol())

            elif event.type == pygame.MOUSEMOTION and dragging_piece:
                dragging_piece = (event.pos[0], event.pos[1], dragging_piece[2])

            elif event.type == pygame.MOUSEBUTTONUP and dragging_piece:
                target_square = chess.square(event.pos[0] // SQUARE_SIZE, 7 - (event.pos[1] // SQUARE_SIZE))
                move = chess.Move(selected_square, target_square)

                # Pawn Promotion
                if board.piece_at(selected_square) and board.piece_at(selected_square).piece_type == chess.PAWN:
                    if target_square in chess.SquareSet(chess.BB_RANK_8) or target_square in chess.SquareSet(chess.BB_RANK_1):
                        move = chess.Move(selected_square, target_square, promotion=chess.QUEEN)

                if move in board.legal_moves:
                    board.push(move)
                    check_game_over()

                    if not game_over:
                        pygame.time.delay(300)
                        ai_move = get_losing_move()
                        if ai_move:
                            board.push(ai_move)
                            check_game_over()

                selected_square = None
                dragging_piece = None

    # Draw everything
    if game_over:
        quit_rect = display_game_over()
    else:
        screen.fill((0, 0, 0))
        draw_board()
        draw_pieces()
        pygame.display.flip()

pygame.quit()

