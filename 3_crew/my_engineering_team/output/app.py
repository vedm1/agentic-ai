import gradio as gr
from accounts import Account

# Initialize a single user account
account = Account("user1", 0.0)

def create_account(initial_deposit):
    global account
    account = Account("user1", float(initial_deposit))
    return f"Account created with initial deposit: ${initial_deposit}"

def deposit(amount):
    account.deposit_funds(float(amount))
    return f"Deposited ${amount}. Current cash balance: ${account.cash_balance:.2f}"

def withdraw(amount):
    success = account.withdraw_funds(float(amount))
    if success:
        return f"Withdrew ${amount}. Current cash balance: ${account.cash_balance:.2f}"
    else:
        return f"Withdrawal failed. Insufficient funds. Current cash balance: ${account.cash_balance:.2f}"

def buy(symbol, quantity):
    success = account.buy_shares(symbol, int(quantity))
    if success:
        return f"Bought {quantity} shares of {symbol}. Current cash balance: ${account.cash_balance:.2f}"
    else:
        return f"Purchase failed. Insufficient funds. Current cash balance: ${account.cash_balance:.2f}"

def sell(symbol, quantity):
    success = account.sell_shares(symbol, int(quantity))
    if success:
        return f"Sold {quantity} shares of {symbol}. Current cash balance: ${account.cash_balance:.2f}"
    else:
        return f"Sale failed. Insufficient shares. You own {account.portfolio.get(symbol, 0)} shares of {symbol}."

def show_holdings():
    holdings = account.get_holdings()
    if not holdings:
        return "No shares currently held."
    output = "Current Holdings:\n"
    for symbol, quantity in holdings.items():
        output += f"{symbol}: {quantity} shares\n"
    output += f"\nCash Balance: ${account.cash_balance:.2f}"
    return output

def show_portfolio_value():
    total_value = account.get_portfolio_value()
    return f"Total Portfolio Value: ${total_value:.2f}\nCash Balance: ${account.cash_balance:.2f}"

def show_profit_loss():
    profit_loss = account.get_profit_loss()
    if profit_loss >= 0:
        return f"Profit: ${profit_loss:.2f}"
    else:
        return f"Loss: ${abs(profit_loss):.2f}"

def show_transactions():
    transactions = account.list_transactions()
    if not transactions:
        return "No transactions yet."
    output = "Transaction History:\n\n"
    for i, trans in enumerate(transactions, 1):
        output += f"{i}. {trans['description']}\n"
    return output

# Create Gradio interface
with gr.Blocks(title="Trading Simulation Platform") as demo:
    gr.Markdown("# Trading Simulation Platform")
    gr.Markdown("A simple account management system for trading simulation")
    
    with gr.Tab("Account Setup"):
        gr.Markdown("## Create Account")
        initial_deposit_input = gr.Number(label="Initial Deposit ($)", value=10000)
        create_btn = gr.Button("Create Account")
        create_output = gr.Textbox(label="Result")
        create_btn.click(create_account, inputs=[initial_deposit_input], outputs=[create_output])
    
    with gr.Tab("Manage Funds"):
        gr.Markdown("## Deposit Funds")
        deposit_input = gr.Number(label="Amount to Deposit ($)")
        deposit_btn = gr.Button("Deposit")
        deposit_output = gr.Textbox(label="Result")
        deposit_btn.click(deposit, inputs=[deposit_input], outputs=[deposit_output])
        
        gr.Markdown("## Withdraw Funds")
        withdraw_input = gr.Number(label="Amount to Withdraw ($)")
        withdraw_btn = gr.Button("Withdraw")
        withdraw_output = gr.Textbox(label="Result")
        withdraw_btn.click(withdraw, inputs=[withdraw_input], outputs=[withdraw_output])
    
    with gr.Tab("Trade Shares"):
        gr.Markdown("## Buy Shares")
        gr.Markdown("Available symbols: AAPL ($150), TSLA ($200), GOOGL ($100)")
        buy_symbol_input = gr.Textbox(label="Symbol", placeholder="AAPL")
        buy_quantity_input = gr.Number(label="Quantity", value=1)
        buy_btn = gr.Button("Buy")
        buy_output = gr.Textbox(label="Result")
        buy_btn.click(buy, inputs=[buy_symbol_input, buy_quantity_input], outputs=[buy_output])
        
        gr.Markdown("## Sell Shares")
        sell_symbol_input = gr.Textbox(label="Symbol", placeholder="AAPL")
        sell_quantity_input = gr.Number(label="Quantity", value=1)
        sell_btn = gr.Button("Sell")
        sell_output = gr.Textbox(label="Result")
        sell_btn.click(sell, inputs=[sell_symbol_input, sell_quantity_input], outputs=[sell_output])
    
    with gr.Tab("View Account"):
        gr.Markdown("## Account Information")
        
        holdings_btn = gr.Button("Show Holdings")
        holdings_output = gr.Textbox(label="Holdings", lines=10)
        holdings_btn.click(show_holdings, inputs=[], outputs=[holdings_output])
        
        portfolio_btn = gr.Button("Show Portfolio Value")
        portfolio_output = gr.Textbox(label="Portfolio Value")
        portfolio_btn.click(show_portfolio_value, inputs=[], outputs=[portfolio_output])
        
        profit_loss_btn = gr.Button("Show Profit/Loss")
        profit_loss_output = gr.Textbox(label="Profit/Loss")
        profit_loss_btn.click(show_profit_loss, inputs=[], outputs=[profit_loss_output])
        
        transactions_btn = gr.Button("Show Transaction History")
        transactions_output = gr.Textbox(label="Transactions", lines=15)
        transactions_btn.click(show_transactions, inputs=[], outputs=[transactions_output])

if __name__ == "__main__":
    demo.launch()