import time
# from simple_pid import PID

class Game_Loop_Timer:

	'''
	https://gafferongames.com/post/fix_your_timestep/

	fixed timestep game loop.
	the class works by accumulating time by having update() called each frame.
	when the accumulated time is greater than or equal to the chosen update_pr_sec the is_update_ready() will return true and the game state should be updated.
	the accumulated time must then have the desired updates_pr_sec subtracted from its current value.
	
	fx. if updates_pr_sec_p=60 that means ms_between_updates = 1000/60 = 16.67 ms
	at each frame the cycle time is added to ms_accumulator_update. so let's say the cycle time is 5 ms then it grows from 0 -> 5 -> 10 -> 15 -> 20 ...
	at ms_accumulator_update=20 it is greater than ms_between_updates=16.67. at this point is_update_ready() will return true and the game state should be updated
	and the ms_accumulator_update -= ms_between_updates => ms_accumulator_update=3.33ms.
	the accumulator then grows with each cycle again and the process repeats.
	in this way the game will always update at the desired rate regardless of hardware and the drawing can be done independently at whichever desired fps.
	
	note that the ms_accumulator_update could be greater than the ms_between_updates by any number of factors - like twice as large or thrice.
	because of that the game state update() should be called in a while loop.
	fx.
	while Game_Loop_Timer.is_update_ready():
		*update game state*
		Game_Loop_Timer.subtract_accumulator_update()

	the get_alpha() function returns a fraction of the remaining ms_accumulator_update time divided by desired ms_between_updates.
	this value is used to interpolate drawing between the previous state and current state to eliminate graphical 'stuttering' at low update rates.

	the class works the same with draw where you can call is_draw_ready() and if true then draw your game and after that
	call subtract_accumulator_draw() at the end of drawing to reset the accumulator.
	note that if the ms_accumulator_draw is larger than ms_betwees_draws by factors then we don't want to draw the same state multiple times
	so the subtract_accumulator_draw() is a while loop that keeps subtracting the ms_betwees_draws until the ms_accumulator_draw is < than ms_betwees_draws.
	
	you can use the 'get_update_rate_modifyer()' function if you designed your game at a specific update rate and then for whatever
	reason needs to change it. this can in cases where dt is not used cause the game to run slower or faster.
    the returned value of this function needs to be passed to objects that relys on the games update rate so they can compensate
	if the update rate changes.
	fx. the game updates 60 times pr sec and a projectile moves 10 pr update => the projectile moves 600 pr sec.
	if you were to change the update rate to 30 times pr sec the same projectile would move 300 pr sec which is half speed.
	pass the update_rate_modifyer to the projectile and multiply it with its speed to compensate for update rates that vary
	from designed update rate.
	# using dt 'get_dt_ms()' for movement and timing will eliminate the need for this compensation.

	the max_fps_p parameter is used to prevent the game from running as fast as possible on your machine which would in many cases use an unnecessary
	amount of resources and could cause the pc fans to spin up noisily. it slows the game down by calling time.sleep(1/max_fps_p).
	set max_fps_p=0 to allow unlimited max fps.
	make sure this cap doesn't cause your update and draw fps to drop.
	you can monitor your fps, update_fps and draw_fps with the get_fps() function.
	'''

	def __init__(self, updates_pr_sec_p, draws_pr_sec_p, max_fps_p=140, updates_pr_sec_design_p=None):
		self.updates_pr_sec = updates_pr_sec_p
		self.draws_pr_sec = draws_pr_sec_p
		self.max_fps = max_fps_p
		self.updates_pr_sec_design = updates_pr_sec_design_p

		time_now = time.time()

		self.last_fps_time = time_now
		self.fps_list = [0] * 60
		self.fps_list_pos = 0
		self.fps_avg = 0

		self.ms_between_updates = 1000 / self.updates_pr_sec
		self.ms_accumulator_update = 0
		self.time_old_update = time_now
		self.last_update_time = time_now
		self.update_fps_list = [0] * 60
		self.update_fps_list_pos = 0
		self.update_fps_avg = 0
		
		self.ms_betwees_draws = 1000 / self.draws_pr_sec
		self.ms_accumulator_draw = 0
		self.time_old_draw = time_now
		self.last_draw_time = time_now
		self.draw_fps_list = [0] * 60
		self.draw_fps_list_pos = 0
		self.draw_fps_avg = 0

		# self.pid = PID(-0.00001, -0.00001, -0, setpoint=self.max_fps)  # PID loop controlled max fps
		self.max_fps_sleep = 1/self.max_fps

		self.update_paused = False

	def update(self):
		time_now = time.time()
		
		if not self.update_paused:
			# update
			self.ms_accumulator_update += (time_now - self.time_old_update) * 1000
			self.time_old_update = time_now
		
		# draw
		self.ms_accumulator_draw += (time_now - self.time_old_draw) * 1000
		self.time_old_draw = time_now

		self.calc_fps(time_now)

		# max fps (this approach is probably dumb)
		if self.fps_avg > self.max_fps:
			self.max_fps_sleep += 0.00001
		elif self.fps_avg < self.max_fps:
			self.max_fps_sleep -= 0.00001
		# self.max_fps_sleep = self.pid(self.fps_avg)
		if self.max_fps != 0:
			if self.max_fps_sleep > 0 and self.max_fps_sleep <=1:
				time.sleep(self.max_fps_sleep) # fps cap to prevent pc resource overuse and noisy fans

	def is_update_ready(self):
		return self.ms_accumulator_update >= self.ms_between_updates

	def subtract_accumulator_update(self):
		self.ms_accumulator_update -= self.ms_between_updates
		self.calc_fps_update()

	def get_alpha(self):
		return round(self.ms_accumulator_update/self.ms_between_updates, 2)

	def is_draw_ready(self):
		return self.ms_accumulator_draw >= self.ms_betwees_draws

	def subtract_accumulator_draw(self):
		while self.ms_accumulator_draw - self.ms_betwees_draws >= 0:
			self.ms_accumulator_draw -= self.ms_betwees_draws
		self.calc_fps_draw()

	def get_update_rate_modifyer(self):
		if self.updates_pr_sec_design != None:
			return round(self.updates_pr_sec_design / self.updates_pr_sec, 2)
		else:
			return 1

	# get calculated dt in ms based on the chosen updates_pr_sec.
	# pass this to obejcts which update() uses dt.
	# multiply it with desired game speed before passing it.
	# fx. game speed 1 is standard. game speed 2 is double speed. will work with decimal speeds as fx. 1.5.
	def get_dt_ms(self):
		return round(1000 / self.updates_pr_sec, 2)

	def pause_update(self):
		self.update_paused = not self.update_paused
		if self.update_paused:
			self.ms_accumulator_update = 0
		else:
			self.time_old_update = time.time()

	def calc_fps(self, time_now):
		if time_now - self.last_fps_time != 0:
			fps = 1/(time.time() - self.last_fps_time)
			self.fps_list[self.fps_list_pos] = fps
			self.fps_list_pos = (self.fps_list_pos+1) % len(self.fps_list)
			self.fps_avg = sum(self.fps_list)/len(self.fps_list)
		self.last_fps_time = time_now

	def calc_fps_update(self):
		if time.time() - self.last_update_time != 0:
			update_fps = 1/(time.time() - self.last_update_time)
			self.update_fps_list[self.update_fps_list_pos] = update_fps
			self.update_fps_list_pos = (self.update_fps_list_pos+1) % len(self.update_fps_list)
			self.update_fps_avg = sum(self.update_fps_list)/len(self.update_fps_list)
		self.last_update_time = time.time()

	def calc_fps_draw(self):
		if time.time() - self.last_draw_time != 0:
			draw_fps = 1/(time.time() - self.last_draw_time)
			self.draw_fps_list[self.draw_fps_list_pos] = draw_fps
			self.draw_fps_list_pos = (self.draw_fps_list_pos+1) % len(self.draw_fps_list)
			self.draw_fps_avg = sum(self.draw_fps_list)/len(self.draw_fps_list)
		self.last_draw_time = time.time()

	def get_fps(self):
		return int(self.fps_avg), int(self.update_fps_avg), int(self.draw_fps_avg)