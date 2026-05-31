import pygame
import chess
import asyncio
import os
import platform
import json

# Initialize pygame
pygame.init()
WIDTH, HEIGHT = 800, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("LoserChess")

# Colors & Fonts
COLORS = {'white': (240, 217, 181), 'black': (181, 136, 99)}
SELECTED_COLOR = (0, 255, 0)
MOVE_DOT_COLOR = (0, 0, 0)
FPS = 60
SQUARE_SIZE = WIDTH // 8
PIECE_SIZE = int(SQUARE_SIZE * 0.8)
PIECE_OFFSET = (SQUARE_SIZE - PIECE_SIZE) // 2
AI_MOVE_DELAY_MS = 300

font_large  = pygame.font.SysFont('arial', 64)
font_medium = pygame.font.SysFont('arial', 48)
font_small  = pygame.font.SysFont('arial', 18)

# Load piece images
PIECE_IMAGES = {}
piece_names = ['P', 'N', 'B', 'R', 'Q', 'K', 'p', 'n', 'b', 'r', 'q', 'k']
for p in piece_names:
    color_prefix = 'w' if p.isupper() else 'b'
    filename = f"assets/{color_prefix}{p.upper()}.png"
    try:
        if os.path.exists(filename):
            img = pygame.image.load(filename).convert_alpha()
            img = pygame.transform.smoothscale(img, (PIECE_SIZE, PIECE_SIZE))
            PIECE_IMAGES[p] = img
        else:
            print(f"Warning: {filename} not found.")
    except Exception as e:
        print(f"Error loading {filename}: {e}")

# Board setup
board = chess.Board()
clock = pygame.time.Clock()
selected_square  = None
dragging_piece   = None   # (x, y, symbol_str)
game_over        = False
winner           = ""
last_move        = None
animating_piece  = None   # dict with 'from_sq', 'to_sq', 'symbol', 'start_time', 'duration'

# Sound setup
move_sound = None
capture_sound = None
check_sound = None
mate_sound = None

try:
    pygame.mixer.init()
    def load_sound(path):
        if os.path.exists(path):
            return pygame.mixer.Sound(path)
        return None
    move_sound    = load_sound('sounds/move.ogg')
    capture_sound = load_sound('sounds/capture.ogg')
    check_sound   = load_sound('sounds/check.ogg')
    mate_sound    = load_sound('sounds/mate.ogg')
except Exception as e:
    print(f"Sound init error: {e}")



# ---------------------------------------------
# Drawing helpers
# ---------------------------------------------

