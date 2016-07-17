import seaborn as sb
import matplotlib.pyplot as plt
from bokeh.plotting import output_file
from bokeh.mpl import to_bokeh

def figtoFile(figure, pathName, fileType = 'pdf', dpi = 600):
    oldFig = plt.gcf()
    figure
    try:
        plt.savefig(pathName, bbox_inches = 'tight', dpi = dpi, format = fileType)
    except:
        print('Failed to save figure to {}'.format(pathName))
        return 0
    
    oldFig
    
    return 1

def figtoHTML(figure, pathName):
    try:
        output_file(pathName)
        bfig = to_bokeh(figure)
    except:
        print('Failed to save figure to {}'.format(pathName))
        return 0
        
    return 1
