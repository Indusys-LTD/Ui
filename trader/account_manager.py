import MetaTrader5 as mt5
import json
import sys
from typing import Dict, List
import time
import logging
import os

from .strategy import Strategy
from .parameters import Account_Info, Account_Specific_Parameters

class AccountManager:
    def __init__(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('trading.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def initialize_mt5(self) -> bool:
        """Initialize MT5 connection"""
        if not mt5.initialize():
            print(f"MT5 initialization failed: {mt5.last_error()}")
            return False
        return True

    def load_accounts(self) -> List[Dict]:
        """Load account configurations from JSON file"""
        try:
            with open('accounts.json', 'r') as f:
                data = json.load(f)
                return data.get('accounts', [])
        except Exception as e:
            print(f"Error loading accounts.json: {e}")
            return []

    def validate_account(self, account: Dict) -> bool:
        required_fields = [
            'login', 'password', 'server', 'default_symbol',
            'tpPoints', 'maxPositions', 'minDeviationDistance',
            'deviationIncreaseFactor'
        ]
        return all(field in account for field in required_fields)

    def cleanup_strategies(self, strategies: Dict):
        """Cleanup strategy instances"""
        for login, strategy in strategies.items():
            try:
                strategy.stop()
                strategy.cleanup()
            except Exception as e:
                self.logger.error(f"Error cleaning up strategy for account {login}: {e}")

    def monitor_performance(self, strategies: Dict):
        """Monitor strategy performance"""
        for login, strategy in strategies.items():
            stats = strategy.get_stats()
            if stats['consecutive_losses'] > 5:
                self.logger.warning(f"Account {login} has {stats['consecutive_losses']} consecutive losses")
            if stats['total_profit'] < -1000:
                self.logger.warning(f"Account {login} has significant losses: {stats['total_profit']}")

    def create_account_info(self, account: Dict) -> Account_Info:
        """Convert account dictionary to Account_Info object"""
        params = Account_Specific_Parameters(
            symbol=account['default_symbol'],
            tpPoints=float(account['tpPoints']),
            maxPositions=int(account['maxPositions']),
            minDeviationDistance=float(account['minDeviationDistance']),
            deviationIncreaseFactor=float(account['deviationIncreaseFactor'])
        )
        
        return Account_Info(
            parameters=params,
            login=int(account['login']),
            password=account['password'],
            server=account['server'],
            symbol=account['default_symbol'])

    def run(self):
        # Initialize MT5
        if not self.initialize_mt5():
            sys.exit(1)

        try:
            # Load accounts
            accounts = self.load_accounts()
            if not accounts:
                self.logger.error("No accounts found in configuration")
                sys.exit(1)
            
            while True:
                for account in accounts:
                    try:
                        if not self.validate_account(account):
                            self.logger.error(f"Invalid account configuration for {account.get('login', 'unknown')}")
                            continue
                        # Login to the account
                        if mt5.login(account['login'], account['password'], account['server']):
                            print(f"Account {account['login']} | Balance: {mt5.account_info().balance} | Equity: {mt5.account_info().equity}")
                            time.sleep(3) # Wait for 3 seconds to allow the account to be ready
                            account_info = self.create_account_info(account)
                            strategy = Strategy(account_info)
                            strategy.Run()
                                
                        else:
                            self.logger.error(f"Login failed for account {account['login']}: {mt5.last_error()}")
                    except Exception as e:
                        self.logger.error(f"Error initializing strategy for account {account.get('login', 'unknown')}: {str(e)}")

        except KeyboardInterrupt:
            print("\nShutting down gracefully...")
        except Exception as e:
            print(f"Unexpected error: {e}")
        finally:
            mt5.shutdown()

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        mt5.shutdown()