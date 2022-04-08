import sys
import ccxt
import pandas as pd
import numpy as np
import ta
from datetime import datetime
import json
f = open('./secret.json',)
secret = json.load(f)
f.close()

now = datetime.now()
current_time = now.strftime("%d/%m/%Y %H:%M:%S")
print("alligator -> Execution Time :", current_time)

strategy_name = "alligator"+"_"+sys.argv[1]+"_"+sys.argv[2]
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
pair_symbol = sys.argv[1]+"/"+sys.argv[2]
symbol_coin = sys.argv[1]
symbol_usd = sys.argv[2]
timeframe = "1h" # En réalisté cela sera 2h mais on va quand même lancer toutes les heures


limit = 1000
min_size = float(markets[pair_symbol]["info"]["minProvideSize"])

df = pd.DataFrame(data=session.fetch_ohlcv(
    pair_symbol, timeframe, None, limit=limit))
df = df.rename(
    columns={0: 'timestamp', 1: 'open', 2: 'high', 3: 'low', 4: 'close', 5: 'volume'})
df = df.set_index(df['timestamp'])
df.index = pd.to_datetime(df.index, unit='ms')
del df['timestamp']

if df.index.hour[-1] % 2 == 0: 

    if df.index.hour[0] % 2 == 1: 
        df = df.iloc[1:]
        
    df = df[::2]
    # Definitions des indiicateurs
    df['ema1'] = ta.trend.ema_indicator(close = df['close'], window = 5) # Moyenne exponentielle 1
    df['ema2'] = ta.trend.ema_indicator(close = df['close'], window = 15) # Moyenne exponentielle 2
    df['ema3'] = ta.trend.ema_indicator(close = df['close'], window = 50) # Moyenne exponentielle 3
    df['ema4'] = ta.trend.ema_indicator(close = df['close'], window = 100) # Moyenne exponentielle 4
    df['ema5'] = ta.trend.ema_indicator(close = df['close'], window = 200) # Moyenne exponentielle 5
    df['stoch_rsi'] = ta.momentum.stochrsi(close = df['close'], window = 14) # Stochastic RSI non moyenné (K=1 sur Trading View)

    # Condition pour rentrer en achat (row = période actuelle et previous_row = période précédente)
    def buy_condition(row, previous_row = None):
        if row['ema1'] > row['ema2'] and row['ema2'] > row['ema3'] and row['ema3'] > row['ema4'] and row['ema4'] > row['ema5'] and row['stoch_rsi'] < 0.8:
            return True
        else:
            return False

    # Condition pour vendre (row = période actuelle et previous_row = période précédente)
    def sell_condition(row, previous_row = None):
        if row['ema2'] > row['ema1'] and row['stoch_rsi'] > 0.2:
            return True
        else:
            return False


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

    if buy_condition(row) and balance_usd > min_size*row["close"]:
        amount_to_buy = balance_usd / row["close"] 
        session.createOrder(
                    pair_symbol, 
                    'market', 
                    "buy", 
                    session.amount_to_precision(pair_symbol, amount_to_buy),
                    None
                )
        print("Achat de " + str(session.amount_to_precision(pair_symbol, amount_to_buy)) + " " + symbol_coin + " au prix d'environ " +  str(row["close"]) + " $")
    elif sell_condition(row) and  balance_coin > min_size:
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
