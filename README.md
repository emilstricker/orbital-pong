# Orbital Pong

A modern twist on the classic Pong game, featuring orbital mechanics, particle effects, and dynamic lighting!

## Features
- Unique orbital gameplay mechanics
- Beautiful particle effects and dynamic lighting
- Increasing difficulty as you progress
- Smooth animations and visual effects
- Portrait mode optimized for modern displays

## Installation

1. Make sure you have Python 3.7+ installed
2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## How to Play

Run the game:
```bash
python orbital_pong.py
```

### Controls
- Move paddles using mouse movement
- Try to keep the ball in play by bouncing it off the paddles
- Score points by successfully deflecting the ball
- Watch out for the central orb's gravity effect!

## Play Online

You can play the game directly in your browser (including mobile devices) at:
`https://emilstricker.github.io/orbital-pong`

Note: The game may take a few moments to load in your browser.

## Development

This game was developed using:
- Python 3.7+
- Pygame 2.5.2
- Pygbag for web deployment

## Deployment

The game is automatically deployed to GitHub Pages when changes are pushed to the main branch.

To deploy manually:
1. Install Pygbag: `pip install pygbag`
2. Build the web version: `pygbag --build .`
3. The built files will be in `build/web`

## Assets
Make sure the following files are present in the game directory:
- PressStart2P.ttf (font file)
- asteroid.jpg (texture for the central orb)

## License
MIT License - Feel free to use, modify, and distribute!