def draw_board():
    """Draw squares, selection highlight, last-move highlight, and legal-move dots/rings."""
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

            # Soft yellow highlights for last move squares
            if last_move is not None and sq in (last_move.from_square, last_move.to_square):
                highlight_surf = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
                highlight_surf.fill((246, 246, 130, 100)) # Lichess-style subtle yellow tint
                screen.blit(highlight_surf, (col * SQUARE_SIZE, row * SQUARE_SIZE))

            # Translucent green highlight on the selected piece's square
            if selected_square is not None:
                sel_row, sel_col = divmod(selected_square, 8)
                if row == 7 - sel_row and col == sel_col:
                    sel_surf = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
                    sel_surf.fill((20, 220, 20, 80)) # subtle translucent green
                    screen.blit(sel_surf, (col * SQUARE_SIZE, row * SQUARE_SIZE))

            # Small translucent dot or outer ring on legal-move targets
            if sq in possible_targets:
                cx = col * SQUARE_SIZE + SQUARE_SIZE // 2
                cy = row * SQUARE_SIZE + SQUARE_SIZE // 2
                target_piece = board.piece_at(sq)
                if target_piece:
                    # Draw a nice outer circle outline if targeting an occupied square
                    pygame.draw.circle(screen, (0, 0, 0), (cx, cy), SQUARE_SIZE // 2 - 4, 4)
                else:
                    # Draw a small dot if targeting an empty square
                    pygame.draw.circle(screen, MOVE_DOT_COLOR, (cx, cy), 8)


def draw_pieces(current_time):
    """Draw all pieces; skip the piece being dragged or animated."""
    global animating_piece
    
    anim_progress = 1.0
    anim_symbol = None
    anim_to_sq = None
    
    if animating_piece:
        elapsed = current_time - animating_piece['start_time']
        duration = animating_piece['duration']
        if elapsed >= duration:
            animating_piece = None
        else:
            anim_progress = elapsed / duration
            anim_symbol = animating_piece['symbol']
            anim_to_sq = animating_piece['to_sq']
            
    for square, piece in board.piece_map().items():
        if dragging_piece and square == selected_square:
            continue
        # Skip drawing the animating piece at its destination square during animation
        if animating_piece and square == anim_to_sq and piece.symbol() == anim_symbol:
            continue
            
        row, col = divmod(square, 8)
        sym = piece.symbol()
        if sym in PIECE_IMAGES:
            x = col * SQUARE_SIZE + PIECE_OFFSET
            y = (7 - row) * SQUARE_SIZE + PIECE_OFFSET
            screen.blit(PIECE_IMAGES[sym], (x, y))
            
    # Draw sliding piece
    if animating_piece:
        from_row, from_col = divmod(animating_piece['from_sq'], 8)
        to_row, to_col = divmod(animating_piece['to_sq'], 8)
        
        from_x = from_col * SQUARE_SIZE + PIECE_OFFSET
        from_y = (7 - from_row) * SQUARE_SIZE + PIECE_OFFSET
        to_x = to_col * SQUARE_SIZE + PIECE_OFFSET
        to_y = (7 - to_row) * SQUARE_SIZE + PIECE_OFFSET
        
        curr_x = from_x + (to_x - from_x) * anim_progress
        curr_y = from_y + (to_y - from_y) * anim_progress
        
        sym = animating_piece['symbol']
        if sym in PIECE_IMAGES:
            screen.blit(PIECE_IMAGES[sym], (int(curr_x), int(curr_y)))

    # Draw the piece under the cursor while dragging
    if dragging_piece:
        sym = dragging_piece[2]
        if sym in PIECE_IMAGES:
            img = PIECE_IMAGES[sym]
            screen.blit(img, (
                dragging_piece[0] - PIECE_SIZE // 2,
                dragging_piece[1] - PIECE_SIZE // 2
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


def display_game_over(mouse_pos):
    """Render the semi-transparent game-over overlay; return button rects."""
    # 1. Semi-transparent full-screen dimming overlay
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((10, 10, 15, 180)) # Dark translucent tint
    screen.blit(overlay, (0, 0))

    # 2. Main Dialog Card
    card_w, card_h = 500, 320
    card_x = (WIDTH - card_w) // 2
    card_y = (HEIGHT - card_h) // 2

    # Draw card background with rounded corners (using alpha)
    card_surf = pygame.Surface((card_w, card_h), pygame.SRCALPHA)
    pygame.draw.rect(card_surf, (24, 24, 28, 245), (0, 0, card_w, card_h), border_radius=16)
    # Draw card border
    pygame.draw.rect(card_surf, (255, 255, 255, 30), (0, 0, card_w, card_h), width=2, border_radius=16)
    screen.blit(card_surf, (card_x, card_y))

    # 3. Title text (Winner status)
    text_color = (255, 255, 255)
    if "WIN" in winner:
        text_color = (46, 204, 113) # Nice Emerald Green
    elif "LOSE" in winner:
        text_color = (231, 76, 60) # Smooth Red
    else:
        text_color = (149, 165, 166) # Silver/Gray for draws

    winner_text = font_large.render(winner.upper(), True, text_color)
    if winner_text.get_width() > card_w - 40:
        # Scale down to fit the card width if text is too long (e.g. 50-move rule draws)
        new_w = card_w - 40
        new_h = int(winner_text.get_height() * (new_w / winner_text.get_width()))
        winner_text = pygame.transform.smoothscale(winner_text, (new_w, new_h))

    winner_rect = winner_text.get_rect(center=(WIDTH // 2, card_y + 60))
    screen.blit(winner_text, winner_rect)

    # 4. Buttons
    # Play Again Button
    play_again_text = font_medium.render("PLAY AGAIN", True, (255, 255, 255))
    play_again_rect = play_again_text.get_rect(center=(WIDTH // 2, card_y + 160))
    play_again_btn_rect = play_again_rect.inflate(60, 20)

    # Quit Button
    quit_text = font_medium.render("QUIT", True, (255, 255, 255))
    quit_rect = quit_text.get_rect(center=(WIDTH // 2, card_y + 240))
    quit_btn_rect = quit_rect.inflate(60, 20)

    # Check Hover states
    is_play_again_hovered = play_again_btn_rect.collidepoint(mouse_pos)
    is_quit_hovered = quit_btn_rect.collidepoint(mouse_pos)

    # Draw Play Again Button
    play_again_color = (46, 204, 113) if is_play_again_hovered else (39, 174, 96)
    pygame.draw.rect(screen, play_again_color, play_again_btn_rect, border_radius=12)
    if is_play_again_hovered:
        pygame.draw.rect(screen, (255, 255, 255, 200), play_again_btn_rect, width=2, border_radius=12)

    # Draw text
    screen.blit(play_again_text, play_again_rect)

    # Draw Quit Button
    quit_color = (231, 76, 60) if is_quit_hovered else (50, 50, 55)
    pygame.draw.rect(screen, quit_color, quit_btn_rect, border_radius=12)
    if is_quit_hovered:
        pygame.draw.rect(screen, (255, 255, 255, 200), quit_btn_rect, width=2, border_radius=12)

    # Draw text
    screen.blit(quit_text, quit_rect)

    return play_again_btn_rect, quit_btn_rect



# ---------------------------------------------
# Game logic
# ---------------------------------------------

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


async def get_losing_move():
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
            score -= 10          # AI captured something -> bad for AI -> lower score = chosen sooner

        # FIX #3: after push it is White's turn; is_check/is_checkmate refers to White
        if board.is_check():
            score += 5           # AI left White in check -> bad for a losing bot
        if board.is_checkmate():
            score += 200         # AI checkmated White -> the worst possible outcome for a losing bot

        # Penalise positions where White CAN capture next turn (those are good for the losing bot)
        for response in board.legal_moves:
            if board.is_capture(response):
                score -= 15

        board.pop()

        if score < worst_score:
            worst_score = score
            worst_move  = move
            
        await asyncio.sleep(0) # Keep async loop responsive during heavy evaluation

    return worst_move or legal_moves[0]


def check_game_over():
    global game_over, winner

    if board.is_checkmate():
        # board.turn is the side that HAS been checkmated (they're to move but can't)
        if board.turn == chess.BLACK:
            winner = "YOU WIN!"      # Black (AI) checkmated -> player wins
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


def update_captured_js():
    # Count pieces on the board
    counts = {
        'P': 0, 'N': 0, 'B': 0, 'R': 0, 'Q': 0, 'K': 0,
        'p': 0, 'n': 0, 'b': 0, 'r': 0, 'q': 0, 'k': 0
    }
    for sq in chess.SQUARES:
        piece = board.piece_at(sq)
        if piece:
            counts[piece.symbol()] += 1
            
    captured_white = {
        'P': max(0, 8 - counts['P']),
        'N': max(0, 2 - counts['N']),
        'B': max(0, 2 - counts['B']),
        'R': max(0, 2 - counts['R']),
        'Q': max(0, 1 - counts['Q']),
    }
    captured_black = {
        'p': max(0, 8 - counts['p']),
        'n': max(0, 2 - counts['n']),
        'b': max(0, 2 - counts['b']),
        'r': max(0, 2 - counts['r']),
        'q': max(0, 1 - counts['q']),
    }
    
    if platform.system() == "Emscripten":
        try:
            platform.window.updateCaptured(json.dumps(captured_white), json.dumps(captured_black))
        except Exception:
            pass


def play_move_sound(is_capture):
    if board.is_checkmate():
        if mate_sound:
            mate_sound.play()
    elif board.is_check():
        if check_sound:
            check_sound.play()
    elif is_capture:
        if capture_sound:
            capture_sound.play()
    else:
        if move_sound:
            move_sound.play()


def reset_game():
    global board, game_over, winner, selected_square, dragging_piece, last_move, animating_piece
    board           = chess.Board()
    game_over       = False
    winner          = ""
    selected_square = None
    dragging_piece  = None
    last_move       = None
    animating_piece = None
    
    if platform.system() == "Emscripten":
        try:
            platform.window.resetMoves()
        except Exception:
            pass


# ---------------------------------------------
# Main loop
# ---------------------------------------------

# Cached button rects so we can hit-test without redrawing every event
play_again_rect_cached = None
quit_rect_cached       = None

async def main():
    global play_again_rect_cached, quit_rect_cached, selected_square, dragging_piece
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
    
                    # Pawn promotion -> auto-queen
                    piece_moved = board.piece_at(selected_square)
                    if (piece_moved
                            and piece_moved.piece_type == chess.PAWN
                            and chess.square_rank(target_square) in (0, 7)):
                        move = chess.Move(selected_square, target_square, promotion=chess.QUEEN)
    
                    if move in board.legal_moves:
                        is_capture = board.is_capture(move)   # check BEFORE push
                        piece_symbol = board.piece_at(selected_square).symbol()
                        
                        # Set up sliding animation
                        global animating_piece, last_move
                        animating_piece = {
                            'from_sq': selected_square,
                            'to_sq': target_square,
                            'symbol': piece_symbol,
                            'start_time': pygame.time.get_ticks(),
                            'duration': 150
                        }
                        last_move = move
                        
                        san = board.san(move)
                        board.push(move)
                        
                        if platform.system() == "Emscripten":
                            try:
                                platform.window.addMove(san)
                            except Exception:
                                pass
                                
                        play_move_sound(is_capture)
                        update_captured_js()
                        check_game_over()
    
                        if not game_over:
                            # Use asyncio.sleep instead of pygame.time.delay so browser doesn't freeze
                            await asyncio.sleep(AI_MOVE_DELAY_MS / 1000.0)
                            ai_move = await get_losing_move()
                            if ai_move:
                                is_capture_ai = board.is_capture(ai_move)
                                piece_symbol_ai = board.piece_at(ai_move.from_square).symbol()
                                animating_piece = {
                                    'from_sq': ai_move.from_square,
                                    'to_sq': ai_move.to_square,
                                    'symbol': piece_symbol_ai,
                                    'start_time': pygame.time.get_ticks(),
                                    'duration': 150
                                }
                                last_move = ai_move
                                san_ai = board.san(ai_move)
                                board.push(ai_move)
                                
                                if platform.system() == "Emscripten":
                                    try:
                                        platform.window.addMove(san_ai)
                                    except Exception:
                                        pass
                                        
                                play_move_sound(is_capture_ai)
                                update_captured_js()
                                check_game_over()
    
                    selected_square = None
                    dragging_piece  = None
    
        # Render
        screen.fill((0, 0, 0))
 
        draw_board()
        draw_pieces(pygame.time.get_ticks())
        draw_labels()
 
        if game_over:
            # FIX #4: render overlay once per frame, cache button rects
            mouse_pos = pygame.mouse.get_pos()
            play_again_rect_cached, quit_rect_cached = display_game_over(mouse_pos)
            
        pygame.display.flip()
        await asyncio.sleep(0)

    pygame.quit()

if __name__ == "__main__":
    asyncio.run(main())
