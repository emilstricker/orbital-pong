import asyncio
import pygame
import sys
import math
import random
from pygame import Color
from typing import Tuple, List

# Import your existing game
from orbital_pong import Game, WINDOW_SIZE

async def main():
    print("Starting game initialization...")
    pygame.init()
    print("Pygame initialized")
    
    # Set up display for web
    canvas = pygame.display.set_mode(WINDOW_SIZE, pygame.SCALED | pygame.RESIZABLE)
    pygame.display.set_caption("Orbital Pong")
    print("Display set up")
    
    try:
        # Create game instance
        game = Game()
        print("Game instance created")
        
        # Main game loop
        running = True
        while running:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type in (pygame.MOUSEMOTION, pygame.FINGERMOTION):
                    # Handle both mouse and touch events
                    if event.type == pygame.FINGERMOTION:
                        # Convert touch position to mouse position
                        x = event.x * WINDOW_SIZE[0]
                        y = event.y * WINDOW_SIZE[1]
                        game.move_paddles(y)
                    else:
                        game.move_paddles(event.pos[1])
            
            # Update game state
            game.run()
            
            # Keep the game running at 60 FPS
            await asyncio.sleep(0)
    except Exception as e:
        print(f"Error during game execution: {str(e)}")
        raise

print("Starting Orbital Pong...")
asyncio.run(main())
