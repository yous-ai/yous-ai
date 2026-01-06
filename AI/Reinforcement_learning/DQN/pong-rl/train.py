"""
Training script for Pong DQN Agent
"""
import argparse
import os
import numpy as np
import matplotlib.pyplot as plt
from collections import deque

import config
from pong_env import PongEnv
from agent import DQNAgent


def train(episodes=config.EPISODES, render=False, save_interval=config.SAVE_INTERVAL):
    """
    Train the DQN agent on Pong.
    
    Args:
        episodes: Number of episodes to train
        render: Whether to render the game
        save_interval: Save model every N episodes
    """
    # Create environment and agent
    render_mode = 'human' if render else None
    env = PongEnv(render_mode=render_mode)
    agent = DQNAgent()
    
    start_episode = 0
    # Auto-resume from existing model if available
    model_path = os.path.join(config.MODEL_DIR, config.MODEL_NAME)
    if os.path.exists(model_path):
        print(f"Found existing model at {model_path}")
        loaded_episode = agent.load(model_path)
        if loaded_episode is not None:
             start_episode = loaded_episode
             print(f"Resumed training from checkpoint (episode {start_episode}, epsilon: {agent.epsilon:.4f})")
        else:
            print("Failed to load model, starting fresh")
    else:
        print("No existing model found, starting fresh training")
    
    # Training metrics
    recent_rewards = deque(maxlen=100)
    best_avg_reward = float('-inf')
    avg_losses = []
    
    print(f"Starting training for {episodes} episodes (from {start_episode})...")
    print(f"Epsilon: {agent.epsilon:.4f} (will decay to {config.EPSILON_END})")
    print("-" * 60)
    
    for episode in range(start_episode + 1, start_episode + episodes + 1):
        state = env.reset()
        episode_reward = 0
        episode_losses = []
        
        while True:
            # Select and perform action
            action = agent.select_action(state)
            next_state, reward, done, info = env.step(action)
            
            # Render if enabled
            if render:
                env.render()
            
            # Store transition
            agent.store_transition(state, action, reward, next_state, done)
            
            # Train
            loss = agent.train_step()
            if loss is not None:
                episode_losses.append(loss)
            
            episode_reward += reward
            state = next_state
            
            if done:
                break
        
        # End of episode
        agent.decay_epsilon()
        recent_rewards.append(episode_reward)
        agent.episode_rewards.append(episode_reward)
        
        # Update target network periodically
        if episode % config.TARGET_UPDATE == 0:
            agent.update_target_network()
        
        # Calculate metrics
        avg_reward = np.mean(recent_rewards)
        avg_loss = np.mean(episode_losses) if episode_losses else 0
        avg_losses.append(avg_loss)
        
        # Print progress
        if episode % 10 == 0 or episode == 1:
            print(f"Episode {episode:4d} | "
                  f"Reward: {episode_reward:7.2f} | "
                  f"Avg(100): {avg_reward:7.2f} | "
                  f"Loss: {avg_loss:.4f} | "
                  f"Epsilon: {agent.epsilon:.4f} | "
                  f"Score: {info['player_score']}-{info['opponent_score']}")
        
        # Save best model
        if avg_reward > best_avg_reward and len(recent_rewards) == 100:
            best_avg_reward = avg_reward
            agent.save(os.path.join(config.MODEL_DIR, "best_model.pth"), episode)
        
        # Save periodic checkpoint
        if episode % save_interval == 0:
            agent.save(os.path.join(config.MODEL_DIR, config.MODEL_NAME), episode)
    
    # Final save
    agent.save(os.path.join(config.MODEL_DIR, config.MODEL_NAME), episode)
    env.close()
    
    print("-" * 60)
    print(f"Training complete!")
    print(f"Final average reward (100 episodes): {np.mean(recent_rewards):.2f}")
    print(f"Best average reward: {best_avg_reward:.2f}")
    
    # Plot training progress
    plot_training(agent.episode_rewards, avg_losses)
    
    return agent


def plot_training(rewards, losses):
    """Plot training metrics."""
    fig, axes = plt.subplots(2, 1, figsize=(10, 8))
    
    # Plot rewards
    axes[0].plot(rewards, alpha=0.6, label='Episode Reward')
    if len(rewards) >= 100:
        moving_avg = np.convolve(rewards, np.ones(100)/100, mode='valid')
        axes[0].plot(range(99, len(rewards)), moving_avg, 
                    color='red', linewidth=2, label='100-Episode Average')
    axes[0].set_xlabel('Episode')
    axes[0].set_ylabel('Reward')
    axes[0].set_title('Training Rewards')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)
    
    # Plot losses
    if losses:
        # Downsample for plotting if too many points
        if len(losses) > 10000:
            step = len(losses) // 10000
            losses_plot = losses[::step]
        else:
            losses_plot = losses
        axes[1].plot(losses_plot, alpha=0.6)
        axes[1].set_xlabel('Training Step')
        axes[1].set_ylabel('Loss')
        axes[1].set_title('Training Loss')
        axes[1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    # Save the plot
    os.makedirs(config.MODEL_DIR, exist_ok=True)
    plot_path = os.path.join(config.MODEL_DIR, 'training_progress.png')
    plt.savefig(plot_path)
    print(f"Training plot saved to {plot_path}")
    plt.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Train Pong DQN Agent')
    parser.add_argument('--episodes', type=int, default=config.EPISODES,
                        help=f'Number of episodes (default: {config.EPISODES})')
    parser.add_argument('--render', action='store_true',
                        help='Render the game during training')
    parser.add_argument('--save-interval', type=int, default=config.SAVE_INTERVAL,
                        help=f'Save model every N episodes (default: {config.SAVE_INTERVAL})')
    
    args = parser.parse_args()
    train(episodes=args.episodes, render=args.render, save_interval=args.save_interval)
