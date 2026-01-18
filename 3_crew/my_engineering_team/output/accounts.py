def get_share_price(symbol: str) -> float:
    """Returns the current price of a share.
    
    Args:
        symbol: The ticker symbol of the share.
        
    Returns:
        float: The price of the share.
    """
    prices = {
        "AAPL": 150.0,
        "TSLA": 200.0,
        "GOOGL": 100.0
    }
    return prices.get(symbol, 0.0)


class Account:
    """Manages user accounts for a trading simulation platform."""
    
    def __init__(self, user_id: str, initial_deposit: float) -> None:
        """Initializes a new user account.
        
        Args:
            user_id: A unique identifier for the user.
            initial_deposit: The starting funds in the account.
        """
        self.user_id = user_id
        self.initial_deposit = initial_deposit
        self.cash_balance = initial_deposit
        self.portfolio = {}  # {symbol: quantity}
        self.transactions = []
        
        # Record initial deposit as a transaction
        self.transactions.append({
            "type": "deposit",
            "amount": initial_deposit,
            "description": "Initial deposit"
        })
    
    def deposit_funds(self, amount: float) -> None:
        """Allows the user to deposit funds into the account.
        
        Args:
            amount: The amount of money to deposit.
        """
        self.cash_balance += amount
        self.transactions.append({
            "type": "deposit",
            "amount": amount,
            "description": f"Deposited ${amount:.2f}"
        })
    
    def withdraw_funds(self, amount: float) -> bool:
        """Attempts to withdraw funds from the account.
        
        Args:
            amount: The amount of money to withdraw.
            
        Returns:
            bool: True if the withdrawal is successful, False if funds are insufficient.
        """
        if self.cash_balance >= amount:
            self.cash_balance -= amount
            self.transactions.append({
                "type": "withdrawal",
                "amount": amount,
                "description": f"Withdrew ${amount:.2f}"
            })
            return True
        return False
    
    def buy_shares(self, symbol: str, quantity: int) -> bool:
        """Records a share purchase.
        
        Args:
            symbol: The ticker symbol of the share to purchase.
            quantity: Number of shares to buy.
            
        Returns:
            bool: True if the purchase is successful, False if funds are insufficient.
        """
        share_price = get_share_price(symbol)
        total_cost = share_price * quantity
        
        if self.cash_balance >= total_cost:
            self.cash_balance -= total_cost
            
            # Update portfolio
            if symbol in self.portfolio:
                self.portfolio[symbol] += quantity
            else:
                self.portfolio[symbol] = quantity
            
            # Record transaction
            self.transactions.append({
                "type": "buy",
                "symbol": symbol,
                "quantity": quantity,
                "price": share_price,
                "total_cost": total_cost,
                "description": f"Bought {quantity} shares of {symbol} at ${share_price:.2f} each"
            })
            return True
        return False
    
    def sell_shares(self, symbol: str, quantity: int) -> bool:
        """Records a share sale.
        
        Args:
            symbol: The ticker symbol of the share to sell.
            quantity: Number of shares to sell.
            
        Returns:
            bool: True if the sale is successful, False if insufficient shares held.
        """
        # Check if user has enough shares
        if symbol not in self.portfolio or self.portfolio[symbol] < quantity:
            return False
        
        share_price = get_share_price(symbol)
        total_revenue = share_price * quantity
        
        # Update cash balance
        self.cash_balance += total_revenue
        
        # Update portfolio
        self.portfolio[symbol] -= quantity
        if self.portfolio[symbol] == 0:
            del self.portfolio[symbol]
        
        # Record transaction
        self.transactions.append({
            "type": "sell",
            "symbol": symbol,
            "quantity": quantity,
            "price": share_price,
            "total_revenue": total_revenue,
            "description": f"Sold {quantity} shares of {symbol} at ${share_price:.2f} each"
        })
        return True
    
    def get_portfolio_value(self) -> float:
        """Calculates the total current value of the user's portfolio.
        
        Returns:
            float: The total value of the portfolio based on current share prices.
        """
        portfolio_value = 0.0
        for symbol, quantity in self.portfolio.items():
            share_price = get_share_price(symbol)
            portfolio_value += share_price * quantity
        
        # Total value includes cash balance plus value of shares
        return self.cash_balance + portfolio_value
    
    def get_profit_loss(self) -> float:
        """Calculates the profit or loss of the user from their initial deposit.
        
        Returns:
            float: The net profit or loss.
        """
        current_total_value = self.get_portfolio_value()
        return current_total_value - self.initial_deposit
    
    def get_holdings(self) -> dict:
        """Reports the current share holdings of the user.
        
        Returns:
            dict: A dictionary with share symbols as keys and quantities as values.
        """
        return self.portfolio.copy()
    
    def list_transactions(self) -> list:
        """Lists all transactions in the user's account history.
        
        Returns:
            list: A list of transactions detailing deposits, withdrawals, and share trades.
        """
        return self.transactions.copy()