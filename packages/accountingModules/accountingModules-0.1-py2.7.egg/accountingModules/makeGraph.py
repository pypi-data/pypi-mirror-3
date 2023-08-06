import numpy as np
import matplotlib
import matplotlib.pyplot as plt


def genPlot(xValues, yValues1, yValues2, fileName, title, legend1, legend2):
    

    Xpositions = np.arange(len(xValues))  # the x locations for the groups
    Ypositions = np.arange(4)
    matplotlib.rcParams.update({'font.size': 10})
    fig = plt.figure(figsize=[20,12])
    ax = fig.add_subplot(111)
    width = 0.35       # the width of the bars
   
    
    bar1 = ax.bar(Xpositions, yValues1, width, color='#3399FF')
    bar2 = ax.bar(Xpositions+width, yValues2, width, color='#FF3300')
    
    
#    ax.set_ylabel('Core Hours (Thousands)')
    ax.set_title(title)
    ax.set_xticks(Xpositions+width)
    ax.set_xticklabels(xValues, rotation='vertical')
#    plt.yticks(Ypositions, (1,2,3,4))

    plt.legend( (bar1[0], bar2[0]), (legend1, legend2) )

    plt.savefig(  fileName, format="pdf", dpi = 400, orientation='landscape')





def genPlot2(xValues,piList, yValues1, yValues2, avgValues, medianValues, fileName, title, legend1, legend2, legend3, legend4):
    
    width = 0.35       # the width of the bars
    Xpositions = np.arange(len(xValues))  # the x locations for the groups
    
    #Y locations on Right Y axis, 16 points apart
    Ypositions = np.arange (0, 256, 16)
    
    #set default font size
    matplotlib.rcParams.update({'font.size': 10})
    fig = plt.figure(figsize=[20,13])
    
    #for core hours
    ax1 = fig.add_subplot(111)
    
    # for avg and median
    ax2 = ax1.twinx()
    
    #for names of PI on top
    ax3 = ax1.twiny()
    
    
    ax2.grid(True)
    cross = ax2.plot(Xpositions+width, avgValues, 'kx')
    circles = ax2.plot(Xpositions+width, medianValues, 'ko')
    ax2.axhline(y=16)
    ax2.set_yticks(Ypositions)
    ax2.set_ylabel('Average nodes per job')
    for tl in ax2.get_yticklabels():
        tl.set_color('k')

    
    ax1.set_xticks(Xpositions+width)
    ax1.set_xticklabels(xValues, rotation='vertical')
    ax3.set_xticks(Xpositions+width)
    ax3.set_xticklabels(piList, rotation='vertical')
#ax3.set_title(title)

    
    bar1 = ax1.bar(Xpositions, yValues1, width, color='#3399FF')
    bar2 = ax1.bar(Xpositions+width, yValues2, width, color='#FF3300')

    #enable grid on x axis only
    ax1.xaxis.grid()
    ax1.set_xlabel("Time Allocations")
    ax1.set_ylabel("Core Hours (Thousands)")

    
    plt.legend( (bar1[0], bar2[0],cross[0], circles[0]), (legend1, legend2, legend3, legend4) )
    plt.savefig(  fileName, format="pdf", dpi = 400, orientation='landscape')

