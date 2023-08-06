#!/usr/bin/env python

# don't forget to place every new macro here!
__all__ = []

__docformat__ = 'restructuredtext'


from sardana.macroserver.macro import macro, Macro, Type

# Place your code here!


@macro()
def test1_macro(self):
    """test1_macro documentation"""
    self.output("test1_macro")

@macro()
def test2_macro(self):
    self.output("test2_macro 2")

@macro([ [ "device", Type.Device, None, "device to be queried"] ])
def devstate(self, device):
    self.output("State of %s is %s", device, device.state())


@macro([ [ "data", Type.JSON, None, "data to be queried"] ])
def mdata(self, data):
    self.output("type: %s, data: %s", type(data), data)

s s 
