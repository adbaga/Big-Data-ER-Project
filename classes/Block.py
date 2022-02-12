class Block:
    def __init__(self, b_name, ep_E1, ep_E2):  
        self.b_name = b_name
        self.ib1 = ep_E1
        self.ib2 = ep_E2
        self.b_cardinality = len(ep_E1)*len(ep_E1)
        self.b_size = len(ep_E1) + len(ep_E2)