from binance import Client, ThreadedWebsocketManager, ThreadedDepthCacheManager
import json

def main():
    cleanData = getPriceData("ETHUSDT", "1 day ago UTC")
    writeFile("./data/rawData.json", cleanData)
    writeFile("./data/halfRawData.json", cleanData[:int(len(cleanData)/2)])
    
def getPriceData(ticker, interval):
    client = Client('', '')
    cleanData = []

    klines = client.get_historical_klines(ticker, Client.KLINE_INTERVAL_1HOUR, interval)

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
    print("[data saved]")
    
#main()