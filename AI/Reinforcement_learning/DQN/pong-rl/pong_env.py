"""
Pong Environment Wrapper for Gymnasium (Authentic Atari)
Uses 'PongNoFrameskip-v4' with standard DeepMind preprocessing.
"""
import gymnasium as gym
import ale_py
from gymnasium.wrappers import AtariPreprocessing, FrameStackObservation
import numpy as np
import config

class PongEnv:
    def __init__(self, render_mode=None):
        """
        Initialize Authentic Atari Pong.
        
        Args:
            render_mode: 'human' or None
        """
        # PongNoFrameskip-v4: Standard for RL benchmarking
        # v4 = No action repeat (handled by wrapper if needed)
        # NoFrameskip = No frame skipping in basic env (handled by wrapper)
        self.env = gym.make("PongNoFrameskip-v4", render_mode=render_mode)
        
        # DeepMind-style Preprocessing (Standard Nature DQN)
        # - Resize to 84x84
        # - Grayscale
        # - Frame Skip 4 (Play every 4th frame, max pool others)
        # - Scale Obs (False -> 0-255 uint8, True -> 0-1 float)
        # We keep False (uint8) to save memory in ReplayBuffer, conversion to float happens in Agent/Network
        self.env = AtariPreprocessing(self.env, screen_size=84, grayscale_obs=True, frame_skip=4, scale_obs=False)
        
        # Frame Stacking (4 frames)
        self.env = FrameStackObservation(self.env, stack_size=4)
        
    def reset(self):
        """Reset environment."""
        obs, info = self.env.reset()
        # Convert LazyFrames to numpy array (float32 for consistency with agent expectations)
        # Although storage is uint8, agent expects array.
        return np.array(obs, dtype=np.float32)

    def step(self, action):
        """Step environment."""
        obs, reward, terminated, truncated, info = self.env.step(action)
        done = terminated or truncated
        
        # Get Scores from RAM for consistent info
        # Pong RAM: 13 = Player, 14 = CPU
        if hasattr(self.env.unwrapped, 'ale'):
            ram = self.env.unwrapped.ale.getRAM()
            info['player_score'] = ram[13]
            info['opponent_score'] = ram[14]
        else:
            # Fallback if ALE not accessible
            info['player_score'] = 0
            info['opponent_score'] = 0
            
        return np.array(obs, dtype=np.float32), reward, done, info

    def render(self):
        """Render handled by env."""
        pass

    def close(self):
        self.env.close()
