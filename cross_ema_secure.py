import ccxt
import pandas as pd
import numpy as np
import ta
from datetime import datetime
import json
f = open('../secret.json',)
secret = json.load(f)
f.close()

now = datetime.now()
current_time = now.strftime("%d/%m/%Y %H:%M:%S")
print("cross_ema_secure -> Execution Time :", current_time)

strategy_name = "cross_ema_secure"
ftx_auth_object = {
    "apiKey": secret[strategy_name]["public_key"],
    "secret": secret[strategy_name]["private_key"],
    'headers': {
        'FTX-SUBACCOUNT': secret[strategy_name]["subaccount_name"]
    }
}

session = ccxt.ftx(ftx_auth_object)
markets = session.load_markets()


# Vous pouvez changer la paire ou la timeframe ici
pair_symbol = "BTC/USD"
symbol_coin = "BTC"
symbol_usd = "USD"
timeframe = "1h"


limit = 1000
min_size = markets[pair_symbol]["limits"]["amount"]["min"]

df = pd.DataFrame(data=session.fetch_ohlcv(
    pair_symbol, timeframe, None, limit=limit))
df = df.rename(
    columns={0: 'timestamp', 1: 'open', 2: 'high', 3: 'low', 4: 'close', 5: 'volume'})
df = df.set_index(df['timestamp'])
df.index = pd.to_datetime(df.index, unit='ms')
del df['timestamp']

df['ema1'] = ta.trend.ema_indicator(close = df['close'], window = 25) # Moyenne exponentiel courte
df['ema2'] = ta.trend.ema_indicator(close = df['close'], window = 45) # Moyenne exponentiel moyenne
df['sma_long'] = ta.trend.sma_indicator(close = df['close'], window = 600) # Moyenne simple longue
df['stoch_rsi'] = ta.momentum.stochrsi(close = df['close'], window = 14) # Stochastic RSI non moyenné (K=1 sur Trading View)

def get_balance(symbol):
    balance = 0
    try:
        balance = pd.DataFrame(session.fetchBalance())['total'][symbol]
    except:
        balance = 0
    return balance

balance_coin = get_balance(symbol_coin)
balance_usd = get_balance(symbol_usd)
row = df.iloc[-2]

if row['ema1'] > row['ema2'] and row['stoch_rsi'] < 0.8 and row['close'] > row['sma_long'] and balance_usd > min_size*row["close"]:
    amount_to_buy = balance_usd / row["close"] 
    session.createOrder(
                pair_symbol, 
                'market', 
                "buy", 
                session.amount_to_precision(pair_symbol, amount_to_buy),
                None
            )
    print("Achat de " + str(session.amount_to_precision(pair_symbol, amount_to_buy)) + " " + symbol_coin + " au prix d'environ " +  str(row["close"]) + " $")
elif row['ema2'] > row['ema1'] and row['stoch_rsi'] > 0.2 and  balance_coin > min_size:
    amount_to_sell = balance_coin
    session.createOrder(
                pair_symbol, 
                'market', 
                "sell", 
                session.amount_to_precision(pair_symbol, amount_to_sell),
                None
            )
    print("Vente de " + str(session.amount_to_precision(pair_symbol, amount_to_sell)) + " " + symbol_coin + " au prix d'environ " +  str(row["close"]) + " $")
else:
    print("Nono le robot ne voit pas d'opportunité de trade actuellement. Il suffit d'attendre ;)")
