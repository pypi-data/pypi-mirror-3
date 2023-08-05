"""
<name>Merge Data</name>
<description>Merge datasets based on values of selected attributes.</description>
<icon>icons/MergeData.png</icon>
<priority>1110</priority>
<contact>Peter Juvan (peter.juvan@fri.uni-lj.si)</contact>
"""
import orange
from OWWidget import *
import OWGUI

class OWMergeData(OWWidget):

#    settingsList = ["varA", "varB"]

    contextHandlers = {"A": DomainContextHandler("A", [ContextField("varA")], syncWithGlobal=False),
                       "B": DomainContextHandler("B", [ContextField("varB")], syncWithGlobal=False)}                                            

    def __init__(self, parent = None, signalManager = None, name = "Merge data"):
        OWWidget.__init__(self, parent, signalManager, name, wantMainArea = 0)  #initialize base class

        # set channels
        self.inputs = [("Examples A", ExampleTable, self.onDataAInput), ("Examples B", ExampleTable, self.onDataBInput)]
        self.outputs = [("Merged Examples A+B", ExampleTable), ("Merged Examples B+A", ExampleTable)]

        # data
        self.dataA = None
        self.dataB = None
        self.varListA = []
        self.varListB = []
        self.varA = None
        self.varB = None
        self.lbAttrAItems = []
        self.lbAttrBItems = []

        # load settings
        self.loadSettings()

        # GUI
        w = QWidget(self)
        self.controlArea.layout().addWidget(w)
        grid = QGridLayout()
        grid.setMargin(0)
        w.setLayout(grid)

        # attribute A
        boxAttrA = OWGUI.widgetBox(self, 'Attribute A', orientation = "vertical", addToLayout=0)
        grid.addWidget(boxAttrA, 0,0)
        self.lbAttrA = OWGUI.listBox(boxAttrA, self, "lbAttrAItems", callback = self.lbAttrAChange)

        # attribute  B
        boxAttrB = OWGUI.widgetBox(self, 'Attribute B', orientation = "vertical", addToLayout=0)
        grid.addWidget(boxAttrB, 0,1)
        self.lbAttrB = OWGUI.listBox(boxAttrB, self, "lbAttrBItems", callback = self.lbAttrBChange)

        # info A
        boxDataA = OWGUI.widgetBox(self, 'Data A', orientation = "vertical", addToLayout=0)
        grid.addWidget(boxDataA, 1,0)
        self.lblDataAExamples = OWGUI.widgetLabel(boxDataA, "num examples")
        self.lblDataAAttributes = OWGUI.widgetLabel(boxDataA, "num attributes")

        # info B
        boxDataB = OWGUI.widgetBox(self, 'Data B', orientation = "vertical", addToLayout=0)
        grid.addWidget(boxDataB, 1,1)
        self.lblDataBExamples = OWGUI.widgetLabel(boxDataB, "num examples")
        self.lblDataBAttributes = OWGUI.widgetLabel(boxDataB, "num attributes")

        # icons
        self.icons = self.createAttributeIconDict()

        # resize
        self.resize(400,500)


    ############################################################################################################################################################
    ## Data input and output management
    ############################################################################################################################################################

    def inVarList(self, varList, var):
        if var in varList:
            return True, varList.index(var)
        elif var and var.varType == orange.Variable.String and var.name in [v.name for v in varList]:
            return True, [v.name for v in varList].index(var.name)
        elif var and (var.name, var.varType) in [(v.name, v.varType) for v in varList]:
            return True, [(v.name, v.varType) for v in varList].index((var.name, var.varType))
        else:
            return False, -1
        
        
    def onDataAInput(self, data):
        self.closeContext("A")
        # set self.dataA, generate new domain if it is the same as of self.dataB.domain
#        if data and self.dataB and data.domain == self.dataB.domain:
#            if data.domain.classVar:
#                classVar = data.domain.classVar.clone()
#            else:
#                classVar = None
#            dc = orange.Domain([x.clone() for x in data.domain], classVar)
#            for i, a in enumerate(dc):
#                a.getValueFrom = lambda ex,f,i=i: ex[i]
##             no need to clone meta attributes: dc.addmetas(dict([(orange.newmetaid(), x.clone()) for x in data.domain.getmetas().values()])); for i,id,a in enumerate(dc.getmetas().items()): ...
#            dc.addmetas(data.domain.getmetas())
#            self.dataA = orange.ExampleTable(dc, data)
#            self.dataA = data
#        else:
#            self.dataA = data
        self.dataA = data
        # update self.varListA and self.varA
        if self.dataA:
            self.varListA = list(self.dataA.domain.variables) + self.dataA.domain.getmetas().values()
        else:
            self.varListA = []
