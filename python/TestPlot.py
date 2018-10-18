#add path to PlotTools if your plot script is not in PlotTools/python/
#sys.path.insert(0, 'PlotTools/python/')

#import plotting library
import PlotTools

#Use ordered dictionaries (collections library) because they allow you to specify the order in which to draw hists naturally
import collections

###############
## As a first example let's make a super simple plot of two hists and their ratio

#First define the list of samples. Is a dictionary where the key is the file path/name and the 
#value is a dictionary where the keys are TObjects in th file and the values are dictionaris with parameters for the corresponding TObject.
samples=collections.OrderedDict()
samples["RootFiles/TestFile.root"] = collections.OrderedDict()

samples["RootFiles/TestFile.root"]["data_hh_v"] = {"label"    : "Data",
                                                   "ratio"    : "numer A",
                                                   "isData"   : True,
                                                   "color"    : "ROOT.kBlack"}

samples["RootFiles/TestFile.root"]["total_hh_v"] = {"label"    : "Model",
                                                    "ratio"    : "denom A",
                                                    "color"    : "ROOT.kRed"}

#define global plot parameters which are not specific to a given input histogram to the final pdf
parameters = {"ratio"     : True,
              "rTitle"    : "Data / Bkgd",
              "xTitle"    : "m_{HH} [GeV]",
              "yTitle"    : "Events / Bin",
              "outputDir" : "",
              "outputName": "TestPlotSimple",
}

PlotTools.plot(samples, parameters)


###############
## Now spice it up a little

samples=collections.OrderedDict()
samples["RootFiles/TestFile.root"] = collections.OrderedDict()

samples["RootFiles/TestFile.root"]["data_hh_v"] = {"label"    : "Data",
                                                   "ratio"    : "numer A",
                                                   "isData"   : True,
                                                   "color"    : "ROOT.kBlack",
                                                   "legend"   : 1,
                                                   "weight"   : 1}

#add systematic variations in quadrature to guide the eye
systematics = ["_NP0_up","_NP0_down",
               "_NP1_up","_NP1_down",
               "_NP2_up","_NP2_down",
               "_LowHtCRw","_LowHtCRi",
               "_HighHtCRw","_HighHtCRi"]

samples["RootFiles/TestFile.root"]["total_hh_v"] = {"label"    : "Stat+Syst Uncertainty",
                                                    "ratio"    : "denom A",
                                                    "fillColor"    : "ROOT.kGray+2",
                                                    "fillStyle": 3245,
                                                    "lineColor": "ROOT.kWhite",
                                                    "lineStyle": 1,
                                                    "lineWidth": 0,
                                                    "drawOptions": "e2",
                                                    "systematics":["total_hh"+syst+"_v" for syst in systematics],
                                                    "legend"   : 5,
                                                    "legendMark": "f"}

samples["RootFiles/TestFile.root"]["qcd_hh_v"] = {"label"    : "Multijet",
                                                  "stack"    : 2,
                                                  "color"    : "ROOT.kYellow",
                                                  "legend"   : 2}

samples["RootFiles/TestFile.root"]["allhad_hh_v"] = {"label"    : "Hadronic t#bar{t}",
                                                     "stack"    : 1,
                                                     "color"    : "ROOT.kAzure-9",
                                                     "TObject"  : "",
                                                     "legend"   : 3}

samples["RootFiles/TestFile.root"]["nonallhad_hh_v"] = {"label"    : "Semi-leptonic t#bar{t}",
                                                        "stack"    : 0,
                                                        "color"    : "ROOT.kAzure-4",
                                                        "TObject"  : "",
                                                        "legend"   : 4}

samples["RootFiles/TestFile.root"]["smrwMhh_hh_v"] = {"label"    : "SM HH #times100",
                                                      "lineWidth": 3,
                                                      "lineStyle": 2,
                                                      "color"    : "ROOT.kTeal+3",
                                                      "weight"   : 100,
                                                      "legend"   : 7}

samples["RootFiles/TestFile.root"]["g_hh_m800_c10_v"] = {"label"    : "G_{KK} (800 GeV, k/#bar{M}_{Pl}=1)",
                                                         "lineWidth": 3,
                                                         "lineStyle": 3,
                                                         "color"    : "ROOT.kViolet",
                                                         "weight"   : (1.77e+02)/(0.10549*1e3),#updated xs/ami xs                                                             
                                                         "legend"   : 8}

samples["RootFiles/TestFile.root"]["g_hh_m1200_c20_v"] = {"label"    : "G_{KK} (1200 GeV, k/#bar{M}_{Pl}=2)",
                                                          "lineWidth": 3,
                                                          "lineStyle": 9,
                                                          "color"    : "ROOT.kViolet-6",
                                                          "weight"   : (2.24e+01*4)/(0.045461*1e3),#updated xs * c^2/ami xs
                                                          "legend"   : 9}

samples["RootFiles/TestFile.root"]["s_hh_m280_v"] = {"label"    : "Scalar (280 GeV)",
                                                     "lineWidth": 3,
                                                     "lineStyle": 7,
                                                     "color"    : "ROOT.kRed",
                                                     "weight"   : 0.04,
                                                     "legend"   : 6}



parameters = {"ratio"     : True,
              "xLogo"     : 0.20,
              "yLogo"     : 0.85,
              "Logo"      : "#font[42]{#scale[1.4]{#bf{#it{Logo}} Internal}}",
              "Lumi"      : "#font[42]{#sqrt{s}=13 TeV, 24.3 fb^{-1}}",
              "Selection" : "#font[42]{Resolved Signal Region, 2016}",
              "rTitle"    : "Data / Bkgd",
              "xTitle"    : "m_{HH} [GeV]",
              "yTitle"    : "Events / Bin",
              "maxDigits" : 4,
              "errors"    : False,
              "xMin"      : 200,
              "xMax"      : 1479,
              "divideByBinWidth" : True,
              "xleg"      : [0.59, 0.92],
              "yleg"      : [0.35, 0.92],
              "outputDir" : "",
              "outputName": "TestPlot",
              "rMax"      : 1.5,
              "rMin"      : 0.5,
              "logY"      : True,
              "yMax"      : 5e5,
              "yMin"      : 0.5,
}
            
#Make the PDF
PlotTools.plot(samples, parameters)
