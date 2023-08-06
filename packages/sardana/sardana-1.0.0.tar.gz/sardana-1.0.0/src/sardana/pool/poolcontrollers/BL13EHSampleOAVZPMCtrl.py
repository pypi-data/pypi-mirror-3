from sardana import pool
from sardana.pool import PoolUtil
from sardana.pool.controller import PseudoMotorController
import math

class BL13EHSampleOAVZController(PseudoMotorController):
    """ This controller provides the sample OAV Z pseudomotor as a function of centx,centy."""

    pseudo_motor_roles = ('sampleoavz',)
    motor_roles = ('centx','centy')

    def __init__(self, inst, props, *args, **kwargs):
        PseudoMotorController.__init__(self, inst, props, *args, **kwargs)

    def CalcPhysical(self, index, pseudos, curr_physicals):
        sampleoavz, = pseudos
        #omega = (math.pi/180.)*taurus.Device('omega').position
        omega = (math.pi/180.)*PoolUtil().get_device(self.GetName(), 'mot03').position
        if index == 1:
            return sampleoavz*math.sin(-1.*omega) 
        if index == 2:
            return sampleoavz*math.cos(-1.*omega) 

    def CalcPseudo(self, index, physicals, curr_pseudos):
        centx, centy = physicals
        #omega = (math.pi/180.)*taurus.Device('omega').position
        omega = (math.pi/180.)*PoolUtil().get_device(self.GetName(), 'mot03').position
        return centx*math.sin(-1.*omega)+centy*math.cos(-1.*omega)
