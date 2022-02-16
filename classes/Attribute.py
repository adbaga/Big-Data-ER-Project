class Attribute:
    #name:string : name of the attribute
    #Entity: String: from which entity this attribute is
    #edge (list) : to which attribute in other entity it is pointing to
    def __init__(self, name : str, entity : str, edges : list): 
        
        self.attName = name
        self.visited = False
        self.entity = entity
        self.edges = edges

    def attribute_traverse(self):
        pass