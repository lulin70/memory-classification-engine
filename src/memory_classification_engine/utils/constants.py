"""Configuration constants for Memory Classification Engine.

This module contains all default configuration values used across the system.
All hardcoded values should be defined here and imported where needed.
"""

# Comment in Chinese removedconds)
DEFAULT_CACHE_TTL = 3600  # Comment in Chinese removedr
DEFAULT_FILE_CACHE_TTL = 86400  # Comment in Chinese removedrs
DEFAULT_ARCHIVE_INTERVAL = 86400  # Comment in Chinese removedrs
DEFAULT_BUSY_TIMEOUT = 30  # Comment in Chinese removedconds
DEFAULT_BATCH_INTERVAL = 0.5  # Comment in Chinese removedconds

# Comment in Chinese removednts
DEFAULT_CACHE_SIZE = 1000
DEFAULT_FILE_CACHE_SIZE = 1000
DEFAULT_MAX_CONNECTIONS = 10
DEFAULT_MAX_FEATURES = 1000
DEFAULT_INTERACTION_LIMIT = 1000
DEFAULT_WORK_MEMORY_SIZE = 100

# Comment in Chinese removednts
DEFAULT_DISCOVERY_PORT = 5000
DEFAULT_DISCOVERY_INTERVAL = 30  # Comment in Chinese removedconds

# Comment in Chinese removednts
DEFAULT_CONFIDENCE = 1.0
DEFAULT_MIN_WEIGHT = 0.1
DEFAULT_DECAY_FACTOR = 0.9
DEFAULT_BEHAVIOR_DECAY = 0.9
DEFAULT_TIME_NOVELTY = 0.5
DEFAULT_SOURCE_PRIORITY_RULE = 4.0
DEFAULT_SOURCE_PRIORITY_PATTERN = 3.0
DEFAULT_SOURCE_PRIORITY_SEMANTIC = 2.0
DEFAULT_SOURCE_PRIORITY_DEFAULT = 1.0

# Comment in Chinese removedights
DEFAULT_RELEVANCE_WEIGHT = 0.4
DEFAULT_DIVERSITY_WEIGHT = 0.3
DEFAULT_NOVELTY_WEIGHT = 0.3

# Comment in Chinese removednts
DEFAULT_PAGE_SIZE = 4096
DEFAULT_CACHE_PAGES = 10000
DEFAULT_PRAGMA_SYNCHRONOUS = "NORMAL"

# Comment in Chinese removedsholds
DEFAULT_COMPRESSION_THRESHOLD_DAYS = 30
DEFAULT_SUPER_COMPRESSION_THRESHOLD_DAYS = 90

# Comment in Chinese removedths
DEFAULT_DATA_PATH = "./data"
DEFAULT_TIER2_PATH = "./data/tier2"
DEFAULT_TIER3_PATH = "./data/tier3"
DEFAULT_TIER4_PATH = "./data/tier4"
DEFAULT_CACHE_DIR = ".cache"

# Comment in Chinese removednts
DEFAULT_CONCURRENCY_LIMIT = 10
DEFAULT_BATCH_SIZE = 10

# Comment in Chinese removednts
DEFAULT_LANGUAGE = "en"
DEFAULT_LANGUAGE_CONFIDENCE = 0.0

# Comment in Chinese removednts
DEFAULT_RECENCY_DECAY_RATE = 0.1
DEFAULT_FREQUENCY_MULTIPLIER = 0.5
DEFAULT_FREQUENCY_EXPONENT = 0.5

# Comment in Chinese removedsholds
DEFAULT_MIN_SIMILARITY = 0.5
DEFAULT_STRONG_ASSOCIATION_THRESHOLD = 0.6

# Comment in Chinese removedl limits
DEFAULT_MEMORY_RETRIEVAL_LIMIT = 100
DEFAULT_ASSOCIATION_RETRIEVAL_LIMIT = 3
DEFAULT_TOTAL_MEMORY_RETRIEVAL_LIMIT = 300
DEFAULT_TIER_MEMORY_RETRIEVAL_LIMIT = 1000

# Comment in Chinese removedshold
DEFAULT_TOPIC_CONTINUITY_THRESHOLD = 0.6

# Comment in Chinese removedtion history limit
DEFAULT_CONVERSATION_HISTORY_LIMIT = 10

# Comment in Chinese removedrsion
ENGINE_VERSION = "0.2.0"
