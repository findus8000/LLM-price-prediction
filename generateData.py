import json
import requests

def main(modelInputSize, nrCandelsToGen, temprature):
    data = initData("./data/rawData.json", modelInputSize)
    mirroredData = getMirroredData("./data/rawData.json", modelInputSize, nrCandelsToGen)
    generatedCandels = generateText(data, [], 0, temprature, 0, nrCandelsToGen)
    writeData("./data/generatedData.json", generatedCandels)
    writeData("./data/rawCompData.json", mirroredData)
    print("[" + str(len(generatedCandels)) + " candles generated]")
    
def addN(string):
    for i in range(1, len(string)):
        if (string[i] == ',' and string[i - 1] == '}'):
            string = string[:i+1] + '\n' + string[i+1:]
    return string

def getMirroredData(filePath, modelInputSize, nrCandelsToGen):
    f = open(filePath, "r")
    mirrorData = json.loads(f.read())[modelInputSize : modelInputSize + nrCandelsToGen]
    f.close()
    return mirrorData

def initData(filePath, modelInputSize):
    f = open(filePath, "r")
    inputData = str(json.loads(f.read())[:modelInputSize])
    f.close()
    inputData = addN(inputData)
    return inputData.rstrip(inputData[-1])    

def sealData(string):
    string = string.replace("\'", "\"") 
    string = string.replace("\n", "") 
    lastIndex = len(string) - 1
    for i in range(0, len(string)):
        if(string[lastIndex - i] == ']' and string[lastIndex - i - 1] == '}' and string[lastIndex - i - 2] == ']'):
            if string[lastIndex - i - 3] == '.':
                return string[:lastIndex - i - 3] + "]}]"
            return string[:lastIndex - i + 1]
        if (string[lastIndex - i] == ',' and string[lastIndex - i - 1] == '}' and string[lastIndex - i - 2] == ']'):
            if string[lastIndex - i - 3] == '.':
                return string[:lastIndex - i - 3] + "]}]"
            return (string[:lastIndex - i] + ']')  
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
                        for j in range(lastIndex - i, len(string)):
                            if string[j - 1] == ']' and string[j] == '}':
                                return string[:j + 1]
    return string
            
def checkForUnsealed(string):
    lastIndex = len(string) - 1
    for i in range(0, len(string)):
        if (i != lastIndex and string[lastIndex - i] != '}' and string[lastIndex - i - 1] == ']'):
            string = string[:lastIndex - i - 1] + "}" + string[lastIndex - i - 1:]
    return string
             
def catchError(string):
    return checkForUnsealed(checkForChar(checkForEnding(string)))

def strToList(string):
    list  = json.loads(sealData(string))
    return list
            
def writeData(filePath, data):
    f = open(filePath, "w")
    f.write(json.dumps(data))
    f.close()
    
def query(payload):
        headers = {"Authorization": f"Bearer {'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'}"}
        API_URL = "https://api-inference.huggingface.co/models/bigscience/bloom"
        data = json.dumps(payload)
        response = requests.request("POST", API_URL, headers=headers, data=data)
        return json.loads(response.content.decode("utf-8"))
            
def generateText(inputData, generatedData, lastOutputLen, temprature, counter, candelsToGen):
    if lastOutputLen == 0:
        lastOutputLen = len(strToList(inputData + "]"))
    if counter > 3:
        temprature -= 0.03
        
    data = query(
        {
            "inputs": inputData,
            "parameters": {"do_sample": True,
                           "repetition_penalty": 0.5,
                           "temperature": temprature,
                           "num_return_sequences":None,
                           "top_k": None,
                           "top_p": None}
        }
    )
    
    print("---------------------------------------------------\n") 
    print("Generated Candels: \n" + addN(str(generatedData)) + "\n")
    print("Progress: " + str(round((len(generatedData)/candelsToGen)*100, 2)) + "%\n")
    
    if len(generatedData) == candelsToGen:
        return generatedData
    else:
        outputList = strToList(catchError(data[0]["generated_text"]))
        if len(outputList) == lastOutputLen + 1:
            counter = 0
            generatedData.append(outputList[len(outputList) - 1])
            outputList.pop(0)
            inputStr = addN((str(outputList)).rstrip((str(outputList))[-1]))
            return generateText(inputStr , generatedData, len(outputList), temprature, counter, candelsToGen)
        else:
            counter += 1
            inputStr = catchError(data[0]["generated_text"])
            return generateText(inputStr, generatedData, lastOutputLen, temprature, counter, candelsToGen)
