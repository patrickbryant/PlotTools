import time
import random
import copy
import array
import math
import ROOT
import os
import sys
import random
import collections
import json
from array import array
ROOT.gROOT.SetBatch(True)
#ROOT.gStyle.SetErrorX(0)
ROOT.gErrorIgnoreLevel = ROOT.kWarning
import PlotTools

def get(rootFile, path):
    try:
        obj = rootFile.Get(path)
        obj.IsZombie()
        return obj
    except ReferenceError:
        rootFile.ls()
        print 
        print "ERROR: Object not found -", rootFile, path
        sys.exit()

#  Make the plot
def plot(sampleDictionary, plotParameters,debug=False):
    # with open('log.json', 'w') as log:
    #     dictionaries = [sampleDictionary, plotParameters]
    #     log.write(json.dumps(dictionaries))
    #     log.close()
    same=""
    if debug: print
    if debug: print "------------------------------------------------------------------------------"
# sampleDictionary is a dictionary of dictionaries which contains 
# information for each histogram going into the current plot with 
# the following structure:
# sampleDictionary[rootFile(s)][pathToHist(s) or functions(s)] = optionsDictionary
#               ->optionsDictionary allowed contents:
#                 ["TObject"]     =   str x : name of TObject (hist,function etc.)
#                 ["label"]       =   str x : label that will go in legend
#                 ["weight"]      = float x : scale hist by x
#                 ["normalize"]   = float x : normalize hist to area x
#                 ["ratio"]       =   str x : where x matches numerator with denominator; ("numer" OR "denom")+label
#                 ["stack"]       =   int x : x is the stack order, 0 at the bottom. Stacks are solid hists
#                 ["isData"]      =  bool x : if x, draw with points and error bars
#                 ["marker"]      =   int x : ROOT code for marker type
#                 ["color"]       =   str x : hist/marker color x = "ROOT.kColor"
#                 ["drawOptions"] =   str x : x is valid ROOT DrawOption like COLZ or PE. overrides defaults for stack/overlay/is_data
#
# plotParameters is a dictionary of top level plot options:
#               ->plotParameters allowed contents:
#                 ["canvasSize"]  =  list l : l=[int x,int y], x,y in pixels. If plotting ratio, that will add to y so total height will by y + 0.4*y
#                 ["ratio"]       =  bool x : if x, draw ratio plot at bottom
#                 ["rTitle"]      =   str x : label of y axis of ratio plot
#                 ["rMax"]        = float x : max of ratio plot, default 2
#                 ["rMin"]        = float x : min of ratio plot, default 0
#                 ["rLogY"]       =  bool x : if x, yaxis of ratio plot is log
#                 ["logY"]        =  bool x : if x, yaxis draw as log plot
#                 ["yTitle"]      =   str x : title of y axis
#                 ["xTitle"]      =   str x : title of x axis
#                 ["yMax"]        = float x : max y value
#                 ["yMin"]        = float x : min y value
#                 ["xMax"]        = float x : max x value 
#                 ["xMin"]        = float x : min x value
#                 ["rebin"]       = type? x : if int, rebin hists by x, if list do variable rebinning with x, if "smart" use smartRebin function on isData hist.
#                 ["outputDir"]   =   str x : directory for output, must end with /
#                 ["outputName"]  =   str x : output pdf with name x
#                 ["title"]       =   str x : plot title
#                 ["lumi"]        =   str x : luminosity (interpreted in LaTeX)
#                 ["maxDigits"]   =   int x : axis labels will used scientific notation if more than x digits
#                 ["functions"]   =  list l : l=[[string s, float x_low, float x_high],etc.] Plot function defined by string s over range x_low, x_high. Example s="sin(x)/x"
#                 ["normalizeStack"] = float x or string x : normalize hist to area x. If string == "data", normalize to area of data hist

