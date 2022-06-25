__version__ = '2.4'
__api_version__ = __version__


class Simulator(object):

    meta = None
    
    mosaik = None  # create_sim()

    def __init__(self, meta):
        self.meta = {
            'api_version': __api_version__,
            'models': {},
        }
        self.meta.update(meta)

    def init(self, sid, **sim_params):
        
        return self.meta

    def create(self, num, model, **model_params):
        
        raise NotImplementedError

    def setup_done(self):
        
        pass

    def step(self, time, inputs):
        
        raise NotImplementedError

    def get_data(self, outputs):
        
        raise NotImplementedError

    def finalize(self):
        
        pass

