# LoserChess

The chess game where the AI actively tries to lose.

[![Play Live Demo](https://img.shields.io/badge/Play-Live%20Demo-brightgreen?style=for-the-badge)](https://mohinvinayak.github.io/LoserChess/)

Live Demo: https://mohinvinayak.github.io/LoserChess/

![LoserChess Gameplay](assets/screenshot1.png)

## What is LoserChess?

LoserChess is a twist on the classic game of chess built with Python and Pygame. Instead of playing the best possible moves, the built-in AI evaluates the board to find the absolute worst move it can make.

Traditional chess engines attempt to maximize their chances of winning. LoserChess reverses this logic. The AI actively seeks losing positions, hangs pieces, walks into tactical mistakes, and helps the player win as quickly as possible.

The project demonstrates how changing an evaluation function can completely alter the behavior of an AI system while using the same game rules and search process.

## Features

### Anti-Stockfish AI

A custom evaluation function designed to make the AI lose:

- Prioritizes losing material
- Rewards hanging pieces
- Avoids strong positional play
- Walks into tactical blunders
- Selects moves that make checkmate easier
- Immediately chooses a move that allows forced checkmate when available

### Modern Chess Interface

Inspired by modern online chess platforms:

- Floating sidebars on widescreen displays
- Clean board layout
- Responsive interface
- Optimized for desktop and mobile screens

### Captured Material Tracker

- Displays captured pieces for both sides
- Updates in real time
- Uses solid piece icons for clarity

### PGN Move History

- Live move notation log
- Scrollable move list
- Standard chess notation

### Smooth Piece Animations

- 150ms movement interpolation
- Pieces glide between squares
- Improved visual feedback

### Audio Feedback

Distinct sound effects for:

- Standard moves
- Captures
- Checks
- Checkmates
- Game completion

### Board Highlights

- Selected piece highlighting
- Move destination indicators
- Last move visualization
- Improved move readability

### Full Chess Rules

Powered by `python-chess`:

- Legal move validation
- Castling
- En passant
- Pawn promotion
- Check and checkmate detection
- Stalemate detection
- Draw conditions

## Installation

### Clone the Repository

```bash
git clone https://github.com/MohinVinayak/LoserChess.git
cd LoserChess
```

### Install Dependencies

```bash
pip install pygame chess
```

### Run the Game

```bash
python main.py
```

## Playing Online

The game is deployed using GitHub Pages and WebAssembly.

https://mohinvinayak.github.io/LoserChess/

No installation is required.

## Building for the Web

LoserChess can be compiled to run entirely in the browser using Pygbag.

### Install Pygbag

```bash
pip install pygbag
```

### Build

```bash
python -m pygbag --template web.tmpl --width 800 --height 800 --icon favicon.png --build .
```

The compiled output will be generated in:

```text
build/web/
```

This directory can be deployed directly to any static hosting platform.

## How the Losing AI Works

Most chess engines evaluate positions and choose moves that improve their chances of winning.

LoserChess intentionally does the opposite.

For every legal move, the AI evaluates the resulting position and prefers outcomes that are objectively worse for itself. Material loss, exposed pieces, weak king safety, and tactical mistakes are treated as desirable outcomes.

As a result, the AI consistently chooses moves that a traditional engine would reject.

If a move exists that allows the player to immediately checkmate the AI, that move becomes the highest-priority choice.

## Tech Stack

- Python
- Pygame
- python-chess
- Pygbag
- WebAssembly
- GitHub Pages

## License

This project is licensed under the MIT License.

## Author

Mohin Vinayak

GitHub: https://github.com/MohinVinayak

Repository: https://github.com/MohinVinayak/LoserChess

Live Demo: https://mohinvinayak.github.io/LoserChess/
