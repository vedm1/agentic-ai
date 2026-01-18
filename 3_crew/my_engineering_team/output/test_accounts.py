import unittest
from unittest.mock import patch
from accounts import Account, get_share_price


class TestGetSharePrice(unittest.TestCase):
    """Test cases for the get_share_price function."""
    
    def test_get_share_price_known_symbol(self):
        """Test getting price for a known symbol."""
        self.assertEqual(get_share_price("AAPL"), 150.0)
        self.assertEqual(get_share_price("TSLA"), 200.0)
        self.assertEqual(get_share_price("GOOGL"), 100.0)
    
    def test_get_share_price_unknown_symbol(self):
        """Test getting price for an unknown symbol."""
        self.assertEqual(get_share_price("UNKNOWN"), 0.0)
        self.assertEqual(get_share_price("XYZ"), 0.0)


class TestAccountInitialization(unittest.TestCase):
    """Test cases for Account initialization."""
    
    def test_account_initialization(self):
        """Test that an account is initialized correctly."""
        account = Account("user123", 1000.0)
        self.assertEqual(account.user_id, "user123")
        self.assertEqual(account.initial_deposit, 1000.0)
        self.assertEqual(account.cash_balance, 1000.0)
        self.assertEqual(account.portfolio, {})
        self.assertEqual(len(account.transactions), 1)
        self.assertEqual(account.transactions[0]["type"], "deposit")
        self.assertEqual(account.transactions[0]["amount"], 1000.0)
    
    def test_account_initialization_zero_deposit(self):
        """Test account initialization with zero deposit."""
        account = Account("user456", 0.0)
        self.assertEqual(account.cash_balance, 0.0)
        self.assertEqual(account.initial_deposit, 0.0)


class TestDepositFunds(unittest.TestCase):
    """Test cases for deposit_funds method."""
    
    def setUp(self):
        """Set up a test account before each test."""
        self.account = Account("user123", 1000.0)
    
    def test_deposit_funds(self):
        """Test depositing funds into account."""
        self.account.deposit_funds(500.0)
        self.assertEqual(self.account.cash_balance, 1500.0)
        self.assertEqual(len(self.account.transactions), 2)
        self.assertEqual(self.account.transactions[-1]["type"], "deposit")
        self.assertEqual(self.account.transactions[-1]["amount"], 500.0)
    
    def test_multiple_deposits(self):
        """Test multiple deposits."""
        self.account.deposit_funds(200.0)
        self.account.deposit_funds(300.0)
        self.assertEqual(self.account.cash_balance, 1500.0)
        self.assertEqual(len(self.account.transactions), 3)


class TestWithdrawFunds(unittest.TestCase):
    """Test cases for withdraw_funds method."""
    
    def setUp(self):
        """Set up a test account before each test."""
        self.account = Account("user123", 1000.0)
    
    def test_successful_withdrawal(self):
        """Test successful withdrawal of funds."""
        result = self.account.withdraw_funds(500.0)
        self.assertTrue(result)
        self.assertEqual(self.account.cash_balance, 500.0)
        self.assertEqual(len(self.account.transactions), 2)
        self.assertEqual(self.account.transactions[-1]["type"], "withdrawal")
    
    def test_insufficient_funds_withdrawal(self):
        """Test withdrawal with insufficient funds."""
        result = self.account.withdraw_funds(1500.0)
        self.assertFalse(result)
        self.assertEqual(self.account.cash_balance, 1000.0)
        self.assertEqual(len(self.account.transactions), 1)
    
    def test_exact_amount_withdrawal(self):
        """Test withdrawing exact account balance."""
        result = self.account.withdraw_funds(1000.0)
        self.assertTrue(result)
        self.assertEqual(self.account.cash_balance, 0.0)


