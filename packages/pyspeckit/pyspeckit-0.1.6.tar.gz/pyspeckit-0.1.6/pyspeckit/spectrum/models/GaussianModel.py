from CompositeModel import AdditiveModelComponent

class GaussianModel(AdditiveModelComponent):
    def __init__(self, parameters=(1,0,1), fixed=(False,False,False), parameter_names=('amplitude','offset','width')):
        self.function = None