#    global legend, watermarks, canv
    ROOT.gStyle.SetOptStat(0)
    try: ROOT.gStyle.SetOptFit( plotParameters["fitStats"])
    except: pass
    try: ROOT.gStyle.SetOptStat(plotParameters["showStats"])
    except: pass
    # if "fitStats"  in plotParameters: ROOT.gStyle.SetOptFit( plotParameters["fitStats"])
    # if "showStats" in plotParameters: ROOT.gStyle.SetOptStat(plotParameters["showStats"])
    #
    # Make canvas and then pads for hist (and ratio if applicable)
    #
    canvasSize = plotParameters.get("canvasSize", [700,500])
    ROOT.TGaxis.SetMaxDigits(plotParameters.get("maxDigits", 5))
    ROOT.TGaxis.SetExponentOffset(0.035, -0.078, "y")
    ROOT.TGaxis.SetExponentOffset(-0.085,0.035,'x')

    ratioOnly = plotParameters.get("ratioOnly", False)
    ratio = False
    try:
        plotParameters["ratio"] = str(plotParameters["ratio"])
        if "2d" in plotParameters["ratio"]: 
                ratio = False
        elif plotParameters["ratio"]:
            ratio = True
            if not ratioOnly: canvasSize[1] = canvasSize[1]*1.2 #add area at bottom of canvas for ratio plot
            rMin   = plotParameters.get("rMin"  , 0)
            rMax   = plotParameters.get("rMax"  , 2)
            rColor = plotParameters.get("rColor", "ROOT.kGray+2")
            rTitle = plotParameters.get("rTitle", "")
    except: pass

    canvas = ROOT.TCanvas("canvas", "canvas", int(canvasSize[0]), int(canvasSize[1]))
    if ratio:
        if not ratioOnly:
            rPad = ROOT.TPad("ratio", "ratio", 0, 0.0, 1, 0.3)
            ROOT.gPad.SetTicks(1,1)
            rPad.SetBottomMargin(0.30)
            rPad.SetTopMargin(0.035)
            rPad.SetRightMargin(0.03)
            rPad.SetFillStyle(0)
            rPad.Draw()
        else:
            rPad = ROOT.TPad("ratio",  "ratio",  0, 0.0, 1, 1.0)
            ROOT.gPad.SetTicks(1,1)
            rPad.SetTopMargin(0.05)
            rPad.SetRightMargin(0.03)
            rPad.Draw()

        hPad = ROOT.TPad("hist",  "hist",  0, 0.3, 1, 1.0)
        ROOT.gPad.SetTicks(1,1)
        hPad.SetBottomMargin(0.02)
        hPad.SetTopMargin(0.05)
        hPad.SetRightMargin(0.03)
        hPad.Draw()
    else:
        hPad = ROOT.TPad("hist",  "hist",  0, 0.0, 1, 1.0)
        ROOT.gPad.SetTicks(1,1)
        hPad.SetTopMargin(0.05)
        hPad.SetRightMargin(0.03)
        hPad.Draw()
    hPad.SetFillStyle(0)
    ROOT.gStyle.SetPadTickX(1)
    ROOT.gStyle.SetPadTickY(1)
    ROOT.gROOT.ForceStyle()

    logX = plotParameters["logX"] if "logX" in plotParameters else False
    hPad.SetLogx(logX)
    if ratio: rPad.SetLogx(logX)
    logY = plotParameters["logY"] if "logY" in plotParameters else False
    hPad.SetLogy(logY)
    logZ = plotParameters["logZ"] if "logZ" in plotParameters else False
    hPad.SetLogz(logZ)
    rLogY = plotParameters["rLogY"] if "rLogY" in plotParameters else False
    if ratio: rPad.SetLogy(rLogY)

    #
    # Initialize some plotParameters
    #
    rebin  = plotParameters["rebin"] if "rebin" in plotParameters else None
    rebinX = rebin
    rebinY = rebin
    if "rebinX" in plotParameters or "rebinY" in plotParameters:
        rebin = True
        rebinX = plotParameters["rebinX"] if "rebinX" in plotParameters else 1
        rebinY = plotParameters["rebinY"] if "rebinY" in plotParameters else 1

    if rebin == "smart":
        #find isData hist
        for f in sampleDictionary:
            for p in sampleDictionary[f]:
                if "isData" in sampleDictionary[f][p]:
                    if sampleDictionary[f][p]["isData"]:
                        #get hist and find smart bins
                        File = ROOT.TFile.Open(f)
                        h = p+sampleDictionary[f][p]["TObject"] if "TObject" in sampleDictionary[f][p] else p#can take in more than just hists
                        hist = get(File,h)
                        rebin = smartBins(hist)
                        if len(rebin) < 2: rebin = 1
                        del hist
                        del File                  
            

    #
    # Get hists/functions and store in same dictionary structure as sampleDictionary
    #
    stackRatio = False
    ratioTObjects=[]
    otherObjects=[]
    stack = {} # store stack order 
    hists = {}
    systematics = {}
    drawSystematics = False
    drawErrors = plotParameters["errors"] if "errors" in plotParameters else True
    histList = []
    histListDim = 1
    Files = {}
    f_data = "" #if hist is data, draw it last.
    nObjects = 0
    varBins = False
    th2Ratio = False
    for f in sampleDictionary:
        try:
            Files[f] = ROOT.TFile.Open(f)
        except TypeError:
            Files[f] = f
        if debug: print "File:",f
        if debug: print "     ",Files[f]

        hists[f] = {}
        systematics[f] = {}

        for p in sampleDictionary[f]:
            h = p+sampleDictionary[f][p]["TObject"] if "TObject" in sampleDictionary[f][p] else p#can take in more than just hists
            hists[f][p] = get(Files[f],h)

            if hists[f][p].InheritsFrom("TH2"):
                #ROOT.gStyle.SetPalette(ROOT.kBird)
                if "ratio" in sampleDictionary[f][p]: th2Ratio=True

            try:
                if plotParameters["divideByBinWidth"]:
                    varBins = True
                    divideByBinWidth(hists[f][p],plotParameters)
            except: pass

            # rebin
            if rebin:
                if hists[f][p].InheritsFrom("TH2"):
                    hists[f][p].RebinX(rebin)
                    hists[f][p].RebinY(rebin)
                elif hists[f][p].InheritsFrom("TH1"):

                    if isinstance(rebin,list): 
                        varBins = True
                        (hists[f][p], binWidth) = do_variable_rebinning(hists[f][p], rebin)
                        hists[f][p].GetYaxis().SetTitle(plotParameters["yTitle"].replace("Bin",str(int(binWidth))+" GeV"))
                        setStyle(hists[f][p],ratio,plotParameters)
                        x_min = rebin[0]
                        x_max = rebin[-1]
                    else: 
                        nBins = hists[f][p].GetNbinsX()
                        if nBins%int(rebin) != 0: 
                            #raw_input("BAD REBIN VALUE, nBins = "+str(nBins)+" rebin = "+str(rebin))
                            #try rebin+1
                            rebin += 1
                        hists[f][p].Rebin(int(rebin))
                        #binWidth = hists[f][p].GetXaxis().GetBinWidth(1)
                        binWidth = None
            else:
                #binWidth = hists[f][p].GetXaxis().GetBinWidth(1)
                binWidth = None

            systHists=[]
            if "systematics" in sampleDictionary[f][p]:
                if sampleDictionary[f][p]["systematics"]: 
                    drawSystematics=True
                    print "Getting Systematic Variations:",sampleDictionary[f][p]["systematics"]
                    systematics[f][p] = {}
                    #systematics[f][p] = ROOT.TGraphAsymmErrors(hists[f][p])
                    for syst in sampleDictionary[f][p]["systematics"]: 
                        systHists.append(get(Files[f],syst))
                        systematics[f][p][syst] = systHists[-1]
                        try:
                            if plotParameters["divideByBinWidth"]:
                                divideByBinWidth(systHists[-1],plotParameters)
                        except: pass
                        if rebin:
                            if isinstance(rebin,list): 
                                (systHists[-1], binWidth) = do_variable_rebinning(systHists[-1], rebin)
                            else: hists[f][p].Rebin(int(rebin))
                            
                    #if not in stack, modify errors to include systematic variation
                    #if "stack" not in sampleDictionary[f][p]:
                    for bin in range(hists[f][p].GetSize()):
                        d = hists[f][p].GetBinContent(bin)
                        e_l = hists[f][p].GetBinError(bin)**2
                        e_h = hists[f][p].GetBinError(bin)**2
                        for syst in systHists:
                            s = syst.GetBinContent(bin)
                            if d > s: e_l += (d-s)**2
                            if d < s: e_h += (d-s)**2
                        e_l = e_l**0.5
                        e_h = e_h**0.5
                        
                        hists[f][p].SetBinError(bin,(e_l+e_h)/2)

                            
            nObjects += 1

            drawOptions = sampleDictionary[f][p]["drawOptions"] if "drawOptions" in sampleDictionary[f][p] else ""
            if drawOptions == "COLZ": hPad.SetRightMargin(0.12)

            try:
                hPad.SetRightMargin(plotParameters["rMargin"])
            except: pass
            try:
                hPad.SetLeftMargin(plotParameters["lMargin"])
            except: pass
            try:
                hPad.SetTopMargin(plotParameters["tMargin"])
            except: pass

            #if "TH" in str(type(hists[f][p])):
            if hists[f][p].InheritsFrom("TH1") or hists[f][p].InheritsFrom("TH2"):
                if not hists[f][p].GetSumw2N(): hists[f][p].Sumw2()
                integral = hists[f][p].Integral()
                nEntries = hists[f][p].GetEntries()
                setStyle(hists[f][p],ratio,plotParameters)
                if debug: print "Hist:",f,p,type(hists[f][p])
                if debug: print "     nEntries =",nEntries
            #if "TGraph" in type(hists[f][p]):
            #    setStyle(hists[f][p],ratio,plotParameters)

                #titles,log,max,min
            hists[f][p].SetTitle(plotParameters.get("title", ""))
            try: hists[f][p].SetTitleOffset(plotParameters["titleOffset"])
            except: pass
            try: hists[f][p].GetXaxis().SetTitle(plotParameters["xTitle"])
            except: pass
            if not varBins:
                try: hists[f][p].GetYaxis().SetTitle(plotParameters["yTitle"])
                except: pass
            try: hists[f][p].GetZaxis().SetTitle(plotParameters["zTitle"])
            except: pass
            if hists[f][p].InheritsFrom("TH1"):
                try: hists[f][p].SetMaximum(plotParameters["yMax"])
                except: pass
                try: hists[f][p].SetMinimum(plotParameters["yMin"])
                except: pass
            if hists[f][p].InheritsFrom("TH2"):
                try:    yMax = plotParameters["yMax"]
                except: yMax = hists[f][p].GetYaxis().GetBinUpEdge(hists[f][p].GetYaxis().GetNbins()-1)
                try:    yMin = plotParameters["yMin"]
                except: yMin = hists[f][p].GetYaxis().GetBinLowEdge(1)
                hists[f][p].GetYaxis().SetRangeUser(yMin,yMax)

            #if "TH" in type(hists[f][p]):
            try:    xMax = plotParameters["xMax"]
            except: xMax = hists[f][p].GetXaxis().GetXmax()
            try:    xMin = plotParameters["xMin"]
            except: xMin = hists[f][p].GetXaxis().GetXmin()
            if hists[f][p].InheritsFrom("TH1") or hists[f][p].InheritsFrom("TH2"):
                if debug: print "Setting Range On ",f,p,"xMin:",xMin,"xMax",xMax
                hists[f][p].GetXaxis().SetRangeUser(xMin,xMax) 

            try: hists[f][p].GetXaxis().SetNdivisions(plotParameters["xNdivisions"])
            except: pass
            try: hists[f][p].GetYaxis().SetNdivisions(plotParameters["yNdivisions"])
            except: pass
            try: hists[f][p].GetZaxis().SetNdivisions(plotParameters["zNdivisions"])
            except: pass
            
            # scale hist if needed
            if "normalize" in sampleDictionary[f][p]:
                hists[f][p].Scale(sampleDictionary[f][p]["normalize"]/integral if integral else 0.0)
            elif  "weight" in sampleDictionary[f][p]:
                hists[f][p].Scale(sampleDictionary[f][p]["weight"])

            if hists[f][p].InheritsFrom("TH1") or hists[f][p].InheritsFrom("TH2"):
                integral = hists[f][p].Integral()
                if debug: print "     Integral =",integral


            if hists[f][p].InheritsFrom("TH1") or hists[f][p].InheritsFrom("TH2") or hists[f][p].InheritsFrom("TF1") or hists[f][p].InheritsFrom("TF2"):
                histList.append(hists[f][p])
                if hists[f][p].InheritsFrom("TH2"):
                    histListDim = 2
            # colors and markers
            if "color" in sampleDictionary[f][p]:
                hists[f][p].SetLineColor(eval(sampleDictionary[f][p]["color"]))
                hists[f][p].SetMarkerColor(eval(sampleDictionary[f][p]["color"]))
                if "marker" in sampleDictionary[f][p]:
                    hists[f][p].SetMarkerStyle(eval(sampleDictionary[f][p]["marker"]))
                if "stack" in sampleDictionary[f][p] and "TH2" not in str(type(hists[f][p])):
                    hists[f][p].SetFillColor(eval(sampleDictionary[f][p]["color"]))
                    #hists[f][p].SetMarkerColor(eval(sampleDictionary[f][p]["color"]) if sampleDictionary[f][p]["stack"] != 2 else ROOT.kBlack)
                    hists[f][p].SetMarkerColor(ROOT.kBlack)
                    hists[f][p].SetLineWidth(1)
                    #hists[f][p].SetLineColor(eval(sampleDictionary[f][p]["color"]) if sampleDictionary[f][p]["stack"] != 2 else ROOT.kBlack)
                    hists[f][p].SetLineColor(ROOT.kBlack)

            try: hists[f][p].SetLineStyle(sampleDictionary[f][p]["lineStyle"])
            except: pass
            try: hists[f][p].SetLineWidth(sampleDictionary[f][p]["lineWidth"])
            except: pass
            try: hists[f][p].SetFillStyle(sampleDictionary[f][p]["fillStyle"])
            except: pass
            try: hists[f][p].SetFillColor(eval(sampleDictionary[f][p]["fillColor"]))
            except: pass
            try: hists[f][p].SetLineColor(eval(sampleDictionary[f][p]["lineColor"]))
            except: pass
            try: hists[f][p].SetMaximum(plotParameters["zMax"])
            except: pass
            try: hists[f][p].SetMinimum(plotParameters["zMin"])
            except: pass
            

            hPad.cd()
            # if hist has an associated stack order, move it to stack dictionary for later stacking
            if "stack" in sampleDictionary[f][p]:
                stack[sampleDictionary[f][p]["stack"]] = hists[f][p]
                stackDrawOptions = sampleDictionary[f][p]["drawOptions"] if "drawOptions" in sampleDictionary[f][p] else ""
                if "ratio" in sampleDictionary[f][p]: stackRatio = sampleDictionary[f][p]["ratio"]
            elif hists[f][p].InheritsFrom("TH1"):
                try:
                    if sampleDictionary[f][p]["isData"]:
                        f_data = f
                        p_data = p
                        h_data_draw = " ex0 PE "+drawOptions
                except: pass

            elif hists[f][p].InheritsFrom("TH2"):
                if not th2Ratio:
                    if not ratioOnly: 
                        if debug: print "hists["+f+"]["+p+"].Draw("+same+drawOptions+")"
                        hists[f][p].Draw(same+drawOptions)
                        same="SAME "
            else:#function or other ROOT object? Try drawing it..
                if "xMin" in sampleDictionary[f][p]: 
                    if "xMax" in sampleDictionary[f][p]:
                        hists[f][p].SetRange(sampleDictionary[f][p]["xMin"],sampleDictionary[f][p]["xMax"])
                if "pad" in sampleDictionary[f][p]:
                    if "rPad" in sampleDictionary[f][p]["pad"]:
                        ratioTObjects.append(hists[f][p])
                    if not ratioOnly: 
                        if debug: print "hists["+f+"]["+p+"].Draw("+drawOptions+")"
                        otherObjects.append({'object':hists[f][p], 'drawOptions':drawOptions})
                        #hists[f][p].Draw(drawOptions)
                        #same="SAME "
                else:
                    if not ratioOnly: 
                        if debug: print "hists["+f+"]["+p+"].Draw("+drawOptions+")"
                        otherObjects.append({'object':hists[f][p], 'drawOptions':drawOptions})
                        #hists[f][p].Draw(drawOptions)
                        #same="SAME "

    if f_data: 
        xMax = plotParameters["xMax"] if "xMax" in plotParameters else hists[f][p].GetXaxis().GetXmax()
        xMin = plotParameters["xMin"] if "xMin" in plotParameters else hists[f][p].GetXaxis().GetXmin()
        hists[f_data][p_data].GetXaxis().SetRangeUser(xMin,xMax) 

        if not ratioOnly: 
            if debug: print "hists["+f_data+"]["+p_data+"].Draw("+same+h_data_draw+")"
            hists[f_data][p_data].Draw(same+h_data_draw)                    
            same="SAME "

    # normalize stack before setting yaxis range
    if stack:
        normalizeStack = plotParameters["normalizeStack"] if "normalizeStack" in plotParameters else None
        if normalizeStack == "data": normalizeStack = hists[f_data][p_data].Integral()

        if normalizeStack: 
            stackIntegral = 0
            for i in sorted(stack.keys()): stackIntegral += stack[i].Integral()
            scaleStack = normalizeStack/stackIntegral if stackIntegral else 0
            for i in sorted(stack.keys()): stack[i].Scale(scaleStack)


    if histListDim == 1:
        yMin = plotParameters["yMin"] if "yMin" in plotParameters else None
        yMax = plotParameters["yMax"] if "yMax" in plotParameters else None
        if debug: print "yMin",yMin,"yMax",yMax
        SetYaxisRange(histList,yMax,yMin,logY,ratio,debug)
    else:
        zMin = plotParameters["zMin"] if "zMin" in plotParameters else None
        zMax = plotParameters["zMax"] if "zMax" in plotParameters else None
        if debug: print "zMin",zMin,"zMax",zMax
        SetYaxisRange(histList,zMax,zMin,logY,ratio,debug)

    # stack up the hists in stack in proper order
    if stack:
        stacked = ROOT.THStack("stack", "")
        for i in sorted(stack.keys()):
            stacked.Add(copy.copy(stack[i]), "hist")

        if not th2Ratio:
            hPad.cd()
            if not ratioOnly: 
                if histListDim == 2:
                    if debug: print "stacked.GetStack().Last().Draw("+same+" "+stackDrawOptions+")"
                    setStyle(stacked.GetStack().Last())
                    stacked.GetStack().Last().Draw(same+" "+stackDrawOptions)
                    same="SAME "
                else:
                    if debug: print "stacked.Draw("+same+" "+stackDrawOptions+")"
                    stacked.Draw(same+" "+stackDrawOptions)
                    same="SAME "
            if "stackErrors" in plotParameters: 
                errors = ROOT.TH1F(stacked.GetStack().Last())
                errors.SetFillColor(ROOT.kGray+2)
                errors.SetFillStyle(3245)
                errors.SetLineStyle(1)
                errors.SetLineWidth(0)
                errors.SetLineColor(ROOT.kWhite)
                #calculate systematic error band
                # for f in systematics:
                #     for p in systematics[f]:
                #         for s in systematics[f][p]:
                #             systematic = s
                #             for word in p.split("_"): systematic = systematic.replace(word,"")
                #             print p,systematic
                if not ratioOnly: 
                    if debug: print """errors.Draw("e2 SAME")"""
                    errors.Draw("e2 SAME")


    #draw hists that are not data or stacked
    hPad.cd()
    for f in sampleDictionary:
        for p in sampleDictionary[f]:
            if "stack" not in sampleDictionary[f][p] and hists[f][p].InheritsFrom("TH1"): 
                if "isData" in sampleDictionary[f][p]:
                    if sampleDictionary[f][p]["isData"]:
                        continue
                drawOptions = sampleDictionary[f][p]["drawOptions"] if "drawOptions" in sampleDictionary[f][p] else "HIST "
                if not ratioOnly: 
                    if debug: print "hists["+f+"]["+p+"].Draw("+drawOptions+same+")"
                    #if "HIST P" in drawOptions: hists[f][p].Draw("HIST"+same) ## NEED THIS FOR SINGLE BIN ACCEPTANCE PLOTS...
                    hists[f][p].Draw(drawOptions+same)
                    same=" SAME "

    for obj in otherObjects:
        obj['object'].Draw(obj['drawOptions']+same)

    if f_data: 
        hists[f_data][p_data].SetMarkerStyle(20)
        hists[f_data][p_data].SetMarkerSize(0.7)
        hists[f_data][p_data].SetLineWidth(2 if "lineWidth" not in sampleDictionary[f_data][p_data] else sampleDictionary[f_data][p_data]["lineWidth"])
        if not ratioOnly:
            if debug: print "hists["+f_data+"]["+p_data+"].Draw("+same+h_data_draw+")"
            if debug: print "hists["+f_data+"]["+p_data+"].Draw("+"ex0 axis "+same+")"
            hists[f_data][p_data].Draw(same+h_data_draw) #HAVE TO DRAW TWICE BECAUSE FUCK ROOT
            hists[f_data][p_data].Draw("ex0 axis "+same) #HAVE TO DRAW TWICE BECAUSE FUCK ROOT
            same="SAME "

    hPad.RedrawAxis()

    #
    # Now make ratio(s)
    #
    if ratio or th2Ratio:
        ratioDictionary = {"numer":{},"denom":{}}
        if stackRatio: 
            if "numer" in stackRatio:
                ratioDictionary["numer"][stackRatio.replace("numer","")] = [stacked.GetStack().Last()]
            if "denom" in stackRatio:
                ratioDictionary["denom"][stackRatio.replace("denom","")] = [stacked.GetStack().Last()]

            #for differential distributions in bottom pad
            if "signal" in stackRatio:
                PlotTools.dN_N(stacked.GetStack().Last(), True,  stackRatio.replace("signal",""), rPad, rMin, rMax)
            if "bkgd"   in stackRatio:
                PlotTools.dN_N(stacked.GetStack().Last(), False, stackRatio.replace("bkgd"  ,""), rPad, rMin, rMax)

        for f in sampleDictionary:
            for p in sampleDictionary[f]:
                if "stack" not in sampleDictionary[f][p] and "ratio" in sampleDictionary[f][p]:
                    histRatio = sampleDictionary[f][p]["ratio"]
                    if "numer" in histRatio:
                        if histRatio.replace("numer","") in ratioDictionary["numer"]:
                            ratioDictionary["numer"][histRatio.replace("numer","")].append(hists[f][p])
                        else:
                            ratioDictionary["numer"][histRatio.replace("numer","")] = [hists[f][p]]

                    if "denom" in histRatio:
                        if histRatio.replace("denom","") in ratioDictionary["denom"]:
                            ratioDictionary["denom"][histRatio.replace("denom","")].append(hists[f][p])
                        else:
                            ratioDictionary["denom"][histRatio.replace("denom","")] = [hists[f][p]]
                        #ratioDictionary["denom"][histRatio.replace("denom","")] = hists[f][p]

                    #differential distributions
                    if "signal" in histRatio:
                        PlotTools.dN_N(hists[f][p], True,  histRatio.replace("signal",""), rPad, rMin, rMax)
                    if "bkgd"   in histRatio:
                        PlotTools.dN_N(hists[f][p], False, histRatio.replace("bkgd"  ,""), rPad, rMin, rMax)

        #draw ratios on rPad
        denomColors = False
        numerColors = False
        for ratioSet in ratioDictionary["denom"].keys():
            if len(ratioDictionary["denom"][ratioSet]) > 1: denomColors = True
            if len(ratioDictionary["numer"][ratioSet]) > 1: numerColors = True
            if denomColors and numerColors: 
                print "ERROR:"
                print ratioDictionary["denom"][ratioSet]
                print ratioDictionary["numer"][ratioSet]
                continue #don't know how to handle this yet..
            for denom in ratioDictionary["denom"][ratioSet]:
                #denom = ratioDictionary["denom"][ratioSet]
                for numer in ratioDictionary["numer"][ratioSet]:
                    if denomColors: lColor = denom.GetLineColor()
                    else:           lColor = numer.GetLineColor()

                    if not th2Ratio:
                        ratioErrors = plotParameters["ratioErrors"] if "ratioErrors" in plotParameters else True
                        doSignificance = True if "significance" in plotParameters["ratio"] else False
                        rErrors = PlotTools.ratio(rPad, numer, denom, rMin, rMax, rTitle, rColor, lColor, ratioTObjects, ratioErrors, doSignificance,plotParameters)
                    else:
                        hPad.cd()
                        try:
                            if "significance" in plotParameters["ratio"]:
                                for i in range(1,numer.GetNbinsX()+1):
                                    for j in range(1,numer.GetNbinsY()+1):
                                        nc = numer.GetBinContent(i,j)
                                        ne = numer.GetBinError(i,j)
                                        dc = denom.GetBinContent(i,j)
                                        de = denom.GetBinError(i,j)
                                        sig = (nc-dc)/((dc+de**2)**0.5) if dc>0 else 0
                                        numer.SetBinContent(i,j,sig)
                                        numer.SetBinError(i,j,0)
                            elif "difference" in plotParameters["ratio"]:
                                numer.Add(denom,-1)
                            elif "ratio" in plotParameters["ratio"]:
                                numer.Divide(denom)
                        except:
                            numer.Divide(denom)                                
                        if debug: print """numer.Draw("SAME COLZ")"""
                        numer.Draw("SAME COLZ")
        

    # make legend
    drawLegend = False
    drawOrder = {}
    legendEntries=[]
    for f in sampleDictionary:
        for p in sampleDictionary[f]:
            if "stack" in sampleDictionary[f][p]:
                legendMark = "f"
                if "label" in sampleDictionary[f][p]:
                    drawLegend = True
                    #legend.AddEntry(hists[f][p], sampleDictionary[f][p]["label"], legendMark)
                    legendEntries.append([hists[f][p], sampleDictionary[f][p]["label"], legendMark])
                    drawOrder[sampleDictionary[f][p]["legend"] if "legend" in sampleDictionary[f][p] else len(legendEntries)] = len(legendEntries)-1
            if "drawOptions" in sampleDictionary[f][p]:
                legendMark = sampleDictionary[f][p]["drawOptions"]
                legendMark = legendMark.replace("C","L")
                legendMark = legendMark.replace("HIST","")
            elif "marker" in sampleDictionary[f][p]:
                legendMark = "p"
            else:
                legendMark = "l"
                if "isData" in sampleDictionary[f][p]:
                    if sampleDictionary[f][p]["isData"]: 
                        legendMark = "ep"

            if "legendMark" in sampleDictionary[f][p]: legendMark = sampleDictionary[f][p]["legendMark"]

            if "label" in sampleDictionary[f][p] and "stack" not in sampleDictionary[f][p]:
                drawLegend = True
                #legend.AddEntry(hists[f][p], sampleDictionary[f][p]["label"], legendMark)
                legendEntries.append([hists[f][p], sampleDictionary[f][p]["label"], legendMark])
                drawOrder[sampleDictionary[f][p]["legend"] if "legend" in sampleDictionary[f][p] else len(legendEntries)] = len(legendEntries)-1

    nLegend = len(drawOrder.keys())
    if ("stackErrors" in plotParameters and drawLegend and drawErrors) or (ratio and not th2Ratio and ratioErrors and drawErrors):
        nLegend += 1
    
    hPad.Update()
    X1, X2 = UserToNDC(hPad, "x", hPad.GetFrame().GetX1()), UserToNDC(hPad, "x", hPad.GetFrame().GetX2())
    dX = X2 - X1
    xleg = plotParameters.get("xleg", [X2 - dX/3, X2 - 0.035])
    #xleg = [X2 - dX/3, X2 - 0.035] if "xleg" not in plotParameters else plotParameters["xleg"] #default tick length is 0.03
    #xleg = [0.67             , 0.930] if "xleg" not in plotParameters else plotParameters["xleg"]
    Y1, Y2 = UserToNDC(hPad, "y", hPad.GetFrame().GetY1()), UserToNDC(hPad, "y", hPad.GetFrame().GetY2())
    dY = Y2 - Y1
    yleg = plotParameters.get("yleg", [Y2 - 0.06*nLegend, Y2 - 0.035])
    #yleg = [Y2 - 0.06*nLegend, Y2 - 0.035] if "yleg" not in plotParameters else plotParameters["yleg"] #default tick length is 0.03
    yspace = (yleg[1]-yleg[0])/nLegend if nLegend else 1
    #yleg = [0.91-0.05*nLegend, 0.910] if "yleg" not in plotParameters else plotParameters["yleg"]
    legend = ROOT.TLegend(xleg[0], yleg[0], xleg[1], yleg[1])
    try: legend.SetNColumns(plotParameters["legendColumns"])
    except: pass
    legend.SetTextAlign(12)

    for i in sorted(drawOrder.keys()):
        legend.AddEntry(legendEntries[drawOrder[i]][0],legendEntries[drawOrder[i]][1],legendEntries[drawOrder[i]][2])

    if "stackErrors" in plotParameters and drawLegend and drawErrors:
        #errors.SetLineColor(ROOT.kWhite)
        legend.AddEntry(errors,"Stat+Syst Uncertainty" if drawSystematics else "Stat. Uncertainty","f")
    elif ratio and not th2Ratio and ratioErrors and drawErrors:
        rErrors.SetLineColor(ROOT.kWhite)
        legend.AddEntry(rErrors,"Stat. Uncertainty")

    if drawLegend:
        legend.SetBorderSize(0)
        legend.SetFillColor(0)
        legend.SetFillStyle(0)
        try: ROOT.gStyle.SetLegendTextSize(plotParameters["legendTextSize"])
        except: pass
        hPad.cd()
        if debug: print "legend.Draw()"
        legend.Draw()

    # Text
    hPad.cd()
    try:
        box = ROOT.TBox(plotParameters["box"][0],plotParameters["box"][1],plotParameters["box"][2],plotParameters["box"][3])
        box.SetLineColor(ROOT.kBlack)
        box.SetFillColor(ROOT.kWhite)
        box.SetFillStyle(1001)
        if debug: print """box.Draw("same l")"""
        box.Draw("same l")
    except: pass

    if "legendSubText" in plotParameters:
        i = 1
        legendSubText = []
        lstx = xleg[0] if 'lstx' not in plotParameters else plotParameters['lstx']
        lsty = yleg[0] if 'lsty' not in plotParameters else plotParameters['lsty']
        if 'lstLocation' in plotParameters:
            lstLocation = plotParameters["lstLocation"]
            if lstLocation == "right": 
                lstx, lsty = xleg[1], yleg[1]
                i = 1
        for line in plotParameters["legendSubText"]:
            legendSubText.append( ROOT.TLatex(lstx, lsty-i*yspace, "#bf{ "+line+"}") )
            legendSubText[-1].SetTextAlign(11)
            legendSubText[-1].SetTextSize((1-legend.GetEntrySeparation())*yspace)
            legendSubText[-1].SetNDC()
            legendSubText[-1].Draw()
            i += 1

    hPad.Update()
    xTitleLeft  = UserToNDC(hPad, "x", hPad.GetFrame().GetX1(), debug)
    xTitleRight = UserToNDC(hPad, "x", hPad.GetFrame().GetX2(), debug)
    yTitleLeft  = UserToNDC(hPad, "y", hPad.GetFrame().GetY2(), debug) + 0.007
    if debug: print "xTitleLeft",xTitleLeft,"yTitleLeft",yTitleLeft

    try:
        plotParameters["titleLeft"]
        if "xTitleLeft" in plotParameters: xTitleLeft = plotParameters["xTitleLeft"]
        if "yTitleLeft" in plotParameters: yTitleLeft = plotParameters["yTitleLeft"]
        titleLeft  = ROOT.TLatex(xTitleLeft, yTitleLeft, "#bf{"+plotParameters["titleLeft"]+"}")
        titleLeft.SetTextAlign(11)
        titleLeft.SetNDC()
        titleLeft.Draw()
    except: pass

    try:
        plotParameters["titleCenter"]
        xTitleCenter = 0.5   if "xTitleCenter" not in plotParameters else plotParameters["xTitleCenter"]
        yTitleCenter = yTitleLeft if "yTitleCenter" not in plotParameters else plotParameters["yTitleCenter"]
        titleCenter  = ROOT.TLatex(xTitleCenter, yTitleCenter, "#bf{"+plotParameters["titleCenter"]+"}")
        titleCenter.SetTextAlign(21)
        titleCenter.SetNDC()
        titleCenter.Draw()
    except: pass

    try:
        plotParameters["titleRight"]
        if "xTitleRight" in plotParameters: xTitleRight = plotParameters["xTitleRight"]
        yTitleRight = yTitleLeft if "yTitleRight" not in plotParameters else plotParameters["yTitleRight"]
        titleRight  = ROOT.TLatex(xTitleRight, yTitleRight, "#bf{"+plotParameters["titleRight"]+"}")
        titleRight.SetTextAlign(31)
        titleRight.SetNDC()
        titleRight.Draw()
    except: pass

    try:
        plotParameters["subTitleRight"]
        xSubTitleRight = xTitleRight - 0.035 if "xSubTitleRight" not in plotParameters else plotParameters["xSubTitleRight"]
        ySubTitleRight = UserToNDC(hPad, "y", hPad.GetFrame().GetY2(), debug) - 0.035 if "ySubTitleRight" not in plotParameters else plotParameters["ySubTitleRight"]
        subTitleRight  = ROOT.TLatex(xSubTitleRight, ySubTitleRight, "#bf{"+plotParameters["subTitleRight"]+"}")
        subTitleRight.SetTextAlign(33)
        subTitleRight.SetNDC()
        subTitleRight.Draw()
    except: pass

    if "drawLines" in plotParameters:
        tline = ROOT.TLine()
        for line in plotParameters["drawLines"]:
            if debug: print "tline.DrawLine("+str(line[0])+","+str(line[1])+","+str(line[2])+","+str(line[3])+")"
            tline.DrawLine(line[0],line[1],line[2],line[3])

    if "ratioLines" in plotParameters:
        rPad.cd()
        tline = ROOT.TLine()
        for line in plotParameters["ratioLines"]:
            if debug: print "tline.DrawLine("+str(line[0])+","+str(line[1])+","+str(line[2])+","+str(line[3])+")"
            tline.DrawLine(line[0],line[1],line[2],line[3])
        hPad.cd()

    #if "functions" in plotParameters:
    try:
        funcs=[]
        contours=[]
        for i, funcDef in enumerate(plotParameters["functions"]):
            #print "Plotting:",funcDef
            hPad.cd()
            if "y" in funcDef[0]:
                funcs.append(ROOT.TF2("func"+str(i),funcDef[0],funcDef[1],funcDef[2],funcDef[3],funcDef[4]))
                contours.append(array("d"))
                for cont in funcDef[5]:
                    contours[-1].append(cont)
                funcs[-1].SetContour(len(funcDef[5]),contours[-1])
                funcs[-1].SetLineColor(eval(funcDef[6]))
                funcs[-1].SetLineStyle(funcDef[7])
                funcs[-1].SetLineWidth(5)
                if debug: print """funcs[-1].Draw("cont3 SAME")"""
                funcs[-1].Draw("cont3 SAME")
            else:
                funcs.append(ROOT.TF1("func"+str(i),funcDef[0],funcDef[1],funcDef[2]))
                funcs[-1].SetLineColor(ROOT.kBlack)
                funcs[-1].SetLineWidth(4)
                if debug: print """funcs[-1].Draw("SAME")"""
                funcs[-1].Draw("SAME")
    except:
        pass

    #update and save canvas
    canvas.Modified()
    canvas.Update()

    if plotParameters["outputDir"]:
        outdir = plotParameters["outputDir"]+"/".join(plotParameters["outputName"].split("/")[:-1])
        if not os.path.exists(outdir):         
            os.makedirs(outdir)

    logstr = "_logy" if logY else ""
    if debug: print "SaveAs("+plotParameters["outputDir"]+plotParameters["outputName"]+logstr+".pdf)"
    canvas.SaveAs(plotParameters["outputDir"]+plotParameters["outputName"]+logstr+".pdf")
    canvas.SaveAs(plotParameters["outputDir"]+plotParameters["outputName"]+logstr+".C")
    #canvas.SaveAs(plotParameters["outputDir"]+plotParameters["outputName"]+".root")

    return canvas


