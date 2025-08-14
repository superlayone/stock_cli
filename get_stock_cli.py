import time
from longport.openapi import Config, QuoteContext

# ANSI escape sequences for colors
COLORS = {
    'red': '\033[31m',
    'green': '\033[32m',
    'yellow': '\033[33m',
    'blue': '\033[34m',
    'magenta': '\033[35m',
    'cyan': '\033[36m',
    'white': '\033[37m',
    'reset': '\033[0m'
}

# Load configuration from environment variables
config = Config.from_env()

# Create a context for quote APIs
ctx = QuoteContext(config)

def colorize_price(price, prev_close):
    """Colorize price based on comparison with previous close"""
    if price == 'N/A':
        return price
    try:
        price_float = float(price)
        prev_close_float = float(prev_close)
        if price_float > prev_close_float:
            return f"{COLORS['green']}{price}{COLORS['reset']}"
        elif price_float < prev_close_float:
            return f"{COLORS['red']}{price}{COLORS['reset']}"
        else:
            return price
    except ValueError:
        return price

def colorize_percentage_change(current, prev_close):
    """Colorize percentage change based on comparison with previous close"""
    if current == 'N/A' or prev_close == 'N/A':
        return 'N/A'
    try:
        current_float = float(current)
        prev_close_float = float(prev_close)
        if prev_close_float == 0:
            return 'N/A'
        
        # Calculate percentage change
        percentage_change = ((current_float - prev_close_float) / prev_close_float) * 100
        
        # Format with 2 decimal places and % sign
        formatted_change = f"{percentage_change:+.2f}%"
        
        # Apply color based on change direction
        if percentage_change > 0:
            return f"{COLORS['green']}{formatted_change}{COLORS['reset']}"
        elif percentage_change < 0:
            return f"{COLORS['red']}{formatted_change}{COLORS['reset']}"
        else:
            return formatted_change
    except ValueError:
        return 'N/A'

def pad_colored_text(text, width):
    """Pad colored text to align properly in table"""
    # Calculate visible length (excluding ANSI escape sequences)
    visible_len = len(text)
    if '\033[' in text:
        # Remove ANSI escape sequences for length calculation
        import re
        ansi_escape = re.compile(r'\033\[[;\d]*m')
        visible_text = ansi_escape.sub('', text)
        visible_len = len(visible_text)
    
    # Add padding
    padding = width - visible_len
    if padding > 0:
        return text + ' ' * padding
    return text

def get_quote_table():
    # Get basic information of securities
    resp = ctx.quote(["BLSH.US","BMNR.US","CRWV.US","DJT.US"])
    
    # Print table header with column separators
    header = f"| {'Symbol':<10} | {'Pre-Market':<12} | {'Current':<12} | {'Post-Market':<12} | {'Change %':<10} |"
    separator = "+" + "-" * 12 + "+" + "-" * 14 + "+" + "-" * 14 + "+" + "-" * 14 + "+" + "-" * 12 + "+"
    print(separator)
    print(header)
    print(separator)
    
    # Print quote data
    for quote in resp:
        symbol = quote.symbol
        prev_close = quote.prev_close
        pre_market = getattr(quote.pre_market_quote, 'last_done', 'N/A') if quote.pre_market_quote else 'N/A'
        current = quote.last_done
        post_market = getattr(quote.post_market_quote, 'last_done', 'N/A') if quote.post_market_quote else 'N/A'
        
        # Colorize prices
        pre_market_colored = colorize_price(pre_market, prev_close)
        current_colored = colorize_price(current, prev_close)
        post_market_colored = colorize_price(post_market, prev_close)
        
        # Colorize percentage change
        change_percent_colored = colorize_percentage_change(current, prev_close)
        
        # Pad colored text for proper alignment
        symbol_padded = f"{symbol:<10}"
        pre_market_padded = pad_colored_text(pre_market_colored, 12)
        current_padded = pad_colored_text(current_colored, 12)
        post_market_padded = pad_colored_text(post_market_colored, 12)
        change_percent_padded = pad_colored_text(change_percent_colored, 10)
        
        # Print row with column separators
        row = f"| {symbol_padded} | {pre_market_padded} | {current_padded} | {post_market_padded} | {change_percent_padded} |"
        print(row)
    print(separator)

# Refresh every 10 seconds
while True:
    get_quote_table()
    time.sleep(10)