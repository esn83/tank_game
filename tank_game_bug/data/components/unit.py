from ..prepare import global_package_dir
import sys
sys.path.append(global_package_dir)
from pg_tools import get_game_speed_dt_and_loops, scale_image, rotate_image, change_image_color
import pygame as pg
import math

class Unit:

    def __init__(self,
                 scale_p,
                 pos_x_p,
                 pos_y_p,
                 tile_size_p,
                 unit_data_p,
                 player_p = None
                 ):
        
        self.scale = scale_p

        self.pos = pg.Vector2(pos_x_p,pos_y_p)
        self.pos_prev = pg.Vector2(pos_x_p,pos_y_p)
        self.pos_draw = pg.Vector2(pos_x_p,pos_y_p)
        self.pos_draw_prev = pg.Vector2(pos_x_p,pos_y_p)
        self.pos_interpolated = pg.Vector2(pos_x_p,pos_y_p)

        self.tile_size = tile_size_p

        # unit data
        self.image_base = unit_data_p[0].copy()
        self.image_base_color = pg.Color(unit_data_p[1])        

        if unit_data_p[2] != None: # top    
            self.image_top = unit_data_p[2].copy()
            self.image_top_color = pg.Color(unit_data_p[3])
            self.offset_top = pg.Vector2(unit_data_p[5]*self.scale, unit_data_p[6]*self.scale)

        if unit_data_p[4] != None: # shoot    
            self.image_shoot = unit_data_p[4].copy()
            self.offset_shoot = pg.Vector2(unit_data_p[7]*self.scale, unit_data_p[8]*self.scale)
        
        self.selected_sound = unit_data_p[9]
        
        self.move_speed = unit_data_p[10]
        self.base_angle_speed = unit_data_p[11]
        self.top_angle_speed = unit_data_p[12]
        self.hitpoints = unit_data_p[13]
        self.damage = unit_data_p[14]
        
        if unit_data_p[15] != None: # shoot sound
            self.shooting_sound = unit_data_p[15]
            self.shooting_delay = unit_data_p[16]

        self.death_sound = unit_data_p[17]

        self.colorkey = unit_data_p[18]
        # unit data

        self.player = player_p # None or Player

        self.image_base = scale_image(self.image_base, self.scale)
        self.image_base.set_colorkey(self.colorkey)
        if self.player != None:
            change_image_color(self.image_base, self.image_base_color, self.player.color)
        if unit_data_p[2] != '': # top 
            self.image_top = scale_image(self.image_top, self.scale)
            self.image_top.set_colorkey(self.colorkey)
            if self.player != None:
                change_image_color(self.image_top, self.image_top_color, self.player.color)
        if unit_data_p[4] != '': # shoot 
            self.image_shoot = scale_image(self.image_shoot, self.scale)
            self.image_shoot.set_colorkey(self.colorkey)

        # self.hitpoints =                unit_data_p_p[0]
        # self.hitpoint_recovery =        unit_data_p_p[1]
        # self.move_speed =               unit_data_p_p[2] * self.scale
        # self.sprite_alive =             Sprite(unit_data_p_p[3], self.scale, 100, 1)
        # self.sprite_death =             Sprite(unit_data_p_p[4], self.scale, 100, 1)
        # self.move_sounds =              unit_data_p_p[5]
        # self.idle_sounds =              unit_data_p_p[6]
        # self.death_sounds =             unit_data_p_p[7]

        # self.rect_base = self.image_base.get_rect(center = self.pos)
        # self.mask_base = pg.mask.from_surface(self.image_base)
        # if self.image_top != '':
        #     self.rect_top = self.image_top.get_rect(center = self.pos + self.offset_top)
        # if self.image_shoot != '':
        #     self.rect_shoot = self.image_shoot.get_rect(center = self.pos + self.offset_shoot)

        self.base_angle_current = 0
        self.base_angle_prev = 0
        self.base_angle_interpoalted = 0

        self.top_angle_current = 0
        self.top_angle_prev = 0
        self.top_angle_interpolated = 0

        self.is_initializing = True
            
        self.is_dead = False

        self.is_selected = False

        self.attack_target = pg.Vector2(self.tile_size*10+self.tile_size//2,self.tile_size*10+self.tile_size//2)
        self.is_shooting = False
        self.shooting_delay_elapsed = 0
        self.shooting_time = 150
        self.shooting_time_elapsed = 0
        self.draw_shoot = False

        self.bullets = []

        # self.hitpoints_max = self.hitpoints
        # self.hitpoint_recovery_timer = 100
        # self.hitpoint_recovery_ms_count = 0

        # self.move_sound_delay_range = [330,330] # ms delay before next sound will be played
        # self.move_sound_delay = random.randint(self.move_sound_delay_range[0], self.move_sound_delay_range[1])
        # self.move_sound_ms_count = self.move_sound_delay
        # self.death_sound_ms_count = 0

        # self.collide_rect = pg.Rect(pos_x_p,pos_y_p,self.current_sprite.active_surf.get_width(),self.current_sprite.active_surf.get_height())

        self.is_moving_left = False
        self.is_moving_right = False
        self.is_moving_up = False
        self.is_moving_down = False
        
        self.path = []

    def events(self, event, mouse_pos_world, pathfinding):
        
        # select
        if event.type == pg.MOUSEBUTTONUP:
            if event.button == 1:
                if self.rect_base_rotated.collidepoint(mouse_pos_world):
                    self.is_selected = True
                    if self.selected_sound != None:
                        self.selected_sound.play()
                else:
                    self.is_selected = False
        
        if self.is_selected:

            if self.player != None:
                if event.type == pg.MOUSEBUTTONUP:
                    pass

                if event.type == pg.MOUSEBUTTONDOWN:

                    if event.button == 3:
                        path = pathfinding.find_path(self.pos, mouse_pos_world)
                        self.set_path(path)

    def update(self, dt):
    
        if not self.is_dead:

            self.base_angle_prev = self.base_angle_current # base angle, set previous angle to current angle then update current angle
            self.top_angle_prev = self.top_angle_current # top angle, set previous angle to current angle then update current angle


            if self.attack_target != None:

                distance_x = self.pos.x-self.attack_target.x
                distance_y = self.pos.y-self.attack_target.y
                target_angle = self.limit_angle_to_360(math.degrees(math.atan2(distance_y, distance_x)))
                target_angle_int = int(target_angle)

                # θ = cos-1 [ (a · b) / (|a| |b|) ]
                # doesn't work
                # pos_length = pg.math.Vector2.length(self.pos)
                # attack_target_length = pg.math.Vector2.length(self.attack_target)
                # dot_product = self.pos.dot(self.attack_target)
                # target_angle = math.acos(dot_product / (pos_length * attack_target_length) )
                # target_angle_int = int(target_angle)
                # print('math', self.pos, self.attack_target, pos_length, attack_target_length, dot_product, target_angle, target_angle_int)


                # .angle_to()
                # doesn't work
                # target_angle = self.pos.angle_to(self.attack_target)
                # print('angle_to', target_angle)
                # target_angle = self.limit_angle_to_360(target_angle)
                # target_angle_int = int(target_angle)
                # print('angle_to', target_angle, target_angle_int)
                
                '''
                image degree up     = 0
                image degree left   = 90
                image degree down   = 180
                image degree right  = 270
                
                target_angle up     = 270
                target_angle left   = 180
                target_angle down   = 90
                target_angle right  = 0
                '''
                
                target_angle_to_image_angle = self.limit_angle_to_360(90-target_angle_int)

                # decide top rotation direction clockwise/counter clockwise
                cw = True
                angle_diff = self.top_angle_current-target_angle_to_image_angle
                angle_diff_360 = self.limit_angle_to_360(angle_diff)
                if angle_diff_360 > 180:
                    cw = False
                
                angle_step = int(self.top_angle_speed/100 * dt)
                print(self.top_angle_current,   self.top_angle_prev,   target_angle_int,   target_angle_to_image_angle,   angle_diff,   angle_diff_360,   cw,   angle_step)
                # if abs(self.top_angle_current - target_angle_to_image_angle) < angle_step:
                if angle_diff < angle_step:
                    self.top_angle_current = target_angle_to_image_angle
                elif cw:
                    self.top_angle_current -= angle_step
                else:
                    self.top_angle_current += angle_step

                # limit current angle to 0-360 and also set prev angle to prevent interpolation issues if current angle is set from fx. 365 to 5 and prev angle remains at fx. 355 the interpolation is done between 5 and 355 which is wrong.
                print(self.top_angle_current,   self.top_angle_prev,   target_angle_int,   target_angle_to_image_angle,   angle_diff,   angle_diff_360,   cw,   angle_step)
                if self.top_angle_current > 360:
                    self.top_angle_current -= 360
                    self.top_angle_prev -= 360
                if self.top_angle_current < 0:
                    self.top_angle_current += 360
                    self.top_angle_prev += 360
                print(self.top_angle_current,   self.top_angle_prev,   target_angle_int,   target_angle_to_image_angle,   angle_diff,   angle_diff_360,   cw,   angle_step)



            # move
            self.pos_prev = self.pos.copy() # position, set previous pos to current pos then update current pos
            
            if self.path != None and len(self.path) > 0:

                node_rect_center = pg.Rect(self.path[0].world_rect).center






                distance_x = self.pos.x-node_rect_center[0]
                distance_y = self.pos.y-node_rect_center[1]
                target_angle = self.limit_angle_to_360(math.degrees(math.atan2(distance_y, distance_x)))
                
                '''
                image degree up     = 0
                image degree left   = 90
                image degree down   = 180
                image degree right  = 270
                
                target_angle up     = 270
                target_angle left   = 180
                target_angle down   = 90
                target_angle right  = 0
                '''
                target_angle_to_image_angle = self.limit_angle_to_360(90-target_angle)

                # decide top rotation direction clockwise/counter clockwise
                cw = True
                angle_diff = self.limit_angle_to_360(self.base_angle_current - target_angle_to_image_angle)
                if angle_diff > 180:
                    cw = False

                angle_step = self.base_angle_speed/100 * dt
                if abs(self.base_angle_current - target_angle_to_image_angle) < angle_step:
                    self.base_angle_current = target_angle_to_image_angle
                elif cw:
                    self.base_angle_current -= angle_step
                else:
                    self.base_angle_current += angle_step

                # limit current angle to 0-360 and also set prev angle to prevent interpolation issues if current angle is set from fx. 365 to 5 and prev angle remains at fx. 355 the interpolation is done between 5 and 355 which is wrong.
                if self.base_angle_current > 360:
                    self.base_angle_current -= 360
                    self.base_angle_prev -= 360
                if self.base_angle_current < 0:
                    self.base_angle_current += 360
                    self.base_angle_prev += 360


                # if abs(self.base_angle_current - target_angle_to_image_angle) < 10:
                if self.base_angle_current == target_angle_to_image_angle:

                    cutoff_limit = 2
                    if abs(self.pos[0] - node_rect_center[0]) <= cutoff_limit:  # center unit x on node when close enough
                        self.pos[0] = node_rect_center[0]
                        self.is_moving_left = False
                        self.is_moving_right = False
                    elif self.pos[0] - node_rect_center[0] > cutoff_limit:  # move left
                        self.is_moving_left = True
                        self.is_moving_right = False
                    elif self.pos[0] - node_rect_center[0] < cutoff_limit:  # move right
                        self.is_moving_left = False
                        self.is_moving_right = True
                    if abs(self.pos[1] - node_rect_center[1]) <= cutoff_limit:  # center unit y on node when close enough
                        self.pos[1] = node_rect_center[1]
                        self.is_moving_up = False
                        self.is_moving_down = False                     
                    elif self.pos[1] - node_rect_center[1] > cutoff_limit:  # move up
                        self.is_moving_up = True
                        self.is_moving_down = False
                    elif self.pos[1] - node_rect_center[1] < cutoff_limit:  # move down
                        self.is_moving_up = False
                        self.is_moving_down = True
                    if not self. is_moving_left and not self.is_moving_right and not self.is_moving_up and not self.is_moving_down:
                        self.path.pop(0)
                else:
                    self.is_moving_left = False
                    self.is_moving_right = False
                    self.is_moving_up = False
                    self.is_moving_down = False
            else:
                self.is_moving_left = False
                self.is_moving_right = False
                self.is_moving_up = False
                self.is_moving_down = False

            if self.is_moving_left:
                self.pos += pg.Vector2(-1,0) * self.move_speed/100 * dt
            if self.is_moving_right:
                self.pos += pg.Vector2(1,0) * self.move_speed/100 * dt
            if self.is_moving_up:
                self.pos += pg.Vector2(0,-1) * self.move_speed/100 * dt
            if self.is_moving_down:
                self.pos += pg.Vector2(0,1) * self.move_speed/100 * dt

            # move sounds
            # if self.is_moving_left or self.is_moving_right or self.is_moving_up or self.is_moving_down:
            #     if len(self.move_sounds) > 0:
            #         self.move_sound_ms_count += dt
            #         if self.move_sound_ms_count > self.move_sound_delay:
            #             random.choice(self.move_sounds).play()
            #             self.move_sound_delay = random.randint(self.move_sound_delay_range[0], self.move_sound_delay_range[1])
            #             self.move_sound_ms_count = 0

        # dead
        else:
            pass

    def draw(self, surface, interpolate):
        if self.path != None:
            for px in self.path:
                pg.draw.circle(surface, pg.Color(0,100,200), pg.Rect(px.world_rect).center, 2*self.scale)

        self.update_rotate_interpolate_and_mask(interpolate)
        surface.blit(self.image_base_rotated, self.rect_base_rotated)
        surface.blit(self.image_top_rotated, self.rect_top_rotated)
        if self.draw_shoot:
            surface.blit(self.image_shoot_rotated, self.rect_shoot_rotated)

        # surf,rect = self.current_sprite.get_surf_rect()
        # if self.pos != self.pos_prev:
        #     i = interpolate
        #     pos_draw_new = self.pos*i + self.pos_prev*(1-i)
        #     self.pos_draw = pos_draw_new
        #     self.pos_draw_prev = self.pos_draw.copy()
        # #rect.topleft = self.pos_draw
        # rect.center = self.pos_draw
        # #rect.bottomleft = self.pos_draw
        # #rect.midbottom = self.pos_draw
        # # rect.midbottom = self.pos  # bypass interpolation

        # surf,rect = self.current_sprite.get_surf_rect()
        # if self.pos != self.pos_draw_prev:
        #     i = interpolate
        #     pos_draw_new = self.pos*i + self.pos_draw_prev*(1-i)
        #     self.pos_draw = pos_draw_new
        #     self.pos_draw_prev = self.pos_draw.copy()
        # #rect.topleft = self.pos_draw
        # #rect.center = self.pos_draw
        # #rect.bottomleft = self.pos_draw
        # rect.midbottom = self.pos_draw
        # # rect.midbottom = self.pos  # bypass interpolation

        # rect.y += self.tile_size[1]//2
        # surface.blit(surf,rect)

    def is_hit(self, damage, dt):        
        if not self.is_dead and self.hitpoints > 0:
            self.hitpoints -= damage
            # dead
            if self.hitpoints <= 0:
                self.hitpoints = 0
                self.is_dead = True

    def set_path(self, path):
        if path != None and len(path) != 0:
            # if self.path != None and len(self.path) != 0:
            #     current_waypoint = self.path[0]
            #     self.path = [current_waypoint] + path
            # else:
            #     self.path = path
            self.path = path

    def limit_angle_to_360(self, angle):
        while angle > 360:
            angle -= 360
        while angle < 0:
            angle += 360
        return angle

    def set_base_angle(self, angle, interpolate):
        self.base_angle_current = angle
        self.update_rotate_interpolate_and_mask(interpolate)

    def set_top_angle(self, angle, interpolate):
        self.top_angle_current = angle
        self.update_rotate_interpolate_and_mask(interpolate)

    def update_rotate_interpolate_and_mask(self, interpolate): # call this every draw frame to rotate and interpolate the images,rects and mask for the drawing
        i = interpolate
        # i=1 # bypass interpolation

        self.pos_interpolated = self.pos*i + self.pos_prev*(1-i)
        self.base_angle_interpoalted = self.base_angle_current*i + self.base_angle_prev*(1-i)
        self.top_angle_interpolated = self.top_angle_current*i + self.top_angle_prev*(1-i)

        if self.pos == self.pos_prev:
            self.pos_interpolated = self.pos
        if self.base_angle_current == self.base_angle_prev:
            self.base_angle_interpoalted = self.base_angle_current
        if self.top_angle_current == self.top_angle_prev:
            self.top_angle_interpolated = self.top_angle_current

        self.image_base_rotated, self.rect_base_rotated = rotate_image      ( self.image_base.copy(),
                                                                              self.base_angle_interpoalted,
                                                                              self.pos_interpolated,
                                                                             #(self.rect_base.width/2 , self.rect_base.height/2)
                                                                             (0,0)
                                                                            )
        self.image_top_rotated, self.rect_top_rotated = rotate_image        ( self.image_top.copy(),
                                                                              self.top_angle_interpolated,
                                                                              self.pos_interpolated,
                                                                              #(self.rect_top.width/2-self.offset_top.x , self.rect_top.height/2-self.offset_top.y)
                                                                              (self.offset_top.x , self.offset_top.y)
                                                                            )
        self.image_shoot_rotated, self.rect_shoot_rotated = rotate_image    ( self.image_shoot.copy(),
                                                                              self.top_angle_interpolated,
                                                                              self.pos_interpolated,
                                                                              #(self.rect_shoot.width/2-self.offset_shoot.x , self.rect_shoot.height/2-self.offset_shoot.y)
                                                                              (self.offset_shoot.x , self.offset_shoot.y)
                                                                            )

        self.mask_base = pg.mask.from_surface(self.image_base_rotated)
        self.is_initializing = False

        # print(self.pos, self.pos_prev, self.pos_interpolated, i)
        # print(int(self.base_angle_current), int(self.base_angle_prev), int(self.base_angle_interpoalted), i)
        print(int(self.top_angle_current), int(self.top_angle_prev), int(self.top_angle_interpolated), i)