def UserToNDC(pad,axis,u,debug=False):
    if axis == "x": 
        u1, u2 = pad.GetX1(), pad.GetX2()
    if axis == "y": 
        u1, u2 = pad.GetY1(), pad.GetY2()
    ndc = (u - u1)/(u2-u1);
    if debug: print "UserToNDC | "+axis+":",u,"| "+axis+"1:",u1,"| "+axis+"2:",u2,"| NDC:",ndc
    return ndc
    

def show_overflow(hist):
    """ Show overflow and underflow on a TH1. h/t Josh """

    nbins          = hist.GetNbinsX()
    underflow      = hist.GetBinContent(   0   )
    underflowerror = hist.GetBinError  (   0   )
    overflow       = hist.GetBinContent(nbins+1)
    overflowerror  = hist.GetBinError  (nbins+1)
    firstbin       = hist.GetBinContent(   1   )
    firstbinerror  = hist.GetBinError  (   1   )
    lastbin        = hist.GetBinContent( nbins )
    lastbinerror   = hist.GetBinError  ( nbins )

    if underflow != 0 :
        newcontent = underflow + firstbin
        if firstbin == 0 :
            newerror = underflowerror
        else:
            newerror = math.sqrt( underflowerror * underflowerror + firstbinerror * firstbinerror )
        hist.SetBinContent(1, newcontent)
        hist.SetBinError  (1, newerror)

    if overflow != 0 :
        newcontent = overflow + lastbin
        if lastbin == 0 :
            newerror = overflowerror
        else:
            newerror = math.sqrt( overflowerror * overflowerror + lastbinerror * lastbinerror )
        hist.SetBinContent(nbins, newcontent)
        hist.SetBinError  (nbins, newerror)

