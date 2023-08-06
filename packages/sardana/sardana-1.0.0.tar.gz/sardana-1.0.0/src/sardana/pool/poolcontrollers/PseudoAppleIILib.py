""" The standard pseudo motor controller library for the device pool """

from sardana.pool.controller import PseudoMotorController
#from pool import PseudoMotorController, PoolUtil

from math import *

class PseudoAppleII(PseudoMotorController):
    """ """
    
    gender = "AppleII"
    model  = "Standard"
    organization = "CELLS - ALBA"
    image = "slit.png"
    logo = "ALBA_logo.png"

    ctrl_extra_attributes = {'Offset':{'Type':'PyTango.DevDouble','R/W Type':'PyTango.READ_WRITE'},
                             'AlwaysZero':{'Type':'PyTango.DevBoolean','R/W Type':'PyTango.READ_WRITE'}}
    
    pseudo_motor_roles = ("GapLeft", "GapRight", "Offset", "Taper")
    motor_roles = ("Z1", "Z2", "Z3", "Z4")
    
   
    def __init__(self,inst,props, *args, **kwargs):
        PseudoMotorController.__init__(self,inst,props, *args, **kwargs)
        self.offsets = {}
        self.AlwaysZero = {}

    def calc_physical(self,index,pseudo_pos):
        
        gap = pseudo_pos[0]
        symmetry = pseudo_pos[1]
        offset = pseudo_pos[2]
        taper = pseudo_pos[3]
        
        Z10 = self.offsets[1]
        Z20 = self.offsets[2]
        Z30 = self.offsets[3]
        Z40 = self.offsets[4]

        #FB for exit of a sw stop
        if self.AlwaysZero[2] == True:
            symmetry = 0.0
        if self.AlwaysZero[3] == True:
            offset = 0.0
        if self.AlwaysZero[4] == True:
            taper = 0.0
        z1 = Z10 + gap/2.0 + offset - taper/4.0 - symmetry/4.0
        z2 = Z20 + gap/2.0 + offset + taper/4.0 + symmetry/4.0
        z3 = Z30 - gap/2.0 + offset - taper/4.0 + symmetry/4.0
        z4 = Z40 - gap/2.0 + offset + taper/4.0 - symmetry/4.0

        #z1 = Z10 + gap/2.0
        #z2 = Z20 + gap/2.0
        #z3 = Z30 - gap/2.0
        #z4 = Z40 - gap/2.0
        
        if index == 1:# z1
            return z1
        if index == 2:# z2
            return z2
        if index == 3:# z3
            return z3
        if index == 4:# z4
            return z4
            
    def calc_pseudo(self,index,physical_pos):
        Z10 = self.offsets[1]
        Z20 = self.offsets[2]
        Z30 = self.offsets[3]
        Z40 = self.offsets[4]
        z1 = physical_pos[0] - Z10
        z2 = physical_pos[1] - Z20
        z3 = physical_pos[2] - Z30
        z4 = physical_pos[3] - Z40
        
        gap = (z1+z2)/2.0 - (z3+z4)/2.0
        symmetry = (z2-z1)+(z3-z4)
        offset = (z1+z2)/4.0 + (z3+z4)/4.0
        taper = (z2-z1)-(z3-z4)
        
        if index == 1:# GAP
            return gap
        if index == 2:# SYMMETRY
            return symmetry
        if index == 3:# OFFSET
            return offset
        if index == 4:# TAPER
            return taper
        
    def GetExtraAttributePar(self,ind,name):
        if name == "Offset":
            return self.offsets[ind]
        elif name == "AlwaysZero":
            return self.AlwaysZero[ind]

    def SetExtraAttributePar(self,ind,name,value):
        try:
            if name == "Offset":
                self.offsets[ind] = value
            elif name == "AlwaysZero":
                self.AlwaysZero[ind] = value
        except Exception,e:
            print "PseudoAppleII Exception"

class PseudoPhaseAppleII(PseudoMotorController):
    """ """
    
    gender = "AppleII"
    model  = "Phase"
    organization = "CELLS - ALBA"
    image = "slit.png"
    logo = "ALBA_logo.png"
    
    ctrl_extra_attributes = {'Offset':{'Type':'PyTango.DevDouble','R/W Type':'PyTango.READ_WRITE'} }

    pseudo_motor_roles = ("Phase", "AntiPhase")
    motor_roles = ("Y1", "Y2")
    
     
    def __init__(self,inst,props, *args, **kwargs):
        PseudoMotorController.__init__(self,inst,props, *args, **kwargs)
        self.offsets = {}

    def calc_physical(self,index,pseudo_pos):
        phase = pseudo_pos[0]
        antiphase = pseudo_pos[1]
        
        #y10 = -700000
        #y20 = 700000
        y10 = self.offsets[1]
        y20 = self.offsets[2]
        y1 = y10 + (phase + antiphase)
        y2 = y20 + (phase - antiphase)
        
        if index == 1:# y1
            return y1
        if index == 2:# y2
            return y2
      
    def calc_pseudo(self,index,physical_pos):
        y10 = self.offsets[1]
        y20 = self.offsets[2]
        y1 = physical_pos[0] - y10
        y2 = physical_pos[1] - y20
        
        phase = (y1+y2)/2.0
        antiphase = (y1-y2)/2.0
        
        if index == 1:# phase
            return phase
        if index == 2:# antiphase
            return antiphase
        
    def GetExtraAttributePar(self,ind,name):
        if name == "Offset":
            return self.offsets[ind]

    def SetExtraAttributePar(self,ind,name,value):
        try:
            if name == "Offset":
                self.offsets[ind] = value
        except Exception,e:
            print "PseudoPhaseAppleII Exception"

