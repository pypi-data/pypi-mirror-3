from sardana.macroserver.macro import Macro, macro, Type

@macro()
def submacros(self):
    """Macro submacros"""
    self.output("Running submacros...")