def ratio(rPad, numer, denom, rMin, rMax, rTitle, rColor, lColor, ratioTObjects=[],ratioErrors=True, doSignificance=False, plotParameters=None, drawOptions=None):
    ratioOnly = plotParameters.get("ratioOnly", False)
    logX      = plotParameters.get("logX",      False)

    same=""
    numer.GetXaxis().SetLabelSize(0)
    denom.GetXaxis().SetLabelSize(0)

    numerdenom = copy.copy(numer)
    denomdenom = copy.copy(numer)

    numerdenom.SetTitle("")
    denomdenom.SetTitle("")
    
    if not ratioOnly:
        numerdenom.GetYaxis().SetNdivisions(503)
        denomdenom.GetYaxis().SetNdivisions(503)

    numerdenom.SetName(numer.GetName()+"numerdenom"+str(random.random()))
    denomdenom.SetName(numer.GetName()+"denomdenom"+str(random.random()))

    #ratio_TGraph = ROOT.TGraphAsymmErrors()
    #ratio_TGraph.SetName("ratio_TGraph")
    #ROOT.SetOwnership(ratio_TGraph,False)

    for hist in [numerdenom, denomdenom]:
        hist.Reset()
        hist.SetMinimum(rMin)
        hist.SetMaximum(rMax)
        hist.GetYaxis().SetTitle(rTitle)
        #hist.GetYaxis().SetTitleOffset(20)
        ROOT.SetOwnership(hist, False)#?

    nbins = numer.GetNbinsX()
    true_r = {}
    for bin in xrange(0, nbins+2):
        x  = ROOT.Double(numer.GetBinCenter(bin))
        nc = numer.GetBinContent(bin)
        ne = numer.GetBinError(bin)
        try:
            dc = denom.GetBinContent(bin)
            de = denom.GetBinError(bin)
        except:
            dc = denom.Eval(x)
            de = 0

        val_nd = nc/dc if dc else -99
        val_dd = 1.0   if dc else -99
        err_nd = ne/dc if dc and ratioErrors else 0
        err_dd = de/dc if dc else 0 #if dc and ratioErrors else 0

        # r      = ROOT.Double( nc    /dc if dc else -99)
        # r_up   = ROOT.Double((ne)/dc if dc else -99)
        # r_down = ROOT.Double((ne)/dc if dc else -99)

        if doSignificance:
            val_nd = (nc-dc)/(dc+de**2)**0.5 if dc>0 else 0
            val_dd = 0.0
            err_nd = 0.0
            err_dd = de/dc**0.5 if dc>0 else 0

        true_r[bin] = val_nd
        numerdenom.SetBinContent(bin, val_nd if val_nd-err_nd < rMax else -99 )
        denomdenom.SetBinContent(bin, val_dd)
        numerdenom.SetBinError(  bin, err_nd if val_nd-err_nd < rMax else   0 )
        denomdenom.SetBinError(  bin, err_dd)

        #ratio_TGraph.SetPoint(bin-1,x,r)
        #ratio_TGraph.SetPointError(bin-1,ROOT.Double(0),ROOT.Double(0),r_down,r_up)


    setStyle(numerdenom)
    setStyle(denomdenom)
    if not ratioOnly:
        numerdenom.GetYaxis().SetLabelOffset(0.015)
        denomdenom.GetYaxis().SetLabelOffset(0.015)
        numerdenom.GetYaxis().SetTitleOffset(0.95 if (rMax*100)%100 == 0 else 1.1)
        denomdenom.GetYaxis().SetTitleOffset(0.95 if (rMax*100)%100 == 0 else 1.1)
        numerdenom.GetXaxis().SetTitleSize(25)
        denomdenom.GetXaxis().SetTitleSize(25)
    if ratioOnly:
        numerdenom.GetXaxis().SetTitleOffset(1)
        denomdenom.GetXaxis().SetTitleOffset(1)        

    if logX:
        numerdenom.GetXaxis().SetLabelOffset(-0.005)
        denomdenom.GetXaxis().SetLabelOffset(-0.005)

    #setStyle(ratio_TGraph)
    #ratio_TGraph.GetYaxis().SetLabelOffset(0.015)
    #ratio_TGraph.GetYaxis().SetTitleOffset(0.95 if (rMax*100)%100 == 0 else 1.1)
    #ratio_TGraph.GetXaxis().SetTitleSize(25)

    #numerdenom.LabelsDeflate("X")
    #denomdenom.LabelsDeflate("X")
    #numerdenom.LabelsOption("d","X")
    #denomdenom.LabelsOption("d","X")

    rPad.cd()

    denomdenom.SetFillColor(eval(rColor))
    denomdenom.SetFillStyle(3245)
    denomdenom.SetMarkerSize(0.0)
    if ratioErrors and (denom.InheritsFrom("TH1") or denom.InheritsFrom("TH2")):
        denomdenom.Draw("E2 SAME")
    
    # Fix for error bars when points arent on the ratio
    numerdenom.SetLineColor(lColor)
    numerdenom.SetMarkerColor(lColor)
    # if "TH" in str(denom):
    numerdenom.Draw("x0 P E0 SAME" if not doSignificance else "HIST SAME")
    # else:
    #    numerdenom.Draw("HIST SAME")

    oldSize = numerdenom.GetMarkerSize()
    # numerdenom.SetMarkerSize(0)
    # numerdenom.DrawCopy("PE x0 SAME")
    # numerdenom.SetMarkerSize(oldSize)
    #if not ratioErrors:
    numerdenom.SetMarkerStyle(20)
    numerdenom.SetMarkerSize(0.5)
        #numerdenom.SetMarkerStyle(7)
    if not doSignificance:# and "TH" in str(denom): 
        numerdenom.DrawCopy("x0 SAME PE")    

    for obj in ratioTObjects: 
        #obj.SetRange(numerdenom.GetXaxis().GetXmin(), numerdenom.GetXaxis().GetXmax())
        obj.Draw("SAME")
        
    one = ROOT.TF1("one","1",hist.GetXaxis().GetXmin(),hist.GetXaxis().GetXmax())
    one.SetLineColor(ROOT.kBlack)
    #one.SetLineStyle(1)
    one.SetLineWidth(1)
    one.DrawCopy("same l")

    try:    xMax = plotParameters["xMax"]
    except: xMax = hist.GetXaxis().GetXmax()
    try:    xMin = plotParameters["xMin"]
    except: xMin = hist.GetXaxis().GetXmin()

    a=ROOT.TArrow()
    a.SetFillColor(lColor)
    rMax=float(rMax)
    rMin=float(rMin)
    for bin in range(1,numerdenom.GetSize()-1):
        #r=numerdenom.GetBinContent(bin)
        r=true_r[bin]
        e=numerdenom.GetBinError(  bin) if ratioErrors else 0
        x=numerdenom.GetBinCenter(bin)
        if x > xMax or x < xMin: continue

        if r == -99: continue

        try:
            nb = numer.GetBinContent(bin)
        except AttributeError:
            nb = numer.Eval(x)

        try:
            db = denom.GetBinContent(bin)
        except AttributeError:
            db = denom.Eval(x)

        if r+e<rMin and nb > 0:#down arrow
            a.DrawArrow( x,rMin + (rMax-rMin)/5,  x,rMin  , 0.015,"|>")

        elif r-e>rMax and db > 0:#up arrow
            a.DrawArrow( x,rMax - (rMax-rMin)/5,  x,rMax  , 0.015,"|>")
            
    #ratio_TGraph.SetLineColor(ROOT.kRed)
    #ratio_TGraph.SetMaximum(rMax)
    #ratio_TGraph.SetMinimum(rMin)
    #ratio_TGraph.Draw("SAME PE0")

    return denomdenom


