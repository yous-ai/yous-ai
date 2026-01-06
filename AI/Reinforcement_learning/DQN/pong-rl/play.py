"""
Play/Inference script for Authentic Atari Pong
"""
import argparse
import pygame
import numpy as np
import os
import torch
import config
from pong_env import PongEnv
from agent import DQNAgent

def play_ai(model_path, episodes=5, fps=30):
    """
    Watch the Trained AI play against the Atari CPU.
    """
    # Create environment (Human render mode for visualization)
    env = PongEnv(render_mode='human')
    agent = DQNAgent(state_dim=config.STATE_DIM, action_dim=config.ACTION_DIM)
    
    # Load trained model
    if os.path.exists(model_path):
        agent.load(model_path)
        agent.epsilon = 0.00  # Pure exploitation
        print(f"Loaded AI model from {model_path}")
    else:
        print(f"Warning: Model not found at {model_path}. Using Random Agent.")
        agent.epsilon = 1.0

    print(f"Playing {episodes} episodes against Atari CPU...")
    # FPS control
    clock = pygame.time.Clock()
    
    for episode in range(1, episodes + 1):
        state = env.reset()
        episode_reward = 0
        
        while True:
            # Select action
            action = agent.select_action(state)
            
            # Step
            next_state, reward, done, info = env.step(action)
            
            # Render is handled by Gymnasium window
            # But we need to keep the window responsive/open?
            # Gym's render_mode='human' usually handles it, but requires process events?
            # Usually calling env.render() is safe.
            # And we need to tick clock?
            
            # NOTE: render_mode='human' in ALE uses SDL. 
            # We don't need to manually verify events unless we want to close gracefully.
            
            episode_reward += reward
            state = next_state
            
            # Limit FPS to watchable speed (Atari is 60, but 30 is easier to see)
            # ALE runs fast.
            # Ideally we sleep?
            # pygame.time.Clock().tick(fps) works if we initialize pygame?
            # ALE initializes pygame display. We can access it via pygame.
            clock.tick(fps)
            
            if done:
                break
        
        # Result
        score_diff = info.get('player_score', 0) - info.get('opponent_score', 0)
        result = "WIN" if score_diff > 0 else "LOSS"
        print(f"Episode {episode}: {result} | Score: {int(info.get('player_score', 0))}-{int(info.get('opponent_score', 0))}")
    
    env.close()

def play_human(fps=30):
    """
    Play Pong yourself against the Atari CPU.
    """
    env = PongEnv(render_mode='human')
    print("Playing Human vs Atari CPU")
    print("Controls: UP arrow, DOWN arrow")
    
    clock = pygame.time.Clock()
    
    while True:
        state = env.reset()
        while True:
            # Handle Events
            # Ale-Py uses SDL. We can use Pygame to get keys.
            pygame.event.pump()
            keys = pygame.key.get_pressed()
            
            action = 0 # NOOP
            if keys[pygame.K_UP]:
                action = 2 # RIGHT (Up in Pong)
            elif keys[pygame.K_DOWN]:
                action = 3 # LEFT (Down in Pong)
            elif keys[pygame.K_d]: # Option: Fire/Speed
                action = 1 
            elif keys[pygame.K_ESCAPE]:
                env.close()
                return

            # Step
            next_state, reward, done, info = env.step(action)
            
            clock.tick(fps)
            if done:
                print(f"Game Over. Score: {int(info.get('player_score', 0))}-{int(info.get('opponent_score', 0))}")
                break
                
    env.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Play Pong (Authentic Atari)')
    parser.add_argument('--model', type=str, 
                        default=os.path.join(config.MODEL_DIR, "best_model.pth"),
                        help='Path to trained model')
    parser.add_argument('--episodes', type=int, default=3,
                        help='Number of episodes for AI demo')
    parser.add_argument('--human', action='store_true',
                        help='Play as Human vs CPU')
    parser.add_argument('--fps', type=int, default=None,
                        help='FPS override (Default: 60 for Human, 30 for AI)')
    
    args = parser.parse_args()
    
    target_fps = args.fps
    if target_fps is None:
        target_fps = 60 if args.human else 30
    
    if args.human:
        play_human(fps=target_fps)
    else:
        play_ai(args.model, episodes=args.episodes, fps=target_fps)
