from collections import deque
import numpy as np

def windowData(data, windowSize, kernel = lambda x: np.mean(x)):
    '''
    (Generator)
    Passes a filter through a 1D list/array/series, according to some specified kernel.

    Args:
        data (1D list): The given data that is being filtered.
        windowSize (int): The length of the filter/window being passed through the data.
        kernel (function handle): The function acting on the windowed data. Default is a mean of the data, resulting in a moving average.

    Returns:
        A single snapshotted filter of the data. Output can be iterated through to recover the entire filtered data.
    '''
    paddedData = np.hstack([data, np.zeros(windowSize-1)])
    window = deque(np.zeros(windowSize),windowSize)
    for n in data:
        window.append(n)
        yield kernel(window)
    
def rSum(data):
    '''
    Calculates a running total of a 1D list of data.

    Args: 
        data (1D list): The given data that is being summed.
    
    Returns:
        output (1D list): A running total of the data.
    '''
    total = 0
    output = []
    for n in data:
        total += n 
        output.append(total)
    return output

def rAvg(data):
    '''
    Calculates a running average of a 1D list of data.

    Args: 
        data (1D list): The given data that is being averaged.
    
    Returns:
        output (1D list): A running average of the data.
    '''
    total = 0
    output = []
    for i,n in enumerate(data):
        total += n
        output.append(total/i)
    return output