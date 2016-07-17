from collections import deque
import numpy as np

def windowData(data, windowSize, kernel = lambda x: np.mean(x)):
    paddedData = np.hstack([data, np.zeros(windowSize-1)])
    window = deque(np.zeros(windowSize),windowSize)
    for n in data:
        window.append(n)
        yield kernel(window)
    

def rSum(data):
    total = 0
    output = []
    for n in data:
        total += n 
        output.append(total)
    return output

def rAvg(data):
    total = 0
    output = []
    for i,n in enumerate(data):
        total += n
        output.append(total/i)
    return output