class TestBuyShares(unittest.TestCase):
    """Test cases for buy_shares method."""
    
    def setUp(self):
        """Set up a test account before each test."""
        self.account = Account("user123", 10000.0)
    
    def test_successful_buy(self):
        """Test successful purchase of shares."""
        result = self.account.buy_shares("AAPL", 10)
        self.assertTrue(result)
        self.assertEqual(self.account.portfolio["AAPL"], 10)
        self.assertEqual(self.account.cash_balance, 8500.0)
        self.assertEqual(len(self.account.transactions), 2)
        self.assertEqual(self.account.transactions[-1]["type"], "buy")
    
    def test_buy_insufficient_funds(self):
        """Test buying shares with insufficient funds."""
        result = self.account.buy_shares("TSLA", 100)
        self.assertFalse(result)
        self.assertEqual(self.account.portfolio, {})
        self.assertEqual(self.account.cash_balance, 10000.0)
        self.assertEqual(len(self.account.transactions), 1)
    
    def test_buy_multiple_times_same_symbol(self):
        """Test buying the same symbol multiple times."""
        self.account.buy_shares("AAPL", 5)
        self.account.buy_shares("AAPL", 3)
        self.assertEqual(self.account.portfolio["AAPL"], 8)
        self.assertEqual(self.account.cash_balance, 8800.0)
    
    def test_buy_different_symbols(self):
        """Test buying different symbols."""
        self.account.buy_shares("AAPL", 5)
        self.account.buy_shares("GOOGL", 10)
        self.assertEqual(self.account.portfolio["AAPL"], 5)
        self.assertEqual(self.account.portfolio["GOOGL"], 10)
        self.assertEqual(self.account.cash_balance, 8250.0)
    
    def test_buy_unknown_symbol(self):
        """Test buying shares of unknown symbol."""
        result = self.account.buy_shares("UNKNOWN", 10)
        self.assertTrue(result)
        self.assertEqual(self.account.portfolio["UNKNOWN"], 10)
        self.assertEqual(self.account.cash_balance, 10000.0)


class TestSellShares(unittest.TestCase):
    """Test cases for sell_shares method."""
    
    def setUp(self):
        """Set up a test account with some shares before each test."""
        self.account = Account("user123", 10000.0)
        self.account.buy_shares("AAPL", 10)
        self.account.buy_shares("TSLA", 5)
    
    def test_successful_sell(self):
        """Test successful sale of shares."""
        initial_balance = self.account.cash_balance
        result = self.account.sell_shares("AAPL", 5)
        self.assertTrue(result)
        self.assertEqual(self.account.portfolio["AAPL"], 5)
        self.assertEqual(self.account.cash_balance, initial_balance + 750.0)
    
    def test_sell_all_shares_of_symbol(self):
        """Test selling all shares of a symbol removes it from portfolio."""
        result = self.account.sell_shares("AAPL", 10)
        self.assertTrue(result)
        self.assertNotIn("AAPL", self.account.portfolio)
    
    def test_sell_insufficient_shares(self):
        """Test selling more shares than owned."""
        result = self.account.sell_shares("AAPL", 20)
        self.assertFalse(result)
        self.assertEqual(self.account.portfolio["AAPL"], 10)
    
    def test_sell_unowned_symbol(self):
        """Test selling shares of unowned symbol."""
        result = self.account.sell_shares("GOOGL", 5)
        self.assertFalse(result)
        self.assertNotIn("GOOGL", self.account.portfolio)
    
    def test_sell_transaction_recorded(self):
        """Test that sell transaction is properly recorded."""
        self.account.sell_shares("TSLA", 2)
        last_transaction = self.account.transactions[-1]
        self.assertEqual(last_transaction["type"], "sell")
        self.assertEqual(last_transaction["symbol"], "TSLA")
        self.assertEqual(last_transaction["quantity"], 2)
        self.assertEqual(last_transaction["price"], 200.0)
        self.assertEqual(last_transaction["total_revenue"], 400.0)


class TestGetPortfolioValue(unittest.TestCase):
    """Test cases for get_portfolio_value method."""
    
    def test_portfolio_value_empty_portfolio(self):
        """Test portfolio value with no shares."""
        account = Account("user123", 1000.0)
        self.assertEqual(account.get_portfolio_value(), 1000.0)
    
    def test_portfolio_value_with_shares(self):
        """Test portfolio value with shares."""
        account = Account("user123", 10000.0)
        account.buy_shares("AAPL", 10)
        account.buy_shares("TSLA", 5)
        self.assertEqual(account.get_portfolio_value(), 10000.0)
    
    def test_portfolio_value_after_sell(self):
        """Test portfolio value after selling shares."""
        account = Account("user123", 10000.0)
        account.buy_shares("AAPL", 10)
        account.sell_shares("AAPL", 5)
        self.assertEqual(account.get_portfolio_value(), 10000.0)


