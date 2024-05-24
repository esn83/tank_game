import pygame as pg

class MapObstacle:

    def __init__(self,
                 scale_p,
                 pos_x_p,
                 pos_y_p,
                 frames_p
                 ):
        
        self.scale = scale_p
        self.pos = pg.Vector2(pos_x_p,pos_y_p)
        self.frames = []
        
        for frame in frames_p:
            frame = pg.transform.scale(frame, (frame.get_width()*self.scale, frame.get_height()*self.scale))
            frame = frame.convert_alpha()
            self.frames.append(frame)
        
        self.surf = self.frames[0]
        self.rect = self.surf.get_rect()
        self.rect.bottomleft = self.pos

    def update(self, dt):
        pass

    def draw(self, surface, interpolate):
        surface.blit(self.surf,self.rect)

    def get_center_y(self):
        return self.rect.center[1]