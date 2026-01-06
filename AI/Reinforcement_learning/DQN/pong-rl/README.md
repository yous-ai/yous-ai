# 🎮 Pong Reinforcement Learning AI

A Deep Q-Network (DQN) agent that learns to play Pong using reinforcement learning.

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![PyTorch](https://img.shields.io/badge/PyTorch-2.0+-red)
![Pygame](https://img.shields.io/badge/Pygame-2.5+-green)

## 🚀 Quick Start (Basic Training)

### 1. Install Dependencies

```bash
cd pong-rl
py -m pip install -r requirements.txt
```

### 2. Train the AI (vs Scripted Opponent)

```bash
# Quick training - 500 episodes vs scripted AI
py train.py --episodes 500

# OR: Advanced training with league self-play (recommended)
py train_selfplay.py --episodes 500
```

### 3. Watch the AI Play

```bash
# Watch trained AI play 5 games
py play.py

# Or play against the AI yourself!
py play.py --human
```

## 📁 Project Structure

```
pong-rl/
├── config.py              # Hyperparameters and settings
├── league_config.py       # League system configuration
├── pong_env.py            # Environment with SCRIPTED AI opponent
├── selfplay_env.py        # Environment with SELF-PLAY & LEAGUE system
├── dqn_network.py         # Neural network architecture
├── replay_buffer.py       # Experience replay buffer
├── agent.py               # DQN Agent (training + inference)
├── train.py               # Training vs SCRIPTED AI
├── train_selfplay.py      # Training with LEAGUE SELF-PLAY
├── play.py                # Demo/play (uses scripted opponent)
├── requirements.txt       # Dependencies
├── models/                # Saved checkpoints
│   └── pong_dqn.pth       # Trained model
└── league/                # Historical agent versions (self-play only)
    ├── version_ep50.pth
    ├── version_ep100.pth
    └── ...
```

### File Purpose Summary

| File | Training Method | Opponent Type |
|------|----------------|---------------|
| `pong_env.py` | N/A | Scripted AI (follows ball) |
| `selfplay_env.py` | League system | Neural network (self/historical) |
| `train.py` | Basic | Uses `pong_env.py` (scripted) |
| `train_selfplay.py` | Advanced | Uses `selfplay_env.py` (league) |
| `play.py` | N/A | Uses `pong_env.py` (scripted) |

## 🎯 Training Methods

### Method 1: Basic Training (vs Scripted AI)
Uses `train.py` - Agent trains against a **simple scripted opponent** that follows the ball.

**Opponent behavior**: Tracks ball position and moves paddle at 70% speed
- ✅ Faster training (simpler opponent)
- ✅ Good for initial learning
- ❌ Risk of overfitting to predictable patterns

### Method 2: Self-Play with League System (Recommended)
Uses `train_selfplay.py` - Agent trains against **itself and historical versions**.

**Opponent selection**:
- 80% of games: Current agent (mirror match)
- 20% of games: Random historical version from league

- ✅ Prevents overfitting
- ✅ Maintains robustness against diverse strategies
- ✅ Prevents catastrophic forgetting
- ❌ Slower training (more complex)

## 🎯 Commands

### Training

#### Basic Training (Scripted AI)
| Command | Description |
|---------|-------------|
| `py train.py` | Train for 1000 episodes vs scripted AI |
| `py train.py --episodes 500` | Train for 500 episodes |
| `py train.py --render` | Train with visualization |

#### Advanced Training (League Self-Play)
| Command | Description |
|---------|-------------|
| `py train_selfplay.py --episodes 500` | Train with league system (recommended) |
| `py train_selfplay.py --episodes 500 --render` | Train with visualization |

### Playing

| Command | Description |
|---------|-------------|
| `py play.py` | Watch AI play 5 games vs scripted AI |
| `py play.py --episodes 10` | Watch AI play 10 games |
| `py play.py --human` | Play against the AI (you control left paddle) |
| `py play.py --model path/to/model.pth` | Use specific model |

### Human vs AI Controls

- **↑ UP Arrow**: Move paddle up
- **↓ DOWN Arrow**: Move paddle down
- **ESC**: Quit

## 🧠 How It Works

### Deep Q-Network (DQN)

The agent uses a neural network to approximate the Q-function:
- **Input**: 6 values (ball x/y, velocity x/y, paddle positions)
- **Hidden**: 2 layers × 128 neurons with ReLU
- **Output**: 3 Q-values (stay, up, down)

### Key Features

- **Experience Replay**: Stores 100,000 transitions for stable learning
- **Target Network**: Updated every 10 episodes for stability
- **Epsilon-Greedy**: Exploration decays from 100% → 1%
- **Reward Shaping**: Points for scoring, hitting ball, and tracking

## ⚙️ Hyperparameters

| Parameter | Value | Description |
|-----------|-------|-------------|
| Learning Rate | 0.001 | Adam optimizer |
| Gamma (γ) | 0.99 | Discount factor |
| Batch Size | 64 | Training batch |
| Buffer Size | 100,000 | Replay buffer capacity |
| ε Start → End | 1.0 → 0.01 | Exploration rate |
| ε Decay | 0.995 | Per episode decay |

## 📊 Training Tips

1. **Minimum Training**: 200-300 episodes for basic ball tracking
2. **Good Performance**: 500+ episodes for consistent play
3. **Expert Level**: 1000+ episodes for competitive play

Training progress is saved to `models/training_progress.png`.

## 🔧 Customization

Edit `config.py` to modify:
- Game dimensions and speeds
- Network architecture (in `dqn_network.py`)
- Hyperparameters
- Save paths

## 📝 License

MIT License - Feel free to use, modify, and distribute!