#        if not self.varA in self.varListA:
#            self.varA = None
        # update info
        self.updateInfoA()
        # update attribute A listbox
        self.lbAttrA.clear()
        for var in self.varListA:
            self.lbAttrA.addItem(QListWidgetItem(self.icons[var.varType], var.name))
        if self.dataA:
            self.openContext("A", self.dataA)
        match, index = self.inVarList(self.varListA, self.varA)
        if match:
            self.varA = self.varListA[index]
            self.lbAttrA.setCurrentItem(self.lbAttrA.item(index))
    #        elif self.dataA:
    #            self.varA = None
        self.sendData()

    def onDataBInput(self, data):
        # set self.dataB, generate new domain if it is the same as of self.dataA.domain
        self.closeContext("B")
#        if data and self.dataA and data.domain == self.dataA.domain:
#            if data.domain.classVar:
#                classVar = data.domain.classVar.clone()
#            else:
#                classVar = None
#            dc = orange.Domain([x.clone() for x in data.domain.attributes], classVar)
#            for i, a in enumerate(dc):
#                a.getValueFrom = lambda ex,f,i=i: ex[i]
#            # no need to clone meta attributes: dc.addmetas(dict([(orange.newmetaid(), x.clone()) for x in data.domain.getmetas().values()])); for i,id,a in enumerate(dc.getmetas().items()): ...
#            dc.addmetas(data.domain.getmetas())
#            self.dataB = orange.ExampleTable(dc, data)
#            self.dataB = data
#        else:
#            self.dataB = data
        self.dataB = data
        # update self.varListB and self.varB
        if self.dataB:
            self.varListB = list(self.dataB.domain.variables) + self.dataB.domain.getmetas().values()
        else:
            self.varListB = []
#        if not self.varB in self.varListB:
#            self.varB = None
        # update info
        self.updateInfoB()
        # update attribute B listbox
        self.lbAttrB.clear()
        for var in self.varListB:
            self.lbAttrB.addItem(QListWidgetItem(self.icons[var.varType], var.name))
        
        if self.dataB:
            self.openContext("B", self.dataB)
        match, index = self.inVarList(self.varListB, self.varB)
        if match:
            self.varB = self.varListB[index]
            self.lbAttrB.setCurrentItem(self.lbAttrB.item(index))
#        elif self.dataB:
#            self.varB = None
            
        self.sendData()


    def updateInfoA(self):
        """Updates data A info box.
        """
        if self.dataA:
            self.lblDataAExamples.setText("%s example%s" % self._sp(self.dataA))
            self.lblDataAAttributes.setText("%s attribute%s" % self._sp(self.varListA))
        else:
            self.lblDataAExamples.setText("No data on input A.")
            self.lblDataAAttributes.setText("")


    def updateInfoB(self):
        """Updates data B info box.
        """
        if self.dataB:
            self.lblDataBExamples.setText("%s example%s" % self._sp(self.dataB))
            self.lblDataBAttributes.setText("%s attribute%s" % self._sp(self.varListB))
        else:
            self.lblDataBExamples.setText("No data on input B.")
            self.lblDataBAttributes.setText("")