def compare(data, pred):
    ks   = data.KolmogorovTest(pred)
    chi2 =        data.Chi2Test(pred, "QUWP CHI2")
    ndf  = chi2 / data.Chi2Test(pred, "QUW CHI2/NDF") if chi2 else 0.0
    return ks, chi2, ndf


#
# Smart variable bin finder
#
def smartBins(hist,debug=False):
    originalWidth = hist.GetXaxis().GetBinWidth(1)
    
    #find peak bin and last non-empty bin
    maxBin = 0
    maxVal = 0
    lastBin = 0
    minError = 0.1
    fractionalError = minError
    for b in range(1, hist.GetNbinsX()+1):
        val=hist.GetBinContent(b)
        if val > 0:
            lastBin = hist.GetXaxis().GetBinUpEdge(b)

        if val > maxVal:
            maxBin = b
            maxVal = val
            error = hist.GetBinError(b)
            fractionalError = error/maxVal

    if fractionalError > minError:
        targetError = minError
    else:
        targetError = fractionalError

    targetError = 0.1

    #go to first non-empty bin. Group bins until frac.uncertainty is <= targetError
    foundStart = False
    bins = [hist.GetXaxis().GetBinLowEdge(1)]
    accumulatedVal = 0
    for b in range(1, hist.GetNbinsX()+1):
        val=hist.GetBinContent(b)
        nextVal=hist.GetBinContent(b) if b < hist.GetNbinsX() else 0

        if val > 0:
            foundStart = True
            accumulatedVal  += val
            nextError        = nextVal**(-0.5) if nextVal > 0 else 0
            accumulatedError = accumulatedVal**(-0.5)
            targetModifier = 2 - (accumulatedVal/maxVal)
            if targetModifier < 1: targetModifier = 1
            bin = hist.GetXaxis().GetBinUpEdge(b)
            widthRequirement = (bin - bins[-1]) > (bins[-1] - bins[-2])/2 if len(bins)>1 else True #don't allow binning to decrease by more than factor of two
            if widthRequirement and (accumulatedError <= targetError*targetModifier or nextError <= targetError*targetModifier):
                accumulatedVal = 0
                if bin not in bins:
                    bins.append(bin)

        elif not foundStart:
            bins.append(hist.GetXaxis().GetBinUpEdge(b))

    if lastBin not in bins and lastBin > bins[-1]: bins.append(lastBin)
    #print hist.GetName(), bins
    return bins
            

