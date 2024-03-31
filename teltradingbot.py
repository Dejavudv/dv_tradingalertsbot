import ccxt
import pandas_ta as ta
import pandas as pd
import matplotlib.pyplot as plt
from telegram import Bot
import asyncio

# Use TkAgg backend for opening plots in a separate window on Windows
plt.switch_backend('TkAgg')

# Initialize the CCXT exchange object
exchange = ccxt.binance()

# Set the symbol (BTC/USDT)
symbol = 'BTC/USDT'

# Define the timeframe (4h)
timeframe = '4h'

# Define the number of data points to fetch
num_points = 5000  # Fetch 100 data points (approximately 400 hours of data)

# Initialize an empty DataFrame to store the data
df = pd.DataFrame()

# Initialize Telegram bot with your bot token
bot = Bot(token='6431358009:AAELe1V2D2th7aTq-jgGnuw3HjHt63VO-V0')

# Define an asynchronous function to fetch OHLCV data
async def fetch_ohlcv():
    # Fetch OHLCV data
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=num_points)

    # Convert the data into a pandas DataFrame
    temp_df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    temp_df['timestamp'] = pd.to_datetime(temp_df['timestamp'], unit='ms')
    temp_df.set_index('timestamp', inplace=True)

    return temp_df

# Define the main function to wrap the execution of asynchronous tasks
# Define the main function to wrap the execution of asynchronous tasks
async def main():
    # Fetch OHLCV data
    df = await fetch_ohlcv()

    # Calculate the 50-period Exponential Moving Average (EMA)
    df['ema_50'] = ta.ema(df['close'], length=50)
    df['ema_200'] = ta.ema(df['close'], length=200)
    # Define an asynchronous function to send messages
    async def send_message(chat_id, message):
        await bot.send_message(chat_id=chat_id, text=message)

    # Initialize lists to store red dot positions and green rectangle positions
    red_dots = []
    green_rectangles = []

    # Iterate through the DataFrame to find points where the closing price equals the 50 EMA and the 50 EMA is above the 200 EMA
    for index, row in df.iterrows():
        close_price = row['close']
        ema_50 = row['ema_50']
        ema_200 = row['ema_200']

        # Check if ema_50 and ema_200 are not NaN
        if not pd.isna(ema_50) and not pd.isna(ema_200):
            # Check if the first three digits of the close price and EMA 50 are equal
            if str(close_price)[:1] == str(int(ema_50))[:1] and ema_50 > ema_200:
                red_dots.append(index)
                # Send red dot alert message
                await send_message('1706992952', f"RED DOT ALERT!\n\nCurrent Price: {close_price}\n50 EMA: {ema_50}\n200 EMA: {ema_200}\nBuy alert above")

            # Check if the price is 2 percent below the 50 EMA
            if close_price < 0.98 * ema_50 and ema_50 < ema_200:
                green_rectangles.append(index)
                # Send green rectangle alert message
                await send_message('1706992952', f"GREEN RECTANGLE ALERT!\n\nCurrent Price: {close_price}\n50 EMA: {ema_50}\n200 EMA: {ema_200}\nBuy alert below")

    # Plotting
    # Plotting
    plt.figure(figsize=(12, 6))
    plt.plot(df.index, df['close'], label='Close Price', color='blue')
    plt.plot(df.index, df['ema_50'], label='50-period EMA', color='orange')
    plt.plot(df.index, df['ema_200'], label='200-period EMA', color='green')

    # Plot red dots
    plt.scatter(red_dots, df.loc[red_dots]['close'], color='red', label='Price equals 50 EMA above 200 EMA')

    # Plot green rectangles
    plt.scatter(green_rectangles, df.loc[green_rectangles]['close'], color='green', label='Price equals 50 EMA above 200 EMA')

    # Adding title and labels
    plt.title('BTC/USDT Price with 50-period and 200-period EMAs')
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.legend()

    # Show plot in a separate window
    plt.show()

# Run the main function within the asyncio event loop
asyncio.run(main())
