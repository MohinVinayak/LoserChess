import pygame
import chess

# Initialize pygame
pygame.init()
WIDTH, HEIGHT = 800, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("LoserChess - You Always Win")

# Colors & Fonts
COLORS = {'white': (240, 217, 181), 'black': (181, 136, 99)}
SELECTED_COLOR = (0, 255, 0)
MOVE_DOT_COLOR = (0, 0, 0)
FPS = 60
SQUARE_SIZE = WIDTH // 8
AI_MOVE_DELAY_MS = 300

font_large  = pygame.font.SysFont('arial', 64)
font_medium = pygame.font.SysFont('arial', 48)
font_small  = pygame.font.SysFont('arial', 18)

# Unicode chess symbols
PIECE_UNICODE = {
    'P': '♙', 'N': '♘', 'B': '♗', 'R': '♖', 'Q': '♕', 'K': '♔',
    'p': '♟︎', 'n': '♞', 'b': '♝', 'r': '♜', 'q': '♛', 'k': '♚'
}

# Board setup
board = chess.Board()
clock = pygame.time.Clock()
selected_square  = None
dragging_piece   = None   # (x, y, symbol_str)
game_over        = False
winner           = ""

# Sound setup (optional)
try:
    pygame.mixer.init()
    move_sound    = pygame.mixer.Sound('sounds/move.wav')
    capture_sound = pygame.mixer.Sound('sounds/capture.wav')
except Exception:
    move_sound = capture_sound = None


# ─────────────────────────────────────────────
# Drawing helpers
# ─────────────────────────────────────────────

