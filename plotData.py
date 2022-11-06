import pandas as pd
import json
import matplotlib.pyplot as plt

def main():
    rawCompData = readData("./data/rawCompData.json")
    generatedData = readData("./data/generatedData.json")
    summarizeData(rawCompData, generatedData)
    plotCandleChart(initPlotData(generatedData), 'Bloom Generated')
    plotCandleChart(initPlotData(rawCompData), 'Real Data')
    plt.show()
    
def readData(filePath):
    f = open(filePath, "r")
    priceData = json.loads(f.read())
    f.close()
    return priceData
    

def initPlotData(priceData):
    opeN = []
    high = []
    low = []
    close = []
    index = []
    
    i = 0
    for item in priceData:
        opeN.append(abs(item["OHLC"][0]))
        high.append(abs(item["OHLC"][1]))
        low.append(abs(item["OHLC"][2]))
        close.append(abs(item["OHLC"][3]))
        index.append(i)
        i += 1

    dataFrame = pd.DataFrame({'open': opeN,
                                'close': close,
                                'high': high,
                                'low': low},
                                index=index)
    return dataFrame

def norm(value, max, min):
    normValue = round((value - min) / (max - min), 2) 
    return normValue
    

def summarizeData(rawCompData, generatedData):
    opeN = [[],[]]
    high = [[],[]]
    low = [[],[]]
    close = [[],[]]
    
    for i in range(0, len(rawCompData)):
        opeN[0].append(abs(rawCompData[i]["OHLC"][0]))
        opeN[1].append(abs(generatedData[i]["OHLC"][0]))
        high[0].append(abs(rawCompData[i]["OHLC"][1]))
        high[1].append(abs(generatedData[i]["OHLC"][1]))
        low[0].append(abs(rawCompData[i]["OHLC"][2]))
        low[1].append(abs(generatedData[i]["OHLC"][2]))
        close[0].append(abs(rawCompData[i]["OHLC"][3]))
        close[1].append(abs(generatedData[i]["OHLC"][3]))
 
    openMax = max(opeN[0] + (opeN[1]))
    openMin = min(opeN[0] + (opeN[1]))
    highMax = max(high[0] + (high[1]))
    highMin = min(high[0] + (high[1]))
    lowMax = max(low[0] + (low[1]))
    lowMin = min(low[0] + (low[1]))
    closeMax = max(close[0] + (close[1]))
    closeMin = min(close[0] + (close[1]))
    
    normRawData = []
    normGenData = []
    for i in range(0, len(rawCompData)):
        normRawData.append({"x": i, 
                               "OHLC": 
                                [norm(rawCompData[i]["OHLC"][0], openMax, openMin),
                                 norm(rawCompData[i]["OHLC"][1], highMax, highMin),
                                 norm(rawCompData[i]["OHLC"][2], lowMax, lowMin),
                                 norm(rawCompData[i]["OHLC"][3], closeMax, closeMin)]})
        normGenData.append({"x": i,
                                "OHLC": 
                                [norm(generatedData[i]["OHLC"][0], openMax, openMin),
                                 norm(generatedData[i]["OHLC"][1], highMax, highMin),
                                 norm(generatedData[i]["OHLC"][2], lowMax, lowMin),
                                 norm(generatedData[i]["OHLC"][3], closeMax, closeMin)]})
        
    normSum = 0
    for i in range(0, len(normRawData)):
        normSum += abs(normRawData[i]["OHLC"][0] - normGenData[i]["OHLC"][0])
        normSum += abs(normRawData[i]["OHLC"][1] - normGenData[i]["OHLC"][1])
        normSum += abs(normRawData[i]["OHLC"][2] - normGenData[i]["OHLC"][2])
        normSum += abs(normRawData[i]["OHLC"][3] - normGenData[i]["OHLC"][3])
        
    score = (1 - (normSum / (len(normRawData) * 4)))/1 * 100
    
    entryIndex = ""
    exitIndex = ""
    tradeResult = ""
    tradeResultPrc = ""
    
    for i in range(0, len(generatedData)):
        if (min(opeN[1]) == generatedData[i]["OHLC"][0]):
            entryIndex = i
            for j in range(i, len(generatedData)):
                if (max((close[1])[i:]) == generatedData[j]["OHLC"][3]):
                    if (generatedData[i]["OHLC"][0] < generatedData[j]["OHLC"][3]):
                        exitIndex = j
                        tradeResult = round(rawCompData[exitIndex]["OHLC"][3] - rawCompData[entryIndex]["OHLC"][0], 2)
                        tradeResultPrc = round((tradeResult / rawCompData[entryIndex]["OHLC"][0]) * 100, 3)
                    else:
                        entryIndex = "no profitable trade found"
                        exitIndex = "no profitable trade found"
                        tradeResultPrc = "no profitable trade found"
                            
    
    print("Entry index: " + str(entryIndex))
    print("Exit index: " + str(exitIndex))
    print("PNL: " + str(tradeResultPrc) + "%")
    print("Datasets match: " + str(round(score, 1)) + "%")

def plotCandleChart(dataFrame, title):
    plt.figure()
    
    up = dataFrame[dataFrame.close >= dataFrame.open]
    down = dataFrame[dataFrame.close < dataFrame.open]

    col1 = 'green'
    col2 = 'red'

    width = .8
    width2 = .05
    
    plt.bar(up.index, up.close-up.open, width, bottom=up.open, color=col1)
    plt.bar(up.index, up.high-up.close, width2, bottom=up.close, color=col1)
    plt.bar(up.index, up.low-up.open, width2, bottom=up.open, color=col1)
    
    plt.bar(down.index, down.close-down.open, width, bottom=down.open, color=col2)
    plt.bar(down.index, down.high-down.open, width2, bottom=down.open, color=col2)
    plt.bar(down.index, down.low-down.close, width2, bottom=down.close, color=col2)
    
    plt.title(title)
    plt.xticks(rotation=30, ha='right')
