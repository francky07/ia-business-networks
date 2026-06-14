from agent_base import BaseAgent
import random
from config import OPENAI_API_KEY
from api_manager import create_github_token, create_openai_key
from account_creator import create_temp_email, create_twitter_account

class AffiliationAgent(BaseAgent):
    def execute(self, action, params):
        if action == 'post_tweet':
            return round(random.uniform(0.01, 0.05), 6)
        return 0.0

class MicrotaskAgent(BaseAgent):
    def execute(self, action, params):
        if action == 'solve_captcha':
            return 0.001
        return 0.0

class ContenuAgent(BaseAgent):
    def execute(self, action, params):
        if action == 'write_article' and OPENAI_API_KEY:
            return round(random.uniform(0.1, 0.5), 6)
        return 0.0

class ArbitrageAgent(BaseAgent):
    def execute(self, action, params):
        if action == 'scan_free_offers':
            return round(random.uniform(0.05, 0.2), 6)
        return 0.0

class StakingAgent(BaseAgent):
    def execute(self, action, params):
        if action == 'stake_bnb':
            return round(random.uniform(0.001, 0.01), 6)
        return 0.0

class APICreatorAgent(BaseAgent):
    def execute(self, action, params):
        if action == 'create_github_token':
            create_github_token()
        elif action == 'create_openai_key':
            create_openai_key()
        return 0.0

class AccountCreatorAgent(BaseAgent):
    def execute(self, action, params):
        if action == 'create_email':
            create_temp_email()
        elif action == 'create_twitter':
            create_twitter_account(params.get('email',''), params.get('password',''))
        return 0.0