def draw_board():
    """Draw squares, selection highlight, and legal-move dots."""
    possible_targets = (
        {move.to_square for move in board.legal_moves if move.from_square == selected_square}
        if selected_square is not None else set()
    )

    for row in range(8):
        for col in range(8):
            sq    = chess.square(col, 7 - row)
            color = COLORS['white'] if (row + col) % 2 == 0 else COLORS['black']
            rect  = pygame.Rect(col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
            pygame.draw.rect(screen, color, rect)

            # Green border on the selected piece's square
            if selected_square is not None:
                sel_row, sel_col = divmod(selected_square, 8)
                if row == 7 - sel_row and col == sel_col:
                    pygame.draw.rect(screen, SELECTED_COLOR, rect, 6)

            # Small dot on legal-move targets
            if sq in possible_targets:
                cx = col * SQUARE_SIZE + SQUARE_SIZE // 2
                cy = row * SQUARE_SIZE + SQUARE_SIZE // 2
                pygame.draw.circle(screen, MOVE_DOT_COLOR, (cx, cy), 10)


def draw_pieces():
    """Draw all pieces; skip the piece being dragged (drawn separately)."""
    for square, piece in board.piece_map().items():
        if dragging_piece and square == selected_square:
            continue
        row, col = divmod(square, 8)
        color = (218, 165, 32) if piece.color else (25, 25, 112)
        text  = font_medium.render(PIECE_UNICODE[piece.symbol()], True, color)
        x     = col * SQUARE_SIZE + (SQUARE_SIZE - text.get_width())  // 2
        y     = (7 - row) * SQUARE_SIZE + (SQUARE_SIZE - text.get_height()) // 2
        screen.blit(text, (x, y))

    # Draw the piece under the cursor while dragging
    if dragging_piece:
        sym   = dragging_piece[2]
        color = (218, 165, 32) if sym.isupper() else (25, 25, 112)
        text  = font_medium.render(PIECE_UNICODE[sym], True, color)
        screen.blit(text, (
            dragging_piece[0] - text.get_width()  // 2,
            dragging_piece[1] - text.get_height() // 2
        ))


def draw_labels():
    """Draw file (a-h) and rank (1-8) labels along the edges."""
    for i in range(8):
        # File letters along the bottom
        col_label = font_small.render(chr(ord('a') + i), True, (120, 120, 120))
        screen.blit(col_label, (i * SQUARE_SIZE + 4, HEIGHT - 20))
        # Rank numbers along the left
        row_label = font_small.render(str(8 - i), True, (120, 120, 120))
        screen.blit(row_label, (4, i * SQUARE_SIZE + 4))


def display_game_over():
    """Render the semi-transparent game-over overlay; return button rects."""
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    screen.blit(overlay, (0, 0))

    winner_text = font_large.render(winner.upper(), True, (255, 255, 255))
    screen.blit(winner_text, winner_text.get_rect(center=(WIDTH // 2, HEIGHT // 3)))

    play_again_text = font_medium.render("PLAY AGAIN", True, (255, 255, 255))
    play_again_rect = play_again_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    pygame.draw.rect(screen, (50, 50, 50), play_again_rect.inflate(40, 20), border_radius=10)
    screen.blit(play_again_text, play_again_rect)

    quit_text = font_medium.render("QUIT", True, (255, 255, 255))
    quit_rect = quit_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 80))
    pygame.draw.rect(screen, (50, 50, 50), quit_rect.inflate(40, 20), border_radius=10)
    screen.blit(quit_text, quit_rect)

    pygame.display.flip()
    return play_again_rect.inflate(40, 20), quit_rect.inflate(40, 20)


# ─────────────────────────────────────────────
# Game logic
# ─────────────────────────────────────────────

def evaluate_board():
    """
    Positive = White (player) advantage.
    The AI (Black) wants to minimise this, i.e. play the *worst* move for itself.
    """
    piece_value = {
        chess.PAWN: 1, chess.KNIGHT: 3, chess.BISHOP: 3,
        chess.ROOK: 5, chess.QUEEN: 9, chess.KING: 1000
    }
    score = 0
    for square, piece in board.piece_map().items():
        value  = piece_value[piece.piece_type]
        score += value if piece.color == chess.WHITE else -value
    return score


def get_losing_move():
    """
    Pick the move that makes the AI (Black) position as bad as possible,
    i.e. gives the human (White) the maximum advantage.
    """
    legal_moves = list(board.legal_moves)
    if not legal_moves:
        return None

    worst_move  = None
    worst_score = float('inf')   # we want the move with the LOWEST score for Black

    for move in legal_moves:
        # FIX #2: evaluate capture BEFORE pushing
        is_capture = board.is_capture(move)

        board.push(move)

        score = evaluate_board()

        # Reward self-captures (AI giving up material is good for the "loser" bot)
        if is_capture:
            score -= 10          # AI captured something → bad for AI → lower score = chosen sooner

        # FIX #3: after push it is White's turn; is_check/is_checkmate refers to White
        if board.is_check():
            score += 5           # AI left White in check → bad for a losing bot
        if board.is_checkmate():
            score += 200         # AI checkmated White → the worst possible outcome for a losing bot

        # Penalise positions where White CAN capture next turn (those are good for the losing bot)
        for response in board.legal_moves:
            if board.is_capture(response):
                score -= 15

        board.pop()

        if score < worst_score:
            worst_score = score
            worst_move  = move

    return worst_move or legal_moves[0]


def check_game_over():
    global game_over, winner

    if board.is_checkmate():
        # board.turn is the side that HAS been checkmated (they're to move but can't)
        if board.turn == chess.BLACK:
            winner = "YOU WIN!"      # Black (AI) checkmated → player wins
        else:
            winner = "YOU LOSE!"     # White (player) checkmated
        game_over = True

    elif board.is_stalemate():
        winner    = "DRAW (Stalemate)!"
        game_over = True
    elif board.is_insufficient_material():
        winner    = "DRAW (Insufficient Material)!"
        game_over = True
    elif board.can_claim_threefold_repetition():
        winner    = "DRAW (Threefold Repetition)!"
        game_over = True
    elif board.can_claim_fifty_moves():
        winner    = "DRAW (50-Move Rule)!"
        game_over = True


def reset_game():
    global board, game_over, winner, selected_square, dragging_piece
    board           = chess.Board()
    game_over       = False
    winner          = ""
    selected_square = None
    dragging_piece  = None


# ─────────────────────────────────────────────
# Main loop
# ─────────────────────────────────────────────

# Cached button rects so we can hit-test without redrawing every event
play_again_rect_cached = None
quit_rect_cached       = None

running = True
while running:
    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif game_over:
            # FIX #4: only hit-test here; rendering happens once per frame below
            if event.type == pygame.MOUSEBUTTONDOWN and play_again_rect_cached:
                if play_again_rect_cached.collidepoint(event.pos):
                    reset_game()
                elif quit_rect_cached.collidepoint(event.pos):
                    running = False

        else:
            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                clicked_square = chess.square(x // SQUARE_SIZE, (7 - y // SQUARE_SIZE))
                piece = board.piece_at(clicked_square)
                if piece and piece.color == chess.WHITE:
                    selected_square = clicked_square
                    dragging_piece  = (x, y, piece.symbol())

            elif event.type == pygame.MOUSEMOTION and dragging_piece:
                dragging_piece = (event.pos[0], event.pos[1], dragging_piece[2])

            elif event.type == pygame.MOUSEBUTTONUP and dragging_piece:
                tx, ty = event.pos
                target_square = chess.square(tx // SQUARE_SIZE, (7 - ty // SQUARE_SIZE))
                move = chess.Move(selected_square, target_square)

                # Pawn promotion → auto-queen
                piece_moved = board.piece_at(selected_square)
                if (piece_moved
                        and piece_moved.piece_type == chess.PAWN
                        and chess.square_rank(target_square) in (0, 7)):
                    move = chess.Move(selected_square, target_square, promotion=chess.QUEEN)

                if move in board.legal_moves:
                    is_capture = board.is_capture(move)   # check BEFORE push
                    board.push(move)

                    if move_sound or capture_sound:
                        try:
                            (capture_sound if is_capture else move_sound).play()
                        except Exception:
                            pass

                    check_game_over()

                    if not game_over:
                        pygame.time.delay(AI_MOVE_DELAY_MS)
                        ai_move = get_losing_move()
                        if ai_move:
                            board.push(ai_move)
                            check_game_over()

                selected_square = None
                dragging_piece  = None

    # ── Render ──────────────────────────────
    screen.fill((0, 0, 0))

    if game_over:
        # Draw the board underneath the overlay so it isn't a black void
        draw_board()
        draw_pieces()
        draw_labels()
        # FIX #4: render overlay once per frame, cache button rects
        play_again_rect_cached, quit_rect_cached = display_game_over()
    else:
        draw_board()
        draw_pieces()
        draw_labels()
        pygame.display.flip()

pygame.quit()
