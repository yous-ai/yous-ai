"""
DQN Agent with training and inference capabilities
"""
import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import os

import config
from dqn_network import DQN
from replay_buffer import ReplayBuffer


class DQNAgent:
    """
    Deep Q-Network Agent for Pong.
    
    Features:
    - Epsilon-greedy exploration
    - Experience replay
    - Target network with periodic updates
    """
    
    def __init__(self, state_dim=config.STATE_DIM, action_dim=config.ACTION_DIM, 
                 learning_rate=config.LEARNING_RATE):
        """
        Initialize the DQN agent.
        
        Args:
            state_dim: Dimension of state space
            action_dim: Dimension of action space
            learning_rate: Learning rate for optimizer
        """
        self.state_dim = state_dim
        self.action_dim = action_dim
        
        # Device selection
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"Using device: {self.device}")
        
        # Networks
        self.policy_net = DQN(state_dim, action_dim).to(self.device)
        self.target_net = DQN(state_dim, action_dim).to(self.device)
        self.target_net.load_state_dict(self.policy_net.state_dict())
        self.target_net.eval()  # Target network is not trained directly
        
        # Optimizer
        self.optimizer = optim.Adam(self.policy_net.parameters(), lr=learning_rate)
        
        # Loss function (Huber loss for stability)
        self.criterion = nn.SmoothL1Loss()
        
        # Replay buffer
        self.memory = ReplayBuffer(config.BUFFER_SIZE)
        
        # Exploration parameters
        self.epsilon = config.EPSILON_START
        self.epsilon_end = config.EPSILON_END
        self.epsilon_decay = config.EPSILON_DECAY
        
        # Training metrics
        self.episode_rewards = []
    
    def select_action(self, state):
        """
        Select an action using epsilon-greedy policy.
        
        Args:
            state: Current state (numpy array)
            
        Returns:
            Selected action (int)
        """
        if np.random.random() < self.epsilon:
            return np.random.randint(0, self.action_dim)
        
        with torch.no_grad():
            state_tensor = torch.FloatTensor(state).unsqueeze(0).to(self.device)
            q_values = self.policy_net(state_tensor)
            return q_values.argmax(dim=1).item()
    
    def store_transition(self, state, action, reward, next_state, done):
        """Store a transition in replay buffer."""
        self.memory.push(state, action, reward, next_state, done)
    
    def train_step(self):
        """
        Perform one training step.
        
        Returns:
            Loss value if training occurred, None otherwise
        """
        if not self.memory.is_ready(config.BATCH_SIZE):
            return None
        
        # Sample batch
        states, actions, rewards, next_states, dones = self.memory.sample(config.BATCH_SIZE)
        
        # Convert to tensors
        states = torch.FloatTensor(states).to(self.device)
        actions = torch.LongTensor(actions).to(self.device)
        rewards = torch.FloatTensor(rewards).to(self.device)
        next_states = torch.FloatTensor(next_states).to(self.device)
        dones = torch.FloatTensor(dones).to(self.device)
        
        # Current Q values
        current_q = self.policy_net(states).gather(1, actions.unsqueeze(1)).squeeze(1)
        
        # Target Q values (using target network)
        with torch.no_grad():
            next_q = self.target_net(next_states).max(dim=1)[0]
            target_q = rewards + config.GAMMA * next_q * (1 - dones)
        
        # Loss
        loss = self.criterion(current_q, target_q)
        
        # Optimize
        self.optimizer.zero_grad()
        loss.backward()
        # Gradient clipping for stability
        torch.nn.utils.clip_grad_norm_(self.policy_net.parameters(), 1.0)
        self.optimizer.step()
        
        return loss.item()
    
    def update_target_network(self):
        """Copy weights from policy network to target network."""
        self.target_net.load_state_dict(self.policy_net.state_dict())
    
    def decay_epsilon(self):
        """Decay exploration rate."""
        self.epsilon = max(self.epsilon_end, self.epsilon * self.epsilon_decay)
    
    def save(self, path, episode=0):
        """Save model checkpoint."""
        os.makedirs(os.path.dirname(path) if os.path.dirname(path) else '.', exist_ok=True)
        torch.save({
            'policy_net_state_dict': self.policy_net.state_dict(),
            'target_net_state_dict': self.target_net.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'epsilon': self.epsilon,
            'episode_rewards': self.episode_rewards,
            'episode': episode
        }, path)
        print(f"Model saved to {path} (episode {episode})")
    
    def load(self, path):
        """Load model checkpoint."""
        if not os.path.exists(path):
            print(f"No checkpoint found at {path}")
            return None
        
        checkpoint = torch.load(path, map_location=self.device, weights_only=False)
        self.policy_net.load_state_dict(checkpoint['policy_net_state_dict'])
        self.target_net.load_state_dict(checkpoint['target_net_state_dict'])
        self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        self.epsilon = checkpoint['epsilon']
        self.episode_rewards = checkpoint.get('episode_rewards', [])
        
        episode = checkpoint.get('episode', 0)
        print(f"Model loaded from {path} (episode {episode})")
        return episode


def test_agent():
    """Test the DQN agent."""
    print("Testing DQN Agent...")
    
    # Create agent
    agent = DQNAgent()
    print(f"Policy network: {agent.policy_net}")
    
    # Test action selection
    state = np.random.randn(config.STATE_DIM).astype(np.float32)
    action = agent.select_action(state)
    print(f"Selected action: {action}")
    
    # Store some transitions
    for _ in range(100):
        state = np.random.randn(config.STATE_DIM).astype(np.float32)
        action = np.random.randint(0, config.ACTION_DIM)
        reward = np.random.randn()
        next_state = np.random.randn(config.STATE_DIM).astype(np.float32)
        done = False
        agent.store_transition(state, action, reward, next_state, done)
    
    print(f"Buffer size: {len(agent.memory)}")
    
    # Test training step
    loss = agent.train_step()
    print(f"Training loss: {loss:.4f}")
    
    # Test target network update
    agent.update_target_network()
    print("Target network updated")
    
    # Test epsilon decay
    old_epsilon = agent.epsilon
    agent.decay_epsilon()
    print(f"Epsilon: {old_epsilon:.4f} -> {agent.epsilon:.4f}")
    
    # Test save/load
    test_path = "models/test_checkpoint.pth"
    agent.save(test_path)
    agent.load(test_path)
    
    # Cleanup
    if os.path.exists(test_path):
        os.remove(test_path)
    
    print("\nDQN Agent test passed!")


if __name__ == "__main__":
    test_agent()
