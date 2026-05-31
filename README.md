# LoserChess

**The chess game where the AI actively tries to lose.**

![LoserChess Gameplay](assets/screenshot1.png)

## What is LoserChess?
LoserChess is a twist on the classic game of chess built with Python and Pygame. Instead of playing the best possible moves, the built-in AI evaluates the board to find the absolute **worst** move it can make. It wants to give away its pieces, walk into checks, and ultimately force you to checkmate it.

## Features
* **Anti-Stockfish AI**: A custom evaluation function that prioritizes self-destruction, piece blunders, and moving into mating nets.
* **Lichess/Chess.com Style UI**: Floating left and right sidebars on widescreen displays showing:
  * **Captured Material Tracker**: Solid-filled icons displaying White and Black captured pieces.
  * **PGN Move History Log**: Scrollable live move notation list.
* **Smooth Sliding Animations**: Pieces glide smoothly between squares (150ms interpolation) instead of instantly teleporting.
* **High-Fidelity Audio Cues**: Distinct Lichess-derived sound effects for normal moves, captures, checks, and checkmate/victory.
* **Smart Board Accents**: Translucent green highlighting on selected pieces, hollow black rings around pieces on target squares, and soft yellow highlights on source/target squares of the last move.
* **Mobile-Responsive**: Side panels automatically hide on vertical/narrow viewports to maximize the 1:1 square chessboard.
* **Rules Enforcement**: Powered by `python-chess` to handle all complex chess rules (en passant, castling, auto-queen promotion, and draw conditions).

## Installation & Setup

### Running Locally
1. **Clone the repository:**
   ```bash
   git clone https://github.com/MohinVinayak/LoserChess.git
   cd LoserChess
   ```

2. **Install dependencies:**
   Make sure you have Python installed, then run:
   ```bash
   pip install pygame chess
   ```

3. **Run the game:**
   ```bash
   python main.py
   ```

### Building for the Web (WebAssembly)
LoserChess is fully compiled for browsers using Pygbag. To re-compile and bundle the assets:
```bash
python -m pygbag --template web.tmpl --width 800 --height 800 --icon favicon.png --build .
```
The compiled output is located in `build/web/` and is ready for static host deployment (e.g. GitHub Pages).

## How the "Losing" AI Works
Standard chess engines evaluate a board and try to maximize their score. LoserChess reverses this logic. When it evaluates legal moves, it looks for outcomes that result in a drastically lower score for itself.

* It actively penalizes moves that capture your pieces.
* It actively rewards moves where you can capture its pieces on the next turn.
* If it sees a move that allows you to checkmate it, it will immediately play it.

## License
This project is open source and available under the MIT License.