#    def sendData(self):
#        """Sends out data.
#        """
#        if self.varA and self.varB and self.dataA and self.dataB:
#            # create dictionaries: attribute values -> example index
#            val2idxDictA = {}
#            for eIdx, e in enumerate(self.dataA):
#                val2idxDictA[e[self.varA].native()] = eIdx
#            val2idxDictB = {}
#            for eIdx, e in enumerate(self.dataB):
#                val2idxDictB[e[self.varB].native()] = eIdx
#            # remove DC and DK from dictionaries (change when bug 62 is fixed)
###            if val2idxDictA.has_key(orange.Value(self.varA.varType, orange.ValueTypes.DC).native()):
###                val2idxDictA.pop(orange.Value(self.varA.varType, orange.ValueTypes.DC).native())
###            if val2idxDictA.has_key(orange.Value(self.varA.varType, orange.ValueTypes.DK).native()):
###                val2idxDictA.pop(orange.Value(self.varA.varType, orange.ValueTypes.DK).native())
###            if val2idxDictB.has_key(orange.Value(self.varB.varType, orange.ValueTypes.DC).native()):
###                val2idxDictB.pop(orange.Value(self.varB.varType, orange.ValueTypes.DC).native())
###            if val2idxDictB.has_key(orange.Value(self.varB.varType, orange.ValueTypes.DK).native()):
###                val2idxDictB.pop(orange.Value(self.varB.varType, orange.ValueTypes.DK).native())
#            if val2idxDictA.has_key("?"):
#                val2idxDictA.pop("?")
#            if val2idxDictA.has_key("~"):
#                val2idxDictA.pop("~")
#            if val2idxDictA.has_key(""):
#                val2idxDictA.pop("")
#            if val2idxDictB.has_key("?"):
#                val2idxDictB.pop("?")
#            if val2idxDictB.has_key("~"):
#                val2idxDictB.pop("~")
#            if val2idxDictB.has_key(""):
#                val2idxDictB.pop("")
#            # example table names
#            nameA = self.dataA.name
#            if not nameA: nameA = "Examples A"
#            nameB = self.dataB.name
#            if not nameB: nameB = "Examples B"
#            # create example B with all values unknown
#            exBDK = orange.Example(self.dataB[0])
#            for var in self.varListB:
###                exBDK[var] = orange.Value(var.varType, orange.ValueTypes.DK)
#                exBDK[var] = "?"
#            # build example table to append to the right of A
#            vlBreduced = list(self.varListB)
#            vlBreduced.remove(self.varB)
#            domBreduced = orange.Domain(vlBreduced, None)
#            etBreduced = orange.ExampleTable(domBreduced)
#            for e in self.dataA:
#                dataBidx = val2idxDictB.get(e[self.varA].native(), None)
#                if dataBidx <> None:
#                    etBreduced.append(self.dataB[dataBidx])
#                else:
#                    etBreduced.append(orange.Example(domBreduced, exBDK))
#            etAB = orange.ExampleTable([self.dataA, etBreduced])
#            etAB.name = "%(nameA)s (merged with %(nameB)s)" % vars()
#            self.send("Merged Examples A+B", etAB)
#
#            # create example A with all values unknown
#            exADK = orange.Example(self.dataA[0])
#            for var in self.varListA:
###                exADK[var] = orange.Value(var.varType, orange.ValueTypes.DK)
#                exADK[var] = "?"
#            # build example table to append to the right of B
#            vlAreduced = list(self.varListA)
#            vlAreduced.remove(self.varA)
#            domAreduced = orange.Domain(vlAreduced, None)
#            etAreduced = orange.ExampleTable(domAreduced)
#            for e in self.dataB:
#                dataAidx = val2idxDictA.get(e[self.varB].native(), None)
#                if dataAidx <> None:
#                    etAreduced.append(self.dataA[dataAidx])
#                else:
#                    etAreduced.append(orange.Example(domAreduced, exADK))
#            etBA = orange.ExampleTable([self.dataB, etAreduced])
#            etBA.name = nameB + " (merged with %s)" % nameA
#            self.send("Merged Examples B+A", etBA)
#        else:
#            self.send("Merged Examples A+B", None)
#            self.send("Merged Examples B+A", None)

    def sendData(self):
        if self.dataA and self.dataB and self.varA and self.varB:
            self.send("Merged Examples A+B", self.merge(self.dataA, self.dataB, self.varA, self.varB))
            self.send("Merged Examples B+A", self.merge(self.dataB, self.dataA, self.varB, self.varA))
        else:
            self.send("Merged Examples A+B", None)
            self.send("Merged Examples B+A", None)

    ############################################################################################################################################################
    ## Event handlers
    ############################################################################################################################################################

    def lbAttrAChange(self):
        if self.dataA:
            if self.lbAttrA.selectedItems() != []:
                ind = self.lbAttrA.row(self.lbAttrA.selectedItems()[0])
                self.varA = self.varListA[ind]
            else:
                self.varA = None
        else:
            self.varA = None
        self.sendData()


    def lbAttrBChange(self):
        if self.dataB:
            if self.lbAttrB.selectedItems() != []:
                ind = self.lbAttrB.row(self.lbAttrB.selectedItems()[0])
                self.varB = self.varListB[ind]
            else:
                self.varB = None
        else:
            self.varB = None
        self.sendData()


    ############################################################################################################################################################
    ## Utility functions
    ############################################################################################################################################################

    def _sp(self, l, capitalize=True):
        """Input: list; returns tupple (str(len(l)), "s"/"")
        """
        n = len(l)
        if n == 0:
            if capitalize:
                return "No", "s"
            else:
                return "no", "s"
        elif n == 1:
            return str(n), ''
        else:
            return str(n), 's'

    def merge(self, dataA, dataB, varA, varB):
        """ Merge two tables
        """
        
        val2idx = dict([(e[varB].native(), i) for i, e in reversed(list(enumerate(dataB)))])
        
        for key in ["?", "~", ""]:
            if key in val2idx:
                val2idx.pop(key)
                 
        metasA = dataA.domain.getmetas().items()
        metasB = dataB.domain.getmetas().items()
        
        includedAttsB = [attrB for attrB in dataB.domain if attrB not in dataA.domain]
        includedMetaB = [(mid, meta) for mid, meta in metasB if (mid, meta) not in metasA]
        includedClassVarB = dataB.domain.classVar and dataB.domain.classVar not in dataA.domain
        
        reducedDomainB = orange.Domain(includedAttsB, includedClassVarB)
        reducedDomainB.addmetas(dict(includedMetaB))
        
        
        mergingB = orange.ExampleTable(reducedDomainB)
        
        for ex in dataA:
            ind = val2idx.get(ex[varA].native(), None)
            if ind is not None:
                mergingB.append(orange.Example(reducedDomainB, dataB[ind]))
                
            else:
                mergingB.append(orange.Example(reducedDomainB, ["?"] * len(reducedDomainB)))
                
        return orange.ExampleTable([dataA, mergingB])

    
