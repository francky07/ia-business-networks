import os
from dotenv import load_dotenv
load_dotenv()

CYCLE_SECONDS = 60
NB_AGENTS_TOTAL = 10
NB_BOOSTERS_TOTAL = 5

NB_AFFILIATION = 2
NB_MICROTASK = 2
NB_CONTENU = 2
NB_ARBITRAGE = 2
NB_STAKING = 1
NB_API_CREATOR = 1
NB_ACCOUNT_CREATOR = 0

BSC_RPC = "https://bsc-dataseed.binance.org"
WALLET_PRIVATE_KEY = os.getenv("WALLET_PRIVATE_KEY")
WALLET_ADDRESS = os.getenv("WALLET_ADDRESS")

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
INFURA_PROJECT_ID = os.getenv("INFURA_PROJECT_ID")
INFURA_SECRET = os.getenv("INFURA_SECRET")
SSH_PRIVATE_KEY_PATH = os.getenv("SSH_PRIVATE_KEY_PATH", "~/.ssh/id_rsa")

WALLET_FILE = "wallet.json"
STATE_FILE = "state.json"
API_KEYS_DB = "api_keys.json"
ACCOUNTS_DB = "accounts.json"
LOG_FILE = "business.log"
