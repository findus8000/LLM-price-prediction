import json
from re import I
import requests

def main():
    data = initData("./data/halfRawData.json")
    generatedText = generateText(data, 10, 0)
    initDataLength = len(json.loads(sealData(data + "]")))
    genTxtLength = len(json.loads(sealData(generatedText)))
    rawData = initData("./data/rawData.json")
    upperBound = 0
    if (genTxtLength > initDataLength*2):
        upperBound = initDataLength*2
    else:
        upperBound = genTxtLength
    cutGenTxt = cutData(json.loads(sealData(generatedText)), initDataLength, upperBound)
    cutRawData = cutData(json.loads(sealData(rawData + "]")), initDataLength, upperBound)
    writeData("./data/rawCompData.json", cutRawData)
    writeData("./data/generatedData.json", cutGenTxt)
    print("[" + str(len(cutGenTxt)) + " candles generated]")
    
def initData(filePath):
    f = open(filePath, "r")
    inputData = str(json.loads(f.read()))
    f.close()
    for i in range(1, len(inputData)):
        if (inputData[i] == ',' and inputData[i - 1] == '}'):
            inputData = inputData[:i+1] + '\n' + inputData[i+1:]
    return (inputData.rstrip(inputData[-1]))    

def sealData(string):
    string = string.replace("\'", "\"")
    string = string.replace("\n", "") 
    lastIndex = len(string) - 1
    for i in range(0, len(string)):
        if(string[lastIndex - i] == ']' and string[lastIndex - i - 1] == '}'):
            string = string[:len(string) - i]
            break
        if (string[lastIndex - i] == ',' and string[lastIndex - i - 1] == '}'):
            string = (string[:lastIndex - i] + ']')
            break    
    return string

def checkForEnding(string):
    lastIndex = len(string) - 1
    for i in range(0, len(string)):
        if(string[lastIndex - i] == ']' and string[lastIndex - i - 1] == '}'):
            string = string[:lastIndex - i]
            return string
    return string
    
def checkForChar(string):
    lastIndex = len(string) - 1
    for item in string:
        if (item.isalpha() and item != 'O' and item != 'H' and item != 'L' and item != 'C'):
            for i in range(0, len(string)):
                if (string[lastIndex - i] == 'C' and string[lastIndex - 1 - i] == 'L' 
                    and string[lastIndex - 2 - i] == 'H' and string[lastIndex - 3 - i] == 'O'):
                    return string[:lastIndex - i]
    return string
            
def checkForUnsealed(string):
    lastIndex = len(string) - 1
    for i in range(0, len(string)):
        if (i != lastIndex and string[lastIndex - i] != '}' and string[lastIndex - i - 1] == ']'):
            string = string[:lastIndex - i - 1] + "}" + string[lastIndex - i - 1:]
    return string
             
            
def writeData(filePath, data):
    f = open(filePath, "w")
    f.write(json.dumps(data))
    f.close()
    
def cutData(arr, int1, int2):
    return arr[int1:int2]
    
def query(payload):
        headers = {"Authorization": f"Bearer {'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'}"}
        API_URL = "https://api-inference.huggingface.co/models/bigscience/bloom"
        data = json.dumps(payload)
        response = requests.request("POST", API_URL, headers=headers, data=data)
        return json.loads(response.content.decode("utf-8"))
            
def generateText(inputData, nrOfCalls, index):
    data = query(
        {
            "inputs": inputData,
            "parameters": {"do_sample": True,
                           "repetition_penalty": None,
                           "temperature": 0.8,
                           "num_return_sequences":None,
                           "top_k": None,
                           "top_p": None}
        }
    )
    index += 1
    print(str((index/nrOfCalls) * 100) + '%')
    if index == nrOfCalls:
        print(data[0]["generated_text"])
        return checkForUnsealed(checkForChar(checkForEnding(data[0]["generated_text"])))
    else:
        print(data[0]["generated_text"])
        return generateText(checkForUnsealed(checkForChar(checkForEnding(data[0]["generated_text"]))), nrOfCalls, index)

#main()