#    def setVarA(self, var):
#        if var in self.varListA:
#            ind = self.varListA.index(var)
#            self.lbAttrA.setCurrentItem(self.lbAttrA.item(ind))
#        
#    def varA(self):
#        selectedItems = self.lbAttrB.selectedItems()
#        if selectedItems:
#            ind = self.lbAttrB.row(selectedItems[0])
#            return self.varListA[ind]
#        else:
#            return None
#    varA = property(varA, setVarA)
#    
#    def setVarB(self, var):
#        if var in self.varListB:
#            ind = self.varListB.index(var)
#            self.lbAttrB.setCurrentItem(self.lbAttrB.item(ind))
#            
#    def varB(self):
#        selectedItems = self.lbAttrB.selectedItems()
#        if selectedItems:
#            ind = self.lbAttrB.row(selectedItems[0])
#            return self.varListB[ind]
#        else:
#            return None
#    
#    varB = property(varB, setVarB)
    
if __name__=="__main__":
    """
    import sys
    import OWDataTable, orngSignalManager
    signalManager = orngSignalManager.SignalManager(0)
    #data = orange.ExampleTable('dicty_800_genes_from_table07.tab')
##    data = orange.ExampleTable(r'..\..\doc\datasets\adult_sample.tab')
##    dataA = orange.ExampleTable(r'c:\Documents and Settings\peterjuv\My Documents\STEROLTALK\Sterolgene v.0 mouse\sterolgene v.0 mouse probeRatios.tab')
##    dataA = orange.ExampleTable(r'c:\Documents and Settings\peterjuv\My Documents\STEROLTALK\Sterolgene v.0 mouse\Copy of sterolgene v.0 mouse probeRatios.tab')
##    dataB = orange.ExampleTable(r'c:\Documents and Settings\peterjuv\My Documents\STEROLTALK\Sterolgene v.0 mouse\sterolgene v.0 mouse probeRatios.tab')
    dataA = orange.ExampleTable(r'c:\Documents and Settings\peterjuv\My Documents\et1.tab')
    dataB = orange.ExampleTable(r'c:\Documents and Settings\peterjuv\My Documents\et2.tab')
    a=QApplication(sys.argv)
    ow=OWMergeData()
    a.setMainWidget(ow)
    ow.show()
    ow.onDataAInput(dataA)
    ow.onDataBInput(dataB)
    # data table
    dt = OWDataTable.OWDataTable(signalManager = signalManager)
    signalManager.addWidget(ow)
    signalManager.addWidget(dt)
    signalManager.setFreeze(1)
    signalManager.addLink(ow, dt, 'Merged Examples A+B', 'Examples', 1)
    signalManager.addLink(ow, dt, 'Merged Examples B+A', 'Examples', 1)
    signalManager.setFreeze(0)
    dt.show()
    a.exec_()
    """
    import sys
    a=QApplication(sys.argv)
    ow=OWMergeData()
    ow.show()
    data = orange.ExampleTable(r"E:\Development\Orange Datasets\UCI\iris.tab")
    ow.onDataAInput(data)
    a.exec_()
