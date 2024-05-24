class Player:
    
    def __init__(self,
                 name_p,
                 color_p,
                 controls_p):
        self.name = name_p            # string
        self.color = color_p          # pg.Color
        self.controls = controls_p    # list of keys [pg.K_UP, ...] in order : left, right, up, down, fire