import sys

try:
    import wx
    WX_VERSION = int(wx.version()[0])
    hasWx = True

except Exception as e:
    hasWx = False
    WX_VERSION = 0

if hasWx:
    import wx.xrc
    from wx.lib.buttons import GenBitmapTextButton
    from pubsub import pub
    import wx.adv

import os
import time
import math
import random
import numpy
import scipy.stats
import datetime

from pytransit.analysis import base
import pytransit.transit_tools as transit_tools
import pytransit.tnseq_tools as tnseq_tools
import pytransit.norm_tools as norm_tools
import pytransit.stat_tools as stat_tools

hasR = False
try:
    import rpy2.robjects
    hasR = True
except Exception as e:
    hasR = False

if hasR:
    from rpy2.robjects import r, DataFrame, globalenv, IntVector, FloatVector, StrVector, packages as rpackages

############# Description ##################

short_name = "heatmap"
long_name = "Heatmap"
short_desc = "Heatmap among Conditions"
long_desc = "Heatmap among Conditions"
transposons = ["himar1", "tn5"]

columns = ["Position","Reads","Genes"] # ???

############# Analysis Method ##############

class Heatmap(base.TransitAnalysis):
    def __init__(self):
        base.TransitAnalysis.__init__(self, short_name, long_name, short_desc, long_desc, transposons, HeatmapMethod, HeatmapGUI, []) 

################## FILE ###################

# there is no output file that could be loaded into the GUI

#class HeatmapFile(base.TransitFile):
#
#    def __init__(self):
#        base.TransitFile.__init__(self, "#CombinedWig", columns) 
#
#    def getHeader(self, path):
#        text = """This is file contains mean counts for each gene. Nzmean is mean accross non-zero sites."""
#        return text

################# GUI ##################

# right now, tnseq_stats is just intended for the command-line; TRI

class HeatmapGUI(base.AnalysisGUI):

    def __init__(self):
        base.AnalysisGUI.__init__(self)

########## METHOD #######################

# should Heatmap be a SingleConditionMethod? args like normalization are irrelevant

class HeatmapMethod(base.SingleConditionMethod):
    """   
    Norm
 
    """
    def __init__(self,gene_means,outfile): 
                ctrldata=None # initializers for superclass
                annotation_path=""
                output_file=outfile
                replicates="Sum"
                normalization="nonorm" 
                LOESS=False
                ignoreCodon=True
                NTerminus=0.0
                CTerminus=0.0
                wxobj=None
                base.SingleConditionMethod.__init__(self, short_name, long_name, short_desc, long_desc, ctrldata, annotation_path, output_file, replicates=replicates, normalization=normalization, LOESS=LOESS, NTerminus=NTerminus, CTerminus=CTerminus, wxobj=wxobj)


    @classmethod
    def fromargs(self, rawargs): 
        if len(rawargs)<3: print(self.usage_string()); sys.exit(-1)
        self.filetype = None
        if rawargs[0]=="-anova": self.filetype = "anova"
        elif rawargs[0]=="-zinb": self.filetype = "zinb"
        else: print(self.usage_string()); sys.exit(-1)
        self.infile = rawargs[1]
        self.outfile = rawargs[2]
        return self(self.infile,outfile=self.outfile)

    def Run(self):

        # assume first non-comment line is header; samples are 
        headers = None
        data,counts = [],[]

        if self.filetype=="anova":
          skip = 2 # assume one comment line and then column headers
          for line in open(self.infile):
            w = line.rstrip().split('\t')
            if skip>0: skip -= 1; headers = w[3:-3]; continue # second line has names of conditions
            cnts = [float(x) for x in w[3:-3]] # ignore first and last 3 columns
            qval = float(w[-2])
            if qval<0.05: counts.append(cnts); data.append(w)
        elif self.filetype=="zinb":
          skip,n = 2,-1 # assume one comment line and then column headers
          for line in open(self.infile):
            w = line.rstrip().split('\t')
            if skip>0: skip -= 1; headers = w; continue 
            if n==-1: 
              # second line has names of conditions, organized as 3+4*n+3 (4 groups X n conditions)
              n = int((len(headers)-6)/4)
              headers = headers[3:3+n]
              headers = [x.replace("Mean_","") for x in headers]
            cnts = [float(x) for x in w[3:3+n]] # take just the columns of means
            qval = float(w[-2])
            if qval<0.05: counts.append(cnts); data.append(w)
        else: print("filetype not recognized: %s" % self.filetype); sys.exit(-1)

        genenames = ["%s/%s" % (w[0],w[1]) for w in data]
        LFCs = []
        for row in counts:
          grandmean = numpy.mean(row)
          PC = 5
          lfcs = [math.log((x+PC)/(grandmean+PC),2) for x in row]
          LFCs.append(lfcs)

        hash = {}
        for i,col in enumerate(headers): hash[col] = FloatVector([x[i] for x in LFCs])
        df = DataFrame(hash)
        heatmapFunc = self.make_heatmapFunc()
        heatmapFunc(df,StrVector(genenames),self.outfile)

    def make_heatmapFunc(self):
      r('''
make_heatmap = function(lfcs,genenames,outfilename) { 
rownames(lfcs) = genenames
suppressMessages(require(gplots))
colors <- colorRampPalette(c("red", "white", "blue"))(n = 1000)

C = length(colnames(lfcs))
R = length(rownames(lfcs))
W = 300+C*30
H = 300+R*15

png(outfilename,width=W,height=H)
heatmap.2(as.matrix(lfcs),col=colors,margin=c(12,12),lwid=c(1,8),lhei=c(1,8),trace="none",cexCol=1.4,cexRow=1.4,key=F) # make sure white=0
dev.off()
}
      ''')
      return globalenv['make_heatmap']

    @classmethod
    def usage_string(self):
        return "usage: python %s heatmap -anova|-zinb <anova_or_zinb_output> <heatmap.png>" % sys.argv[0]
        # could add a flag for padj cutoff (or top n most signif genes)


if __name__ == "__main__":

    (args, kwargs) = transit_tools.cleanargs(sys.argv[1:])

    G = Norm.fromargs(sys.argv[1:])
    G.Run()

