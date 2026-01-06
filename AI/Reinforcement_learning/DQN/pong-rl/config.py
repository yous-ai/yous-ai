# Hyperparameters and Configuration for Pong RL

# Environment settings
SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480
PADDLE_WIDTH = 10
PADDLE_HEIGHT = 60
BALL_SIZE = 10
PADDLE_SPEED = 8
BALL_SPEED = 7
BALL_SPEED_MULTIPLIER = 1.03  # Authentic: ~3% speed increase per hit
MAX_BALL_SPEED_MULTIPLIER = 3.0  # Cap at 3x speed (functional limit of original)

# DQN Hyperparameters
LEARNING_RATE = 1e-4  # Lower learning rate for CNN stability
GAMMA = 0.99  # Discount factor
EPSILON_START = 1.0  # Initial exploration rate
EPSILON_END = 0.02  # Final exploration rate (slightly higher for complex state)
EPSILON_DECAY = 0.999985  # Slower decay (~1M frames to decay)
BATCH_SIZE = 32  # Standard Atari batch size
BUFFER_SIZE = 100000  # Replay buffer capacity
TARGET_UPDATE = 1000  # Update target less frequently for stability

# Training settings
EPISODES = 2000  # More episodes needed for visual learning
MAX_STEPS_PER_EPISODE = 10000
SAVE_INTERVAL = 50  # Save model every N episodes

# State and action dimensions
STATE_DIM = (4, 84, 84)  # 4 Stacked Grayscale Frames (C, H, W)
ACTION_DIM = 6  # Atari action space (0:NOOP, 1:FIRE, 2:UP, 3:DOWN, 4:UPFIRE, 5:DOWNFIRE)

# Paths
MODEL_DIR = "models"
MODEL_NAME = "pong_dqn.pth"