#
#   Do variable rebinning for a histogram
#
def do_variable_rebinning(hist,bins,debug=False):
    if debug: print "Doing var rebinnind"
    a=hist.GetXaxis()
    if debug: print "bins are",bins
    newhist=ROOT.TH1F(hist.GetName()+"variableBins_"+str(random.random()),
                      hist.GetTitle()+";"+hist.GetXaxis().GetTitle()+";"+hist.GetYaxis().GetTitle(),
                      len(bins)-1,
                      array('d',bins))
    histErrorOption = hist.GetBinErrorOption()
    newhist.SetBinErrorOption(histErrorOption)
    if not newhist.GetSumw2N(): newhist.Sumw2()
    newa=newhist.GetXaxis()
    if debug: print newa.GetXmin(),"-",newa.GetXmax()
    for b in range(1, hist.GetNbinsX()+1):
        newb=newa.FindBin(a.GetBinCenter(b))
        val=newhist.GetBinContent(newb)
        ratio_bin_widths=newa.GetBinWidth(newb)/a.GetBinWidth(b)
        if abs(ratio_bin_widths - int(ratio_bin_widths*1e6)/1.0e6) > 0.001: 
            print ratio_bin_widths,"NOT INTEGER RATIO OF BIN WITDHS!!!", abs(ratio_bin_widths - int(ratio_bin_widths*1e6)/1.0e6)
            print hist.GetName()
            raw_input()
        val=val+hist.GetBinContent(b)/ratio_bin_widths
        newhist.SetBinContent(newb,val)

        if not histErrorOption:#gaussian error bars
            err=newhist.GetBinError(newb)
            err=math.sqrt(err**2+(hist.GetBinError(b)/ratio_bin_widths)**2)
            newhist.SetBinError(newb,err)
        else: #poisson error bars
            errUp=newhist.GetBinErrorUp(newb)
            errUp=math.sqrt(errUp**2+hist.GetBinErrorUp(b)/ratio_bin_widths*hist.GetBinErrorUp(b)/ratio_bin_widths)
            #newhist.SetBinErrorUp(newb,errUp)
            errLow=newhist.GetBinErrorLow(newb)
            errLow=math.sqrt(errLow**2+(hist.GetBinErrorLow(b)/ratio_bin_widths)**2)
            #newhist.SetBinErrorLow(newb,errLow)

    #if "m4j_l__data" in type(hist): raw_input()

    return (newhist, a.GetBinWidth(1))


