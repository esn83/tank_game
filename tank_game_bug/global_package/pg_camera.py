import pygame as pg

class Camera:
    
    def __init__(self,
                 display_area_p,                    # tuple (x,y,w,h), area on the screen where the 'map' is displayed
                 world_surf_p,                      # surface
                 start_pos_p=(0,0),                 # tuple (x,y)
                 enable_mouse_edge_scroll_p=True,   # bool
                 enable_right_mouse_pan_p=False,    # bool
                 enable_zoom_p=True,                # bool
                 enable_smoothness_p=True,          # bool
                 zoom_scale_p=1,                    # zoom scale, larger means zoomed in, smaller means zoomed out
                 zoom_scale_min_p=0.4,              # min zoom scale
                 zoom_scale_max_p=3,                # max zoom scale
                 zoom_step_p=0.1,                   # increase/decrease of zoom_scale pr zoom step
                 ):

        self.display_area = display_area_p
        self.world_surf = world_surf_p
        self.world_rect = self.world_surf.get_rect()
        self.enable_mouse_edge_scroll = enable_mouse_edge_scroll_p
        self.enable_right_mouse_pan = enable_right_mouse_pan_p
        self.enable_zoom = enable_zoom_p
        self.enable_smoothness = enable_smoothness_p
        self.zoom_scale = zoom_scale_p
        self.zoom_scale_min = zoom_scale_min_p
        self.zoom_scale_max = zoom_scale_max_p
        self.zoom_step = zoom_step_p

        self.display_x = self.display_area[0]
        self.display_y = self.display_area[1]
        self.display_width = self.display_area[2]
        self.display_height = self.display_area[3]
        self.display_rect = pg.Rect(display_area_p)
        self.scaled_width = self.display_width*self.zoom_scale
        self.scaled_height = self.display_height*self.zoom_scale

        self.right_mouse_camera_pan_active = False # if true center mouse on screen, used for move screen with mouse
        self.scroll_speed = int(self.display_width*0.005) # set scroll speed to a % of map width

        self.camera_sub_surf_rect = pg.Rect(start_pos_p[0], # this rect will move within the world_rect and what is inside this rect will be scaled and drawn to screen
                                            start_pos_p[1],
                                            self.scaled_width,
                                            self.scaled_height)

        self.camera_sub_surf_rect_sz = self.camera_sub_surf_rect.copy() # smooth zoom rect. this rect will slowly follow the camera_sub_surf_rect for a smooth zoom effect
        self.camera_sub_surf_rect_aspect_ratio = self.camera_sub_surf_rect.height/self.camera_sub_surf_rect.width
        self.smooth_zoom_tuning = 15 # this determines how fast the smooth zoom rect size will scale to the target rect size. the larger the number the slower the scaling.

    def events(self, event):

        if event.type == pg.MOUSEWHEEL: # zoom in/out
            
            if self.display_rect.collidepoint(self.mouse_pos):
                if event.y == 1:
                    if self.enable_zoom:
                        if self.zoom_scale - self.zoom_step >= self.zoom_scale_min:
                            self.zoom_scale -= self.zoom_step
                            self.scaled_width = self.display_width*self.zoom_scale
                            self.scaled_height = self.display_height*self.zoom_scale
                elif event.y == -1:
                    if self.enable_zoom:
                        if self.zoom_scale + self.zoom_step <= self.zoom_scale_max:
                            self.zoom_scale += self.zoom_step
                            self.scaled_width = self.display_width*self.zoom_scale
                            self.scaled_height = self.display_height*self.zoom_scale

                        if self.scaled_width > self.world_rect.width or self.scaled_height > self.world_rect.height: # this makes sure the scaled rect is smaller than or equal to world_rect size
                            self.zoom_scale -= self.zoom_step
                            self.scaled_width = self.display_width*self.zoom_scale
                            self.scaled_height = self.display_height*self.zoom_scale
                
                if self.enable_zoom:                                
                    self.camera_sub_surf_rect.inflate_ip(self.scaled_width-self.camera_sub_surf_rect.width, self.scaled_height-self.camera_sub_surf_rect.height) # scale sub_surf_rect and keep centre

        if event.type == pg.MOUSEBUTTONUP:

            if event.button == 3: # right mouse up
                # disable right mouse screen pan
                if self.enable_right_mouse_pan:
                    if self.right_mouse_camera_pan_active == True:
                        self.right_mouse_camera_pan_active = False
                        pg.mouse.set_pos(self.mouse_pos_old)
                        pg.mouse.set_visible(True)

        if event.type == pg.MOUSEBUTTONDOWN:

            if event.button == 3: # right mouse down
                # enable right mouse screen pan
                if self.enable_right_mouse_pan and self.display_rect.collidepoint(self.mouse_pos):
                    if not self.right_mouse_camera_pan_active:
                        self.right_mouse_camera_pan_active = True
                        self.mouse_pos_old = pg.mouse.get_pos()
                        pg.mouse.set_visible(False)
                        pg.mouse.set_pos(self.display_x+self.display_width/2, self.display_y+self.display_height/2)
    
    def move_camera_to_target(self, target):
        self.camera_sub_surf_rect.center = target
        self.camera_sub_surf_rect_sz.center = target

    def get_world_pos_to_screen(self, pos):
        pos_screen_x = (pos[0] - self.camera_surf.get_offset()[0]) / self.zoom_scale
        pos_screen_y = (pos[1] - self.camera_surf.get_offset()[1]) / self.zoom_scale
        return(pos_screen_x, pos_screen_y)

    def get_mouse_screen_to_world(self): # get the world coordinates (eg. 4000x4000 area) of screen mouse pos (eg. 800x600 area)
        mouse_pos_screen = self.mouse_pos
        mouse_pos_world_x = (mouse_pos_screen[0]-self.display_x) * self.zoom_scale + self.camera_surf.get_offset()[0]
        mouse_pos_world_y = (mouse_pos_screen[1]-self.display_y) * self.zoom_scale + self.camera_surf.get_offset()[1]
        return (mouse_pos_world_x,mouse_pos_world_y)

    # this function is used in the general draw step.
    # only draw objects which rects collide with the camera_sub_surf_rect as it is only objects within this rect that is displayed on screen anyway
    # i don't know which is more efficient ; just drawing everything or checking colliderect for everything to filter out and draw only what is on screen?
    def is_rect_in_view(self, rect):
        if rect.colliderect(self.camera_sub_surf_rect_sz):
            return True
        else:
            return False

    def smooth_zoom(self):
        camera_sub_surf_rect_sz_center_old = self.camera_sub_surf_rect_sz.center # keep rect center after scaling smooth zoom rect rect
        if self.camera_sub_surf_rect_sz.width < self.camera_sub_surf_rect.width: # gradually grow the smooth zoom rect camera_sub_surf_rect_sz to fit the sub_surf_rect
            self.camera_sub_surf_rect_sz.width += 1 + (self.camera_sub_surf_rect.width - self.camera_sub_surf_rect_sz.width) / self.smooth_zoom_tuning
            self.camera_sub_surf_rect_sz.height = self.camera_sub_surf_rect_sz.width * self.camera_sub_surf_rect_aspect_ratio

        elif self.camera_sub_surf_rect_sz.width > self.camera_sub_surf_rect.width: # gradually shrink the smooth zoom rect camera_sub_surf_rect_sz to fit the sub_surf_rect
            self.camera_sub_surf_rect_sz.width -= 1 - (self.camera_sub_surf_rect.width - self.camera_sub_surf_rect_sz.width) / self.smooth_zoom_tuning
            self.camera_sub_surf_rect_sz.height = self.camera_sub_surf_rect_sz.width * self.camera_sub_surf_rect_aspect_ratio
        self.camera_sub_surf_rect_sz.center = camera_sub_surf_rect_sz_center_old

        # gradually allign the centres of the smooth zoom rect camera_sub_surf_rect_sz and the the sub_surf_rect
        if self.camera_sub_surf_rect_sz.center[0] < self.camera_sub_surf_rect.center[0]:
            self.camera_sub_surf_rect_sz.x += 1 + (self.camera_sub_surf_rect.center[0] - self.camera_sub_surf_rect_sz.center[0]) / self.smooth_zoom_tuning * 3
        elif self.camera_sub_surf_rect_sz.center[0] > self.camera_sub_surf_rect.center[0]:
            self.camera_sub_surf_rect_sz.x -= 1 - (self.camera_sub_surf_rect.center[0] - self.camera_sub_surf_rect_sz.center[0]) / self.smooth_zoom_tuning * 3
        
        if self.camera_sub_surf_rect_sz.center[1] < self.camera_sub_surf_rect.center[1]:
            self.camera_sub_surf_rect_sz.y += 1 + (self.camera_sub_surf_rect.center[1] - self.camera_sub_surf_rect_sz.center[1]) / self.smooth_zoom_tuning * 3
        elif self.camera_sub_surf_rect_sz.center[1] > self.camera_sub_surf_rect.center[1]:
            self.camera_sub_surf_rect_sz.y -= 1 - (self.camera_sub_surf_rect.center[1] - self.camera_sub_surf_rect_sz.center[1]) / self.smooth_zoom_tuning * 3

        self.camera_sub_surf_rect_sz.clamp_ip(self.world_rect) # this makes sure the camera_sub_surf_rect_sz is within world_rect

    def update(self, target=None):
        self.mouse_pos = pg.mouse.get_pos()
        
        if target != None and not self.right_mouse_camera_pan_active: # if camera needs to follow a target ie. unit
            self.move_camera_to_target(target)
        
        elif self.right_mouse_camera_pan_active:
            # clamp mouse within self.display_rect while panning
            mouse_pos_rect = pg.Rect(self.mouse_pos[0],self.mouse_pos[1],1,1)
            if not mouse_pos_rect.colliderect(self.display_rect):
                mouse_pos_rect.clamp_ip(self.display_rect)
                pg.mouse.set_pos(mouse_pos_rect.x,mouse_pos_rect.y)
            # move camera_sub_surf_rect with mouse pan
            if abs(self.camera_sub_surf_rect.center[0] - self.get_mouse_screen_to_world()[0]) > 10 or abs(self.camera_sub_surf_rect.center[1] - self.get_mouse_screen_to_world()[1]) > 10:
                self.camera_sub_surf_rect.center = self.get_mouse_screen_to_world()
        
        else:
            if self.enable_mouse_edge_scroll: # mouse edge scroll enabled
                if self.display_rect.collidepoint(self.mouse_pos):
                    # x movement
                    if self.mouse_pos[0] < self.display_x + self.display_width * 0.1:
                        self.camera_sub_surf_rect.x -= self.scroll_speed
                    elif self.mouse_pos[0] > self.display_x + self.display_width * 0.9:
                        self.camera_sub_surf_rect.x += self.scroll_speed
                    # y movement
                    if self.mouse_pos[1] < self.display_y + self.display_height * 0.1:
                        self.camera_sub_surf_rect.y -= self.scroll_speed
                    elif self.mouse_pos[1] > self.display_y + self.display_height * 0.9:
                        self.camera_sub_surf_rect.y += self.scroll_speed

        self.camera_sub_surf_rect.clamp_ip(self.world_rect) # make sure self.camera_sub_surf_rect is within self.world_rect

        if self.enable_smoothness:
            self.smooth_zoom()
        else:
            self.camera_sub_surf_rect_sz = self.camera_sub_surf_rect.copy() # bypass smooth_zoom
        
        self.camera_surf = self.world_surf.subsurface(self.camera_sub_surf_rect_sz)
        self.scaled_camera_surf = pg.transform.scale(self.camera_surf,(self.display_width,self.display_height))         # scale
        #self.scaled_camera_surf = pg.transform.smoothscale(self.camera_surf,(self.display_width,self.display_height))  # smooth scale
        self.scaled_camera_rect = self.scaled_camera_surf.get_rect()
        self.scaled_camera_rect.x = self.display_x
        self.scaled_camera_rect.y = self.display_y

    def draw(self, surface, interpolate):
        # blit the scaled camera subsurface to the screen surface
        surface.blit(self.scaled_camera_surf, self.scaled_camera_rect)