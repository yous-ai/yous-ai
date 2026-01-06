# League System Configuration

# Self-play settings
SELF_PLAY_ENABLED = True
CURRENT_AGENT_RATIO = 0.8  # 80% games against current self
HISTORICAL_AGENT_RATIO = 0.2  # 20% games against historical versions

# League settings
MAX_LEAGUE_SIZE = 10  # Keep last N versions in the league
LEAGUE_SAVE_INTERVAL = 50  # Save to league every N episodes
LEAGUE_DIR = "league"  # Directory for league checkpoints
