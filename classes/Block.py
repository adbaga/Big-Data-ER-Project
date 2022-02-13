class Block:
    def __init__(self, name, ep_E1, ep_E2): 
        
        self.b_name = name
        self.ib1 = ep_E1
        self.ib2 = ep_E2
        self.b_cardinality = len(ep_E1)*len(ep_E2)
        self.b_size = len(ep_E1) + len(ep_E2)
   

    def as_dict(self):
        return {'block_name': self.b_name, 'int_b1': self.ib1, 'int_b1_size': len(self.ib1), 'int_b2': self.ib2, 'int_b2_size': len(self.ib2), 'b_cardin': self.b_cardinality, 'b_size': self.b_size}