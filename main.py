import pygame
import chess

# Initialize pygame
pygame.init()
WIDTH, HEIGHT = 800, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("LoserChess- You Always Win")

# Colors & Fonts
COLORS = {'white': (240, 217, 181), 'black': (181, 136, 99)}
SELECTED_COLOR = (0, 255, 0)
FPS = 60
SQUARE_SIZE = WIDTH // 8
font_large = pygame.font.SysFont('arial', 64)
font_medium = pygame.font.SysFont('arial', 48)
font_small = pygame.font.SysFont('arial', 36)

# Unicode chess symbols
PIECE_UNICODE = {
    'P':'♙','N':'♘','B':'♗','R':'♖','Q':'♕','K':'♔',
    'p':'♟︎','n':'♞','b':'♝','r':'♜','q':'♛','k':'♚'
}

# Board setup
board = chess.Board()
clock = pygame.time.Clock()
selected_square, dragging_piece = None, None
game_over, winner = False, ""

# Sound setup (optional)
try:
    pygame.mixer.init()
    move_sound = pygame.mixer.Sound('sounds/move.wav')
    capture_sound = pygame.mixer.Sound('sounds/capture.wav')
except:
    move_sound = capture_sound = None

def draw_board():
    for row in range(8):
        for col in range(8):
            color = COLORS['white'] if (row+col)%2==0 else COLORS['black']
            rect=pygame.Rect(col*SQUARE_SIZE, row*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
            pygame.draw.rect(screen, color, rect)

            # Highlight selected piece's possible moves
            if selected_square is not None:
                sel_row, sel_col = divmod(selected_square, 8)
                if row == 7 - sel_row and col == sel_col:
                    pygame.draw.rect(screen, SELECTED_COLOR, rect, 6)

def draw_pieces():
    for square, piece in board.piece_map().items():
        if dragging_piece and square == selected_square:
            continue
        row, col = divmod(square, 8)
        color = (218, 165, 32) if piece.color else (25, 25, 112)
        text = font_medium.render(PIECE_UNICODE[piece.symbol()], True, color)
        x = col * SQUARE_SIZE + (SQUARE_SIZE - text.get_width()) // 2
        y = (7 - row) * SQUARE_SIZE + (SQUARE_SIZE - text.get_height()) // 2
        screen.blit(text, (x, y))

    if dragging_piece:
        color = (218, 165, 32) if dragging_piece[2].isupper() else (25, 25, 112)
        text = font_medium.render(PIECE_UNICODE[dragging_piece[2]], True, color)
        screen.blit(text, (dragging_piece[0] - text.get_width() // 2,
                           dragging_piece[1] - text.get_height() // 2))

def get_losing_move():
    worst_move = None
    worst_score = float('inf')
    legal_moves = list(board.legal_moves)

    if not legal_moves:
        return None

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

def evaluate_board():
    piece_value = {chess.PAWN: 1, chess.KNIGHT: 3, chess.BISHOP: 3, chess.ROOK: 5, chess.QUEEN: 9, chess.KING: 1000}
    score = 0
    for square, piece in board.piece_map().items():
        value = piece_value[piece.piece_type]
        score += value if piece.color else -value
    return score
def draw_board():
    for row in range(8):
        for col in range(8):
            color = COLORS['white'] if (row+col)%2==0 else COLORS['black']
            rect = pygame.Rect(col*SQUARE_SIZE, row*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
            pygame.draw.rect(screen, color, rect)

            # Highlight selected piece's square
            if selected_square is not None:
                sel_row, sel_col = divmod(selected_square, 8)
                if row == 7 - sel_row and col == sel_col:
                    pygame.draw.rect(screen, SELECTED_COLOR, rect, 6)

            # Highlight possible moves
            if selected_square is not None:
                possible_moves = [move.to_square for move in board.legal_moves if move.from_square == selected_square]
                if chess.square(col, 7 - row) in possible_moves:
                    pygame.draw.circle(screen, (0 , 0, 0), 
                                       (col * SQUARE_SIZE + SQUARE_SIZE // 2, 
                                        row * SQUARE_SIZE + SQUARE_SIZE // 2), 10)

def display_game_over():
    overlay_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay_surface.fill((0, 0, 0, 180))
    screen.blit(overlay_surface, (0,0))

    winner_text = font_large.render(winner.upper(), True, (255,255,255))
    winner_rect = winner_text.get_rect(center=(WIDTH//2, HEIGHT//3))
    screen.blit(winner_text, winner_rect)

    play_again_text = font_medium.render("PLAY AGAIN", True, (255,255,255))
    play_again_rect = play_again_text.get_rect(center=(WIDTH//2, HEIGHT//2))
    pygame.draw.rect(screen, (50,50,50), play_again_rect.inflate(40,20), border_radius=10)
    screen.blit(play_again_text, play_again_rect)

    quit_text = font_medium.render("QUIT", True, (255,255,255))
    quit_rect = quit_text.get_rect(center=(WIDTH//2, HEIGHT//2 + 80))
    pygame.draw.rect(screen,(50,50,50),quit_rect.inflate(40,20),border_radius=10)
    screen.blit(quit_text,quit_rect)

    pygame.display.flip()
    return play_again_rect.inflate(40,20), quit_rect.inflate(40,20)

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

running = True
while running:
    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if game_over:
            play_again_rect_final, quit_rect_final = display_game_over()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if play_again_rect_final.collidepoint(event.pos):
                    board = chess.Board()
                    game_over = False
                    winner = ""
                elif quit_rect_final.collidepoint(event.pos):
                    running = False

        else:
            if event.type == pygame.MOUSEBUTTONDOWN:
                x,y=event.pos
                clicked_square=chess.square(x//SQUARE_SIZE,(7-y//SQUARE_SIZE))
                piece=board.piece_at(clicked_square)
                if piece and piece.color==chess.WHITE:
                    selected_square=clicked_square
                    dragging_piece=(x,y,piece.symbol())

            elif event.type == pygame.MOUSEMOTION and dragging_piece:
                dragging_piece=(event.pos[0],event.pos[1],dragging_piece[2])

            elif event.type == pygame.MOUSEBUTTONUP and dragging_piece:
                target_square=chess.square(event.pos[0]//SQUARE_SIZE,(7-event.pos[1]//SQUARE_SIZE))
                move=chess.Move(selected_square,target_square)

                # Pawn promotion logic fix
                piece_moved=board.piece_at(selected_square)
                if piece_moved and piece_moved.piece_type==chess.PAWN and chess.square_rank(target_square) in [0,7]:
                    move=chess.Move(selected_square,target_square,promotion=chess.QUEEN)

                if move in board.legal_moves:
                    board.push(move)
                    # Play sound effect safely (if enabled)
                    try:
                        if board.is_capture(move):
                            capture_sound.play()
                        else:
                            move_sound.play()
                    except:
                        pass

                    check_game_over()

                    if not game_over:
                        pygame.time.delay(300)
                        ai_move = get_losing_move()
                        if ai_move:
                            board.push(ai_move)
                            check_game_over()

                selected_square = None
                dragging_piece = None

    if not game_over:
        screen.fill((0,0,0))
        draw_board()
        draw_pieces()
        pygame.display.flip()

pygame.quit()
