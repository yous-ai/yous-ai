"""
Experience Replay Buffer for DQN
"""
import numpy as np
from collections import deque
import random
import config


class ReplayBuffer:
    """
    Experience replay buffer for storing and sampling transitions.
    
    Stores tuples of (state, action, reward, next_state, done).
    """
    
    def __init__(self, capacity=config.BUFFER_SIZE):
        """
        Initialize the replay buffer.
        
        Args:
            capacity: Maximum number of transitions to store
        """
        self.buffer = deque(maxlen=capacity)
    
    def push(self, state, action, reward, next_state, done):
        """
        Add a transition to the buffer.
        
        Args:
            state: Current state
            action: Action taken
            reward: Reward received
            next_state: Next state
            done: Whether episode ended
        """
        self.buffer.append((state, action, reward, next_state, done))
    
    def sample(self, batch_size=config.BATCH_SIZE):
        """
        Sample a batch of transitions.
        
        Args:
            batch_size: Number of transitions to sample
            
        Returns:
            Tuple of (states, actions, rewards, next_states, dones) as numpy arrays
        """
        batch = random.sample(self.buffer, batch_size)
        
        states = np.array([t[0] for t in batch], dtype=np.float32)
        actions = np.array([t[1] for t in batch], dtype=np.int64)
        rewards = np.array([t[2] for t in batch], dtype=np.float32)
        next_states = np.array([t[3] for t in batch], dtype=np.float32)
        dones = np.array([t[4] for t in batch], dtype=np.float32)
        
        return states, actions, rewards, next_states, dones
    
    def __len__(self):
        """Return the current size of the buffer."""
        return len(self.buffer)
    
    def is_ready(self, batch_size=config.BATCH_SIZE):
        """Check if buffer has enough samples for a batch."""
        return len(self.buffer) >= batch_size


def test_replay_buffer():
    """Test the replay buffer."""
    print("Testing Replay Buffer...")
    
    buffer = ReplayBuffer(capacity=1000)
    print(f"Initial buffer size: {len(buffer)}")
    
    # Add some transitions
    for i in range(100):
        state = np.random.randn(config.STATE_DIM).astype(np.float32)
        action = np.random.randint(0, config.ACTION_DIM)
        reward = np.random.randn()
        next_state = np.random.randn(config.STATE_DIM).astype(np.float32)
        done = np.random.random() < 0.1
        
        buffer.push(state, action, reward, next_state, done)
    
    print(f"Buffer size after 100 pushes: {len(buffer)}")
    print(f"Buffer ready for batch of 64: {buffer.is_ready(64)}")
    
    # Sample a batch
    states, actions, rewards, next_states, dones = buffer.sample(32)
    print(f"Sampled batch shapes:")
    print(f"  states: {states.shape}")
    print(f"  actions: {actions.shape}")
    print(f"  rewards: {rewards.shape}")
    print(f"  next_states: {next_states.shape}")
    print(f"  dones: {dones.shape}")
    
    # Test capacity limit
    for i in range(2000):
        state = np.random.randn(config.STATE_DIM).astype(np.float32)
        buffer.push(state, 0, 0, state, False)
    
    print(f"Buffer size after 2100 total pushes (capacity 1000): {len(buffer)}")
    
    print("\nReplay Buffer test passed!")


if __name__ == "__main__":
    test_replay_buffer()
