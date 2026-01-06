"""
Training script with League Self-Play System

Uses 80% self-play (current agent) and 20% historical opponents
to prevent overfitting and maintain robustness.
"""
import argparse
import os
import numpy as np
import matplotlib.pyplot as plt
from collections import deque

import config
import league_config
from selfplay_env import SelfPlayPongEnv, League
from agent import DQNAgent


def train_selfplay(episodes=config.EPISODES, render=False, 
                   save_interval=config.SAVE_INTERVAL):
    """
    Train the DQN agent using self-play with league system.
    
    - 80% of games: vs current self (mirror)
    - 20% of games: vs random historical version from league
    
    Args:
        episodes: Number of episodes to train
        render: Whether to render the game
        save_interval: Save model every N episodes
    """
    # Create environment and agent
    render_mode = 'human' if render else None
    env = SelfPlayPongEnv(render_mode=render_mode)
    agent = DQNAgent()
    
    # Auto-resume from existing model if available
    start_episode = 0
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
    
    # Initialize league
    league = League(
        max_size=league_config.MAX_LEAGUE_SIZE,
        league_dir=league_config.LEAGUE_DIR
    )
    
    # Check league directory for highest episode count (in case model file is older or missing episode data)
    league_files = [f for f in os.listdir(league_config.LEAGUE_DIR) if f.startswith('version_ep') and f.endswith('.pth')]
    if league_files and start_episode == 0:
        max_league_ep = 0
        for f in league_files:
            try:
                ep_num = int(f.replace('version_ep', '').replace('.pth', ''))
                max_league_ep = max(max_league_ep, ep_num)
            except ValueError:
                pass
        
        if max_league_ep > start_episode:
             print(f"Found league versions up to episode {max_league_ep}. Updating start episode.")
             start_episode = max_league_ep

    # Training metrics
    recent_rewards = deque(maxlen=100)
    best_avg_reward = float('-inf')
    wins_vs_self = 0
    wins_vs_historical = 0
    games_vs_self = 0
    games_vs_historical = 0
    
    print("=" * 70)
    print("SELF-PLAY TRAINING WITH LEAGUE SYSTEM")
    print("=" * 70)
    print(f"Episodes: {episodes} (starting from {start_episode})")
    print(f"Current agent ratio: {league_config.CURRENT_AGENT_RATIO * 100:.0f}%")
    print(f"Historical agent ratio: {league_config.HISTORICAL_AGENT_RATIO * 100:.0f}%")
    print(f"League size: {league_config.MAX_LEAGUE_SIZE}")
    print(f"Epsilon: {agent.epsilon:.4f} (will decay to {config.EPSILON_END})")
    print("-" * 70)
    
    for episode in range(start_episode + 1, start_episode + episodes + 1):
        # Decide opponent type for this episode
        if len(league) > 0 and np.random.random() < league_config.HISTORICAL_AGENT_RATIO:
            # Play against historical version (20%)
            opponent_net = league.get_random_opponent()
            env.set_opponent(opponent_net, "historical")
            games_vs_historical += 1
        else:
            # Play against current self (80%)
            # Use a copy of current policy network
            env.set_opponent(agent.policy_net, "self")
            games_vs_self += 1
        
        state = env.reset()
        episode_reward = 0
        episode_losses = []
        
        while True:
            # Select and perform action
            action = agent.select_action(state)
            next_state, reward, done, info = env.step(action)
            
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
        
        # Track wins
        if info['player_score'] > info['opponent_score']:
            if info['opponent_type'] == "self":
                wins_vs_self += 1
            else:
                wins_vs_historical += 1
        
        # End of episode
        agent.decay_epsilon()
        recent_rewards.append(episode_reward)
        agent.episode_rewards.append(episode_reward)
        
        # Update target network periodically
        if episode % config.TARGET_UPDATE == 0:
            agent.update_target_network()
        
        # Add to league periodically
        if episode % league_config.LEAGUE_SAVE_INTERVAL == 0:
            league.add_version(agent, episode)
        
        # Calculate metrics
        avg_reward = np.mean(recent_rewards)
        avg_loss = np.mean(episode_losses) if episode_losses else 0
        
        # Print progress
        if episode % 10 == 0 or episode == 1:
            self_wr = (wins_vs_self / games_vs_self * 100) if games_vs_self > 0 else 0
            hist_wr = (wins_vs_historical / games_vs_historical * 100) if games_vs_historical > 0 else 0
            
            print(f"Ep {episode:4d} | "
                  f"Rew: {episode_reward:6.1f} | "
                  f"Avg: {avg_reward:6.1f} | "
                  f"Loss: {avg_loss:.4f} | "
                  f"eps: {agent.epsilon:.3f} | "
                  f"vs {info['opponent_type']:10s} | "
                  f"WR: Self {self_wr:4.0f}% Hist {hist_wr:4.0f}%")
        
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
    
    print("-" * 70)
    print("TRAINING COMPLETE!")
    print(f"Final average reward (100 ep): {np.mean(recent_rewards):.2f}")
    print(f"Best average reward: {best_avg_reward:.2f}")
    print(f"Games vs Self: {games_vs_self} (Win rate: {wins_vs_self/max(1,games_vs_self)*100:.1f}%)")
    print(f"Games vs Historical: {games_vs_historical} (Win rate: {wins_vs_historical/max(1,games_vs_historical)*100:.1f}%)")
    print("=" * 70)
    
    # Plot training progress
    plot_training(agent.episode_rewards, agent.training_losses)
    
    return agent


def plot_training(rewards, losses):
    """Plot training metrics."""
    fig, axes = plt.subplots(2, 1, figsize=(12, 8))
    
    # Plot rewards
    axes[0].plot(rewards, alpha=0.6, label='Episode Reward', color='blue')
    if len(rewards) >= 100:
        moving_avg = np.convolve(rewards, np.ones(100)/100, mode='valid')
        axes[0].plot(range(99, len(rewards)), moving_avg, 
                    color='red', linewidth=2, label='100-Episode Average')
    axes[0].axhline(y=0, color='gray', linestyle='--', alpha=0.5)
    axes[0].set_xlabel('Episode')
    axes[0].set_ylabel('Reward')
    axes[0].set_title('Training Rewards (Self-Play with League)')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)
    
    # Plot losses
    if losses:
        if len(losses) > 10000:
            step = len(losses) // 10000
            losses_plot = losses[::step]
        else:
            losses_plot = losses
        axes[1].plot(losses_plot, alpha=0.6, color='green')
        axes[1].set_xlabel('Training Step')
        axes[1].set_ylabel('Loss')
        axes[1].set_title('Training Loss')
        axes[1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    os.makedirs(config.MODEL_DIR, exist_ok=True)
    plot_path = os.path.join(config.MODEL_DIR, 'training_selfplay.png')
    plt.savefig(plot_path, dpi=100)
    print(f"Training plot saved to {plot_path}")
    plt.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Train Pong with Self-Play League System')
    parser.add_argument('--episodes', type=int, default=config.EPISODES,
                        help=f'Number of episodes (default: {config.EPISODES})')
    parser.add_argument('--render', action='store_true',
                        help='Render the game during training')
    parser.add_argument('--save-interval', type=int, default=config.SAVE_INTERVAL,
                        help=f'Save model every N episodes (default: {config.SAVE_INTERVAL})')
    
    args = parser.parse_args()
    train_selfplay(episodes=args.episodes, render=args.render, 
                   save_interval=args.save_interval)