#
# DO CHI2 MYSELF BECAUSE ONCE AGAIN... ROOT SUCKS
# 
def pearsonChi2(data,pred,binWidth):
    residuals = []
    ndf = 0
    observed = []
    expected = []
    for bin in range(1,data.GetNbinsX()+1):
        w = data.GetXaxis().GetBinWidth(bin)/binWidth if binWidth else 1
        O = data.GetBinContent(bin)
        observed.append(O)
        E = abs(pred.GetBinContent(bin))
        expected.append(E)
        res = w*(O-E)**2/E if E else 0.0
        residuals.append(res)
        ndf = ndf + 1 if E else ndf

    chi2 = sum(residuals)
    return (chi2, ndf)

#
# calculate dN/N as a function of cut value. For S/root(B) to increase need dS/S>dB/2B
#
def dN_N(hist,signal,direction,rPad, rMin, rMax):
    hist.GetXaxis().SetLabelSize(0)
    h_dN = copy.copy(hist)
    h_dN.SetTitle("")
    h_dN.GetYaxis().SetNdivisions(503)
    h_dN.SetName(h_dN.GetName()+"h_dN")
    h_dN.Reset()
    h_dN.SetMinimum(rMin)
    h_dN.SetMaximum(rMax)
    h_dN.GetYaxis().SetTitleOffset(1.6)
    ROOT.SetOwnership(h_dN, False)#?

    nBins = hist.GetNbinsX()
    if direction != "+" and direction != "-":  centerBin = hist.FindBin(float(direction)) 

    if signal:
        h_dN.SetYTitle("dS/S")
    else:
        h_dN.SetYTitle("dB/2B")

    if   direction == "+": cutRange = range(1,nBins+1)
    elif direction == "-": cutRange = range(1,nBins+1)[::-1]
    else:                  cutRange = range(1,min(nBins-centerBin,centerBin))[::-1]

    for cut in cutRange:
        if   direction == "+": 
            N  = hist.Integral(cut,nBins) 
            dN = hist.GetBinContent(cut) 
        elif direction == "-": 
            N  = hist.Integral(0,cut) 
            dN = hist.GetBinContent(cut) 
        else:                  
            N  = hist.Integral(centerBin-cut,centerBin+cut) 
            dN = hist.GetBinContent(centerBin-cut) + hist.GetBinContent(centerBin+cut) 

        if  N < 0:  N = 0
        if dN < 0: dN = 0

        if signal: 
            if direction == "+" or direction == "-":
                h_dN.SetBinContent(cut,dN/N if N else 0)
                h_dN.SetBinError(cut, 0.00001)
            else:
                h_dN.SetBinContent(centerBin-cut,dN/N if N else 0)
                h_dN.SetBinError(centerBin-cut, 0.00001)
                h_dN.SetBinContent(centerBin+cut,dN/N if N else 0)
                h_dN.SetBinError(centerBin+cut, 0.00001)
        else:
            if direction == "+" or direction == "-":
                h_dN.SetBinContent(cut,dN/(2*N) if N else 0)
                h_dN.SetBinError(cut, 0.00001)
            else:
                h_dN.SetBinContent(centerBin-cut,dN/(2*N) if N else 0)
                h_dN.SetBinError(centerBin-cut, 0.00001)
                h_dN.SetBinContent(centerBin+cut,dN/(2*N) if N else 0)
                h_dN.SetBinError(centerBin+cut, 0.00001)
            

    setStyle(h_dN)
    h_dN.GetYaxis().SetLabelOffset(0.02)
    #h_dN.LabelsDeflate("X")
    #h_dN.LabelsOption("d","X")

    rPad.cd()
    if signal:
        h_dN.Draw("SAME PE Y+")
    else:
        h_dN.Draw("SAME PE Y-")

        


