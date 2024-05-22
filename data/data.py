from .prepare import GFX
from .prepare import SFX

# units
unit_data =	{
				'tank_01' : [
								GFX['']['tank_base_1_up'],			# 00 image base
								[255,0,255],						# 01 image_base default color, for color change
								GFX['']['turret_1_up'],				# 02 image top
								[255,0,255],						# 03 image_top default color, for color change
								GFX['']['fire_yellow_4_up'],		# 04 image shoot
								0,									# 05 image_top_offset_x
								7,									# 06 image_top_offset_y
								0,									# 07 image_shoot_offset_x
								-23,								# 08 image_shoot_offset_y
								None,								# 09 selected_sound
								5,									# 10 move_speed
								40,									# 11 base_angle_speed
								20,									# 12 top_angle_speed
								500,								# 13 hitpoints
								100,								# 14 damage
								None,								# 15 shooting_sound
								500,								# 16 shooting_delay [ms]
								None,								# 17 death sound
								[255,255,255],						# 18 color key
							],
			}