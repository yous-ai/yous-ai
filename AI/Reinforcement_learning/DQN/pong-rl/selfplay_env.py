"""
Self-Play Environment Wrapper for Authentic Atari (Gymnasium)
NOTE: Due to PettingZoo build limitations on Windows (missing C++ tools),
we fallback to Gymnasium 'PongNoFrameskip-v4'.
This means 'Self-Play' effectively becomes 'Training against Authentic CPU'.
The League system is preserved for saving versions (Hall of Fame) but active opponents are built-in CPU.
"""
import gymnasium as gym
import ale_py
from gymnasium.wrappers import AtariPreprocessing, FrameStackObservation
import numpy as np
import os
import torch
import config

class SelfPlayPongEnv:
    def __init__(self, render_mode=None):
        self.render_mode = render_mode
        
        # Initialize Authentic Atari Environment (Player vs CPU)
        self.env = gym.make("PongNoFrameskip-v4", render_mode=render_mode)
        self.env = AtariPreprocessing(self.env, screen_size=84, grayscale_obs=True, frame_skip=4, scale_obs=False)
        self.env = FrameStackObservation(self.env, stack_size=4)
        
        self.opponent_type = "authentic_cpu"
        
    def reset(self):
        obs, info = self.env.reset()
        return np.array(obs, dtype=np.float32)

    def set_opponent(self, policy_net, opponent_type="authentic_cpu"):
        """
        Placeholder for setting opponent.
        In this Authentic CPU version, we cannot control the opponent.
        """
        self.opponent_type = "authentic_cpu"

    def step(self, action):
        """
        Step environment. Opponent is controlled by Atari Game Engine (CPU).
        """
        obs, reward, terminated, truncated, info = self.env.step(action)
        done = terminated or truncated
        
        # Inject Score Info from RAM
        if hasattr(self.env.unwrapped, 'ale'):
            ram = self.env.unwrapped.ale.getRAM()
            info['player_score'] = ram[13]
            info['opponent_score'] = ram[14]
        else:
             info['player_score'] = 0 if reward <= 0 else 1
             info['opponent_score'] = 0 if reward >= 0 else 1
        
        info['opponent_type'] = self.opponent_type
        
        return np.array(obs, dtype=np.float32), reward, done, info

    def close(self):
        self.env.close()

class League:
    """
    Manages historical versions.
    In Gymnasium Fallback mode, this acts as a Hall of Fame (saver) only.
    """
    def __init__(self, max_size=10, league_dir="league"):
        self.league_dir = league_dir
        self.versions = []
        if not os.path.exists(league_dir):
            os.makedirs(league_dir)
            
    def add_version(self, agent, episode):
        """Save current agent to league history."""
        filename = f"version_ep{episode}.pth"
        path = os.path.join(self.league_dir, filename)
        torch.save(agent.policy_net.state_dict(), path)
        print(f"Added version {episode} to League Hall of Fame")
        
    def get_random_opponent(self):
        """Cannot load opponents in CPU mode."""
        return None
        
    def __len__(self):
        return 0
