# -*- coding: utf-8 -*-



from PyQt4 import QtCore, QtGui
from qkit.storage.hdf_constants import ds_types
try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_Form(object):
    def setupUi(self, Form,ds_type):
        Form.setObjectName(_fromUtf8("Form"))
        Form.resize(750, 450)
        self.gridLayout_Top = QtGui.QGridLayout(Form)
        self.gridLayout_Top.setMargin(0)
        self.gridLayout_Top.setObjectName(_fromUtf8("gridLayout_Top"))
        # we push for a tight layout
        self.gridLayout_Top.setMargin(0);
        self.gridLayout_Top.setContentsMargins(QtCore.QMargins(0,0,0,0));
        self.gridLayout_Top.setSpacing(0);
        
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setSizeConstraint(QtGui.QLayout.SetMinimumSize)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))

        self.horizontalLayout.setMargin(0);
        self.horizontalLayout.setContentsMargins(QtCore.QMargins(0,0,0,0));
        self.horizontalLayout.setSpacing(0);
        

        self.gridLayout_Top.addLayout(self.horizontalLayout, 0, 0, 1, 1)
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        
        self.gridLayout_Top.addLayout(self.gridLayout, 1, 0, 1, 1)

        Form.setWindowTitle(_translate("Form", "Form", None))
        QtCore.QMetaObject.connectSlotsByName(Form)        
        
        if ds_type == ds_types['coordinate']:
            self.setupCoordinate(Form)
        if ds_type == ds_types['vector']:
            self.setupVector(Form)
        if ds_type == ds_types['matrix'] or ds_type == -1:
            self.setupMatrix(Form)
        if ds_type == ds_types['box']:
            self.setupBox(Form)
        if ds_type == ds_types['txt']:
            self.setupTxt(Form)
        if ds_type == ds_types['view']:
            self.setupView(Form)
        
    def setupCoordinate(self,Form):
        self.setupVector(Form)

    def setupVector(self,Form):
        self.PlotTypeSelector = QtGui.QComboBox(Form)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.PlotTypeSelector.sizePolicy().hasHeightForWidth())
        self.PlotTypeSelector.setSizePolicy(sizePolicy)
        self.PlotTypeSelector.setObjectName(_fromUtf8("PlotTypeSelector"))
        self.PlotTypeSelector.addItem(_fromUtf8(""))
        self.PlotTypeSelector.addItem(_fromUtf8(""))
        self.horizontalLayout.addWidget(self.PlotTypeSelector)
        self.PlotTypeSelector.setItemText(0, _translate("Form", "Line Plot", None))
        self.PlotTypeSelector.setItemText(1, _translate("Form", "Table", None))
        
        spacerItem = QtGui.QSpacerItem(40, 1, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self._addIndicatorLabels(Form,sizePolicy,indicators=["PointX","PointY"])
        

    def setupView(self,Form):
        self.TraceSelector = QtGui.QSpinBox(Form)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.TraceSelector.sizePolicy().hasHeightForWidth())
        
        self._addTraceSelectorIndicator(Form,sizePolicy,TraceSelector = "TraceSelector", 
                                        TraceIndicator="TraceValue")

        #The indicators should be located at the most right side of the bar
        spacerItem = QtGui.QSpacerItem(40, 1, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self._addIndicatorLabels(Form,sizePolicy,indicators=["PointX","PointY"])
        

    def setupMatrix(self,Form):
        self.PlotTypeSelector = QtGui.QComboBox(Form)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.PlotTypeSelector.sizePolicy().hasHeightForWidth())
        
        self.PlotTypeSelector.setSizePolicy(sizePolicy)
        self.PlotTypeSelector.setObjectName(_fromUtf8("PlotTypeSelector"))
        self.PlotTypeSelector.addItem(_fromUtf8(""))
        self.PlotTypeSelector.addItem(_fromUtf8(""))
        self.PlotTypeSelector.addItem(_fromUtf8(""))
        self.PlotTypeSelector.setItemText(0, _translate("Form", "Color Plot", None))
        self.PlotTypeSelector.setItemText(1, _translate("Form", "Line Plot", None))
        self.PlotTypeSelector.setItemText(2, _translate("Form", "Table", None))
        
        
        self.PlotTypeLayout = QtGui.QVBoxLayout()
        self.PlotTypeLayout.addWidget(self.PlotTypeSelector)
        # add a empty label to move the PlotTypeSelector to the top
        emptyL = QtGui.QLabel(Form)
        self.PlotTypeLayout.addWidget(emptyL)
        self.horizontalLayout.addLayout(self.PlotTypeLayout,stretch = -10)
        
        self._addTraceSelectorIndicator(Form,sizePolicy,TraceSelector = "TraceSelector",
                                        TraceIndicator="TraceValue")
        
        #The indicators should be located at the most right side of the bar
        spacerItem = QtGui.QSpacerItem(40, 1, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)        
        self._addIndicatorLabels(Form,sizePolicy, indicators=["PointX","PointY","PointZ"])
        
        
    def setupBox(self,Form):
        self.PlotTypeSelector = QtGui.QComboBox(Form)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.PlotTypeSelector.sizePolicy().hasHeightForWidth())
        
        self.PlotTypeSelector.setSizePolicy(sizePolicy)
        self.PlotTypeSelector.setObjectName(_fromUtf8("PlotTypeSelector"))
        self.PlotTypeSelector.addItem(_fromUtf8(""))
        self.PlotTypeSelector.addItem(_fromUtf8(""))
        self.PlotTypeSelector.addItem(_fromUtf8(""))
        self.PlotTypeSelector.addItem(_fromUtf8(""))
        #self.horizontalLayout.addWidget(self.PlotTypeSelector)
        self.PlotTypeSelector.setItemText(0, _translate("Form", "Select X", None))
        self.PlotTypeSelector.setItemText(1, _translate("Form", "Select Y", None))
        self.PlotTypeSelector.setItemText(2, _translate("Form", "Select Z", None))
        self.PlotTypeSelector.setItemText(3, _translate("Form", "Line Plot", None))
        
        self.PlotTypeLayout = QtGui.QVBoxLayout()
        self.PlotTypeLayout.addWidget(self.PlotTypeSelector)
        # add a empty label to move the PlotTypeSelector to the top
        emptyL = QtGui.QLabel(Form)
        self.PlotTypeLayout.addWidget(emptyL)
        self.horizontalLayout.addLayout(self.PlotTypeLayout,stretch = -10)
       
        self._addTraceSelectorIndicator(Form,sizePolicy,TraceSelector = "TraceXSelector", 
                                        TraceIndicator="TraceXValue", prefix = "TraceX: ")
        self._addTraceSelectorIndicator(Form,sizePolicy,TraceSelector = "TraceYSelector", 
                                        TraceIndicator="TraceYValue", prefix = "TraceY: ")
        self._addTraceSelectorIndicator(Form,sizePolicy,TraceSelector = "TraceZSelector",  
                                        TraceIndicator="TraceZValue",  prefix = "TraceZ: ")        

        spacerItem = QtGui.QSpacerItem(40, 1, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        
        self._addIndicatorLabels(Form,sizePolicy,indicators=["PointX","PointY","PointZ"])
        

    def setupTxt(self,Form):
        pass
        #self.setupMatrix()



        
    def _addIndicatorLabels(self,Form,sizePolicy,indicators=[]):
        self.IndicatorLayout = QtGui.QVBoxLayout()
        self.IndicatorLayout.setSizeConstraint(QtGui.QLayout.SetMinimumSize)
        self.IndicatorLayout.setObjectName(_fromUtf8("horizontalLayout"))

        self.IndicatorLayout.setMargin(0);
        self.IndicatorLayout.setContentsMargins(QtCore.QMargins(0,0,0,0));
        self.IndicatorLayout.setSpacing(3);
        
        for indicator in indicators:
            setattr(self,indicator,QtGui.QLabel(Form))
            temp_indicator = getattr(self,indicator)
            temp_indicator.setSizePolicy(sizePolicy)
            temp_indicator.setObjectName(_fromUtf8(indicator))
            self.IndicatorLayout.addWidget(temp_indicator)
            
        self.horizontalLayout.addLayout(self.IndicatorLayout,stretch = -10)


    def _addTraceSelectorIndicator(self,Form,sizePolicy,TraceSelector = "", TraceIndicator="", prefix = "Trace: "):
        self.TraceSelIndLayout = QtGui.QVBoxLayout()
        self.TraceSelIndLayout.setSizeConstraint(QtGui.QLayout.SetMinimumSize)
        self.TraceSelIndLayout.setObjectName(_fromUtf8("TraceSelIndLayout"))

        self.TraceSelIndLayout.setMargin(0);
        self.TraceSelIndLayout.setContentsMargins(QtCore.QMargins(0,0,0,0));
        self.TraceSelIndLayout.setSpacing(1);


        setattr(self,TraceSelector,QtGui.QSpinBox(Form))
        temp_SelInd = getattr(self,TraceSelector)
        temp_SelInd.setSizePolicy(sizePolicy)
        temp_SelInd.setSuffix(_fromUtf8(""))
        temp_SelInd.setMinimum(-99999)
        temp_SelInd.setMaximum(99999)
        temp_SelInd.setProperty("value", -1)
        temp_SelInd.setObjectName(_fromUtf8(TraceSelector))
        temp_SelInd.setPrefix(_translate("Form", prefix , None))

        
        self.TraceSelIndLayout.addWidget(temp_SelInd)
            
        setattr(self,TraceIndicator,QtGui.QLineEdit(Form))
        temp_SelInd = getattr(self,TraceIndicator)
        temp_SelInd.setSizePolicy(sizePolicy)
        temp_SelInd.setReadOnly(False)
        temp_SelInd.setObjectName(_fromUtf8("TraceValue"))
        self.TraceSelIndLayout.addWidget(temp_SelInd)
        self.horizontalLayout.addLayout(self.TraceSelIndLayout,stretch = -10)              