class TestGetProfitLoss(unittest.TestCase):
    """Test cases for get_profit_loss method."""
    
    def test_profit_loss_no_change(self):
        """Test profit/loss with no transactions."""
        account = Account("user123", 1000.0)
        self.assertEqual(account.get_profit_loss(), 0.0)
    
    def test_profit_loss_after_trades(self):
        """Test profit/loss after buying and holding shares."""
        account = Account("user123", 10000.0)
        account.buy_shares("AAPL", 10)
        self.assertEqual(account.get_profit_loss(), 0.0)
    
    def test_profit_loss_after_withdrawal(self):
        """Test profit/loss after withdrawal."""
        account = Account("user123", 1000.0)
        account.withdraw_funds(500.0)
        self.assertEqual(account.get_profit_loss(), -500.0)
    
    def test_profit_loss_after_deposit(self):
        """Test profit/loss after deposit."""
        account = Account("user123", 1000.0)
        account.deposit_funds(500.0)
        self.assertEqual(account.get_profit_loss(), 500.0)


class TestGetHoldings(unittest.TestCase):
    """Test cases for get_holdings method."""
    
    def test_get_holdings_empty(self):
        """Test getting holdings with empty portfolio."""
        account = Account("user123", 1000.0)
        holdings = account.get_holdings()
        self.assertEqual(holdings, {})
    
    def test_get_holdings_with_shares(self):
        """Test getting holdings with shares."""
        account = Account("user123", 10000.0)
        account.buy_shares("AAPL", 10)
        account.buy_shares("TSLA", 5)
        holdings = account.get_holdings()
        self.assertEqual(holdings, {"AAPL": 10, "TSLA": 5})
    
    def test_get_holdings_returns_copy(self):
        """Test that get_holdings returns a copy, not reference."""
        account = Account("user123", 10000.0)
        account.buy_shares("AAPL", 10)
        holdings = account.get_holdings()
        holdings["AAPL"] = 999
        self.assertEqual(account.portfolio["AAPL"], 10)


class TestListTransactions(unittest.TestCase):
    """Test cases for list_transactions method."""
    
    def test_list_transactions_initial(self):
        """Test that initial deposit is recorded."""
        account = Account("user123", 1000.0)
        transactions = account.list_transactions()
        self.assertEqual(len(transactions), 1)
        self.assertEqual(transactions[0]["type"], "deposit")
    
    def test_list_transactions_multiple(self):
        """Test multiple transactions are recorded."""
        account = Account("user123", 10000.0)
        account.deposit_funds(500.0)
        account.buy_shares("AAPL", 5)
        account.sell_shares("AAPL", 2)
        account.withdraw_funds(100.0)
        transactions = account.list_transactions()
        self.assertEqual(len(transactions), 5)
    
    def test_list_transactions_returns_copy(self):
        """Test that list_transactions returns a copy."""
        account = Account("user123", 1000.0)
        transactions = account.list_transactions()
        transactions.append({"type": "fake"})
        self.assertEqual(len(account.transactions), 1)


class TestIntegrationScenarios(unittest.TestCase):
    """Integration test cases for complex scenarios."""
    
    def test_complete_trading_scenario(self):
        """Test a complete trading scenario."""
        account = Account("trader1", 10000.0)
        
        account.buy_shares("AAPL", 10)
        account.buy_shares("TSLA", 5)
        account.sell_shares("AAPL", 3)
        account.deposit_funds(2000.0)
        account.withdraw_funds(500.0)
        
        self.assertEqual(account.portfolio["AAPL"], 7)
        self.assertEqual(account.portfolio["TSLA"], 5)
        
        expected_cash = 10000.0 - 1500.0 - 1000.0 + 450.0 + 2000.0 - 500.0
        self.assertEqual(account.cash_balance, expected_cash)
        
        self.assertEqual(len(account.transactions), 6)
    
    def test_portfolio_value_calculation_comprehensive(self):
        """Test comprehensive portfolio value calculation."""
        account = Account("trader2", 5000.0)
        
        account.buy_shares("AAPL", 5)
        account.buy_shares("GOOGL", 10)
        
        portfolio_value = account.get_portfolio_value()
        
        expected_shares_value = (5 * 150.0) + (10 * 100.0)
        expected_cash = 5000.0 - (5 * 150.0) - (10 * 100.0)
        expected_total = expected_cash + expected_shares_value
        
        self.assertEqual(portfolio_value, expected_total)
        self.assertEqual(account.get_profit_loss(), 0.0)
    
    def test_edge_case_zero_quantity_buy(self):
        """Test buying zero shares."""
        account = Account("user123", 1000.0)
        result = account.buy_shares("AAPL", 0)
        self.assertTrue(result)
        self.assertNotIn("AAPL", account.portfolio)
    
    def test_edge_case_sell_zero_shares(self):
        """Test selling zero shares."""
        account = Account("user123", 10000.0)
        account.buy_shares("AAPL", 10)
        result = account.sell_shares("AAPL",