#
#  Helper function for parsing txt files with model parameters
#
def read_parameter_file(inFileName):
    inFile = open(inFileName,"r")
    outputDict = {}

    for line in inFile:
        words =  line.split()
        
        if not len(words): continue

        if not len(words) == 2: 
            print "Cannot parse",line
            continue

        try:
            outputDict[words[0]] = float(words[1])
        except ValueError:
            outputDict[words[0]] = words[1]
    return outputDict


def setStyle(h,ratio=False,plotParameters={}):
    ratioOnly = plotParameters.get("ratioOnly", False)
    logX      = plotParameters.get("logX",      False)
    h.SetLineWidth(2)
    ROOT.gPad.SetTicks(1,1)
    ROOT.gPad.Update()
    
    if h.InheritsFrom("TH1"): 
        h.GetXaxis().SetTitleOffset(3.0)
    if h.InheritsFrom("TH2"): 
        h.GetZaxis().SetLabelOffset(0.01)
        h.GetZaxis().SetLabelSize(plotParameters.get("labelSize", 0.032))
        #h.GetZaxis().SetExponentOffset(0.01,0.01)

    h.GetXaxis().SetLabelSize(plotParameters.get("labelSize", 18))
    h.GetYaxis().SetLabelSize(plotParameters.get("labelSize", 18))

    h.GetXaxis().SetLabelFont(43)
    h.GetXaxis().SetTitleFont(43)

    if ratio and not ratioOnly:
        h.GetXaxis().SetLabelSize(0)
        h.GetXaxis().SetTitleSize(0)
        h.GetXaxis().SetLabelOffset(0.013)
        h.GetYaxis().SetTitleOffset(1.15)
    else:
        if h.InheritsFrom("TH1"): 
            h.GetXaxis().SetTitleSize(21)
            #h.GetXaxis().SetTitleOffset(0.90)
        h.GetYaxis().SetTitleOffset(0.90)

    h.GetYaxis().SetLabelFont(43)
    h.GetYaxis().SetTitleFont(43)
    h.GetYaxis().SetTitleSize(25)
    if h.InheritsFrom("TH2"): 
        h.GetXaxis().SetTitleSize(26)
        h.GetXaxis().SetTitleOffset(1)
        h.GetYaxis().SetTitleSize(25)
        h.GetYaxis().SetTitleOffset(1.1)

    h.SetTitleFont(43)

    if "xTitleOffset" in plotParameters: h.GetXaxis().SetTitleOffset(plotParameters["xTitleOffset"])
    if "yTitleOffset" in plotParameters: h.GetYaxis().SetTitleOffset(plotParameters["yTitleOffset"])
    if "zTitleOffset" in plotParameters: h.GetZaxis().SetTitleOffset(plotParameters["zTitleOffset"])

    if "yTickLength" in plotParameters: h.GetYaxis().SetTickLength(plotParameters["yTickLength"])
    
    
def SetYaxisRange(histList,yMax,yMin,logY,ratio, debug=False):
    if yMax != None and yMin != None:
        minimum = float(yMin)
        maximum = float(yMax)
        if debug: print "Manually setting range:",minimum,maximum
    elif yMax != None:
        maximum = float(yMax)
        minimum = max([hist.GetMinimum() for hist in histList])
        minimum = (abs(minimum/2) if logY else 0)
    elif yMin != None:
        minimum = float(yMin)
        maximum = max([hist.GetMaximum() for hist in histList])
        maximum = maximum*(20.0 if logY  else 1.3)
        maximum = maximum*(1.2  if ratio else 1.0)
    else:
        if debug: print histList, [hist.GetMaximum() for hist in histList]
        maximum = max([hist.GetMaximum() for hist in histList])
        maximum = maximum*(20.0 if logY  else 1.1)
        maximum = maximum*(1.1  if ratio else 1.0)
        minimum = max([hist.GetMinimum() for hist in histList])
        minimum = (abs(minimum/2) if logY else 0)
    if not minimum and logY:
        minimum = 0.05

    for hist in histList:
        if hist.InheritsFrom("TH2"): continue
        hist.SetMaximum(maximum)
        hist.SetMinimum(minimum)


def divideByBinWidth(hist,plotParameters):
    a=hist.GetXaxis()

    #find smallest bin
    s=1e8
    for b in range(1, hist.GetNbinsX()+1):
        w=a.GetBinWidth(b)
        if w<s: s=w
        
    #normalize to smallest width bin
    for b in range(1, hist.GetNbinsX()+1):
        w=a.GetBinWidth(b)
        c=hist.GetBinContent(b)
        e=hist.GetBinError(b)
        hist.SetBinContent(b,c*s/w)
        hist.SetBinError(b,e*s/w)

    w = s

    # #find largest bin
    # l=0
    # for b in range(1, hist.GetNbinsX()+1):
    #     w=a.GetBinWidth(b)
    #     if w>l: l=w
        
    # #normalize to largest width bin
    # for b in range(1, hist.GetNbinsX()+1):
    #     w=a.GetBinWidth(b)
    #     c=hist.GetBinContent(b)
    #     e=hist.GetBinError(b)
    #     hist.SetBinContent(b,c*l/w)
    #     hist.SetBinError(b,e*l/w)

    # w = l

    if plotParameters["yTitle"] != "Arb. Units":
        hist.GetYaxis().SetTitle("Events / "+str(int(w))+" GeV")
    else:
        hist.GetYaxis().SetTitle("Arb. Units / "+str(int(w))+" GeV")
    
        

