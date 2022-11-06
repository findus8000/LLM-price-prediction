from binance import Client
import json

def main(ticker, timeframe, interval):
    cleanData = getPriceData(ticker, timeframe, interval)
    writeFile("./data/rawData.json", cleanData)
    
def getPriceData(ticker, timeframe, interval):
    client = Client('', '')
    cleanData = []

    klines = client.get_historical_klines(ticker, timeframe, interval)

    for candle in klines:
        cleanData.append({"OHLC":
                                [round(float(candle[1]), 2),
                                round(float(candle[2]), 2),
                                round(float(candle[3]), 2),
                                round(float(candle[4]), 2)]})
    return cleanData
    
def writeFile(filePath, data):
    f = open(filePath, "w")
    f.write(json.dumps(data))
    f.close()
    print("[price data saved]")
