import getBinanceData
import generateData
import plotData
from binance import Client

def main():
    getBinanceData.main("ETHUSDT", Client.KLINE_INTERVAL_4HOUR, "25 days ago UTC")
    generateData.main(30, 20, 0.8)
    plotData.main()
    
main()
