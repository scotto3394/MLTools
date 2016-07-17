import seaborn as sb
import matplotlib.pyplot as plt
from bokeh.plotting import output_file
from bokeh.mpl import to_bokeh

def figtoFile(figure, pathName, fileType = 'pdf', dpi = 600):
    '''
    For a given figure object (matplotlib), saves it a specified file path, file format, and resolution.

    Args:
        figure: A matplotlib figure object to save.
        pathName: Path of file to save figure to.
        fileType: Type of image format to save as. Default: 'pdf'
        dpi: Resolution of save image (Dots per inch). Default: 600
    
    Returns:
        1 if successful, 0 if not successful.
    '''
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
    '''
    For a given figure object (matplotlib), saves it a specified file path as an HTML file (bokeh format).

    Args:
        figure: A matplotlib figure object to save.
        pathName: Path of file to save figure to.
    
    Returns:
        1 if successful, 0 if not successful.
    '''
    try:
        output_file(pathName)
        bfig = to_bokeh(figure)
    except:
        print('Failed to save figure to {}'.format(pathName))
        return 0
        
    return 1
