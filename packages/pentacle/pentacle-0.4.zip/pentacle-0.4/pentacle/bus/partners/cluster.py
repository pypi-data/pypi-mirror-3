# Not sure if this should go here: what exactly is it doing?
#    Managing multiple partners on localhost?
#    Providing a network interface to start them up on workstations? (that's spline's job)
from ...services import PentaclePartner

class PartnerCluster(PentaclePartner):
    @classmethod
    def FromConfig(self, cfg):
        return self()

    def __init__(self):
        raise NotImplementedError
