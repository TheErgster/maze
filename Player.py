import sys
sys.dont_write_bytecode = True
# This is a holy warding spell, one that is required for my computer for some stupid reason
# Please place it at the top of each new file, such that I may remain protected


import wasabi2d as w2d
import time
import math
from pewpew import Orb
from chunk_generation import Chunk, Cell
from maze_as_a_whole import Maze

# Create a new scene
scene = w2d.Scene(width=800, height=600, background=(0, 0, 0), title="My Scene")
animate = w2d.animate 
TILE_LEN = 50

class Player:
	
	def __init__(self):
		self.maze = Maze()
		self.map_position = [self.maze.MAP_LEN//2, self.maze.MAP_LEN//2] # [Y, X], NOT THE OTHER WAY AROUND!!!!!

		self.CHUNKLEN = self.maze.center_chunk.CHUNKLEN

		self.rendered_room_stuff:dict[set[Cell]] = {}
		
		# Create a new square sprite for the Player
		self.sprite = scene.layers[1].add_rect(
			width=TILE_LEN,
			height=TILE_LEN,
			pos=(50, 50),
			color=(1, 0, 0),  # Red color
		)

		# Set flags for key presses
		self.up_pressed:bool = False
		self.down_pressed:bool = False
		self.left_pressed:bool = False
		self.right_pressed:bool = False
		self.space_pressed:bool = False

		self.attacking = 0  

		self.direction = 0
		self.last_ver_move_up:bool = True
		self.last_hor_move_right:bool = True

		# Orb feature attributes
		self.orb_types = [
			{
				'name': 'purple',
				'color': (0.5, 0, 0.5),
				'cooldown': 0.5,
				'expand_on_impact': False,
			},
			{
				'name': 'orange',
				'color': (1, 0.5, 0),
				'cooldown': 1.0,
				'expand_on_impact': True,
			}
		]
		self.current_orb_index = 0
		self.last_orb_time = 0
		self.active_orbs = []

		# Orb feature attributes
		self.orb_types = [
			{
				'name': 'purple',
				'color': (0.5, 0, 0.5),
				'cooldown': 0.5,
				'expand_on_impact': False,
			},
			{
				'name': 'orange',
				'color': (1, 0.5, 0),
				'cooldown': 1.0,
				'expand_on_impact': True,
			}
		]
		self.current_orb_index = 0
		self.last_orb_time = 0
		self.active_orbs = []






	def render_chunk(self, map_y, map_x): 
		"""
		Here so that there's only one scene to render, despite multiple layers
		
		Single hunk rendering starts at (0,0), then builds right and down
		multi-chunk rendering starts some offset (seen below), then does the same
		"""
		if tuple([map_y, map_x]) in self.rendered_room_stuff:
			print(4)
			return
		print(5)
		chunk:Chunk = self.maze.get_chunk(map_y,map_x)
		pix_start_y = self.maze.center_chunk.CHUNKLEN * TILE_LEN * (map_y - self.maze.center[0])
		pix_start_x = self.maze.center_chunk.CHUNKLEN * TILE_LEN * (map_x - self.maze.center[1])
		
		# print(f"{map_y} -> {pix_start_y} | {map_x} -> {pix_start_x} | {self.maze.center}")

		self.rendered_room_stuff[tuple([map_y,map_x])] = set()
		tile_set = self.rendered_room_stuff[tuple([map_y,map_x])]

		for i in range(chunk.CHUNKLEN):
			for j in range(chunk.CHUNKLEN):
				if chunk.grid[i][j].wall == True:
					tile = scene.layers[0].add_rect(
					width=TILE_LEN,
					height=TILE_LEN,
					pos=(pix_start_x + (TILE_LEN*j), pix_start_y + (TILE_LEN*i)),
					color=(1, 1, 1),  # White
					)
					tile_set.add(tile)
	

	def find_current_tile(self):
		tile_x = int(round(self.sprite.x / 50))
		tile_y = int(round(self.sprite.y / 50))
		
		return [tile_y, tile_x]


	def render_manager(self):
		print("TRIGGERED")

		pos_set:set = set([]) # this is for chunk de-rendering
		
		# the chunk you're in
		self.render_chunk(self.map_position[0], self.map_position[1])
		pos_set.add(tuple([self.map_position[0], self.map_position[1]]))

		# the chunks directly around you
		self.render_chunk(self.map_position[0]-1, self.map_position[1])
		pos_set.add(tuple([self.map_position[0]-1, self.map_position[1]]))
		self.render_chunk(self.map_position[0]+1, self.map_position[1])
		pos_set.add(tuple([self.map_position[0]+1, self.map_position[1]]))
		self.render_chunk(self.map_position[0], self.map_position[1]-1)
		pos_set.add(tuple([self.map_position[0], self.map_position[1]-1]))
		self.render_chunk(self.map_position[0], self.map_position[1]+1)
		pos_set.add(tuple([self.map_position[0], self.map_position[1]+1]))

		# the chunks diagonally around you
		self.render_chunk(self.map_position[0]+1, self.map_position[1]+1)
		pos_set.add(tuple([self.map_position[0]+1, self.map_position[1]+1]))
		self.render_chunk(self.map_position[0]-1, self.map_position[1]+1)
		pos_set.add(tuple([self.map_position[0]-1, self.map_position[1]+1]))
		self.render_chunk(self.map_position[0]-1, self.map_position[1]-1)
		pos_set.add(tuple([self.map_position[0]-1, self.map_position[1]-1]))
		self.render_chunk(self.map_position[0]+1, self.map_position[1]-1)
		pos_set.add(tuple([self.map_position[0]+1, self.map_position[1]-1]))

		will_del = set()
		for key in self.rendered_room_stuff.keys():
			if key not in pos_set:
				to_del = self.rendered_room_stuff[key]
				for tile in to_del:
					del tile
				will_del.add(key)
		
		for key in will_del:
			del self.rendered_room_stuff[key]
				


	def update_map_position(self, y, x):
		self.map_position[0] += y
		self.map_position[1] += x

		self.render_manager()

	
	def move_up(self):
		if self.sprite.y % TILE_LEN == 0:
			tile_coords:list[int] = self.find_current_tile()
			tile_coords[0] -= 1
			current_chunk_y_start = ((self.map_position[0]-(self.CHUNKLEN//2)) * self.CHUNKLEN)
			print(tile_coords,current_chunk_y_start)

			if tile_coords[0] < current_chunk_y_start:
				self.update_map_position(-1, 0)

				

			chunk:Chunk = self.maze.map[self.map_position[0]][self.map_position[1]]
			if chunk.grid[tile_coords[0] % self.CHUNKLEN][tile_coords[1] % self.CHUNKLEN].wall:
				return

		# Add trail at current position before moving
		# trail = scene.layers[0].add_rect(
		# 	width=10,
		# 	height=10,
		# 	pos=(self.sprite.x, self.sprite.y),
		# 	color=(1, 0, 0, 0.3),  # Red with transparency
		# )
		
		new_y = self.sprite.y - 10
		
		player.attacking = 1
		self.sprite.y = new_y
		self.direction = 90
		player.attacking = 0

		scene.camera.pos = player.sprite.pos
		self.last_ver_move_up = True



	def move_down(self):

		if self.sprite.y % TILE_LEN == 0:
			tile_coords:list[int] = self.find_current_tile()
			tile_coords[0] += 1
			current_chunk_y_end = ((self.map_position[0]-(self.CHUNKLEN//2)) * self.CHUNKLEN) + self.CHUNKLEN
			print(tile_coords,current_chunk_y_end)

			if tile_coords[0] > current_chunk_y_end: # might need to change to a >=, but this works so it's fine
				self.update_map_position(1, 0)


			chunk:Chunk = self.maze.map[self.map_position[0]][self.map_position[1]]
			if chunk.grid[tile_coords[0] % self.CHUNKLEN][tile_coords[1] % self.CHUNKLEN].wall:
				return

		# Add trail at current position before moving
		# trail = scene.layers[0].add_rect(
		# 	width=10,
		# 	height=10,
		# 	pos=(self.sprite.x, self.sprite.y),
		# 	color=(1, 0, 0, 0.3),  # Red with transparency
		# )
		
		new_y = self.sprite.y + 10

		player.attacking = 1
		self.sprite.y = new_y
		self.direction = 270
		player.attacking = 0
		

		scene.camera.pos = player.sprite.pos
		self.last_ver_move_up = False



	def move_left(self):

		if self.sprite.x % TILE_LEN == 0:
			tile_coords:list[int] = self.find_current_tile()
			tile_coords[1] -= 1
			current_chunk_x_start = ((self.map_position[1]-(self.CHUNKLEN//2)) * self.CHUNKLEN)
			print(tile_coords,current_chunk_x_start)

			if tile_coords[1] < current_chunk_x_start:
				self.update_map_position(0, -1)


			chunk:Chunk = self.maze.map[self.map_position[0]][self.map_position[1]]
			if chunk.grid[tile_coords[0] % self.CHUNKLEN][tile_coords[1] % self.CHUNKLEN].wall:
				print("ow my liver")
				return
			
		# Add trail at current position before moving
		# trail = scene.layers[0].add_rect(
		# 	width=10,
		# 	height=10,
		# 	pos=(self.sprite.x, self.sprite.y),
		# 	color=(1, 0, 0, 0.3),  # Red with transparency
		# )
		
		new_x = self.sprite.x - 10

		player.attacking = 1
		self.sprite.x = new_x
		self.direction = 180
		player.attacking = 0

		scene.camera.pos = player.sprite.pos
		self.last_hor_move_right = False
	def move_right(self):

		if self.sprite.x % TILE_LEN == 0:
			tile_coords:list[int] = self.find_current_tile()
			tile_coords[1] += 1
			current_chunk_x_end = ((self.map_position[1]-(self.CHUNKLEN//2)) * self.CHUNKLEN) + self.CHUNKLEN
			print(tile_coords,current_chunk_x_end)

			if tile_coords[1] > current_chunk_x_end:
				self.update_map_position(0, 1)


			chunk:Chunk = self.maze.map[self.map_position[0]][self.map_position[1]]



	def move_right(self):

		if self.sprite.x % TILE_LEN == 0:
			tile_coords:list[int] = self.find_current_tile()
			tile_coords[1] += 1
			current_chunk_x_end = ((self.map_position[1]-(self.CHUNKLEN//2)) * self.CHUNKLEN) + self.CHUNKLEN
			print(tile_coords,current_chunk_x_end)

			if tile_coords[1] > current_chunk_x_end:
				self.update_map_position(0, 1)


			chunk:Chunk = self.maze.map[self.map_position[0]][self.map_position[1]]
			if chunk.grid[tile_coords[0] % self.CHUNKLEN][tile_coords[1] % self.CHUNKLEN].wall:
				return
			
		# Add trail at current position before moving
		# trail = scene.layers[0].add_rect(
		# 	width=10,
		# 	height=10,
		# 	pos=(self.sprite.x, self.sprite.y),
		# 	color=(1, 0, 0, 0.3),  # Red with transparency
		# )
		
		new_x = self.sprite.x + 10

		player.attacking = 1
		self.sprite.x = new_x
		self.direction = 180
		player.attacking = 0
		

		scene.camera.pos = player.sprite.pos
		self.last_hor_move_right = True
	# Define movement functions




	# Remove the sword after the attack
	def attack(self):
		self.Sword = scene.layers[-1].add_sprite( # should probably re-write in terms of TILE_LEN
		scale = 1.5,
		pos=(400, 300),
		image="sword.png",  # Set the rotation based on the player's direction
		# Black color for the sword
		)

		def on_animation_finished():
			self.Sword.delete()
			self.attacking = 0
			# Reset movement flags to stop continuous movement after attack
			self.up_pressed = False
			self.down_pressed = False
			self.left_pressed = False
			self.right_pressed = False
		
		self.attacking = 1

		# Determine the tile in front of the player based on direction
		tile_coords = self.find_current_tile()
		chunk = self.maze.map[self.map_position[0]][self.map_position[1]]

		print(f"Attack: tile_coords={tile_coords}, direction={self.direction}")

		front_wall = False
		if self.direction == 180:  # facing left
			print(f"Checking left tile wall: {chunk.grid[tile_coords[1]][tile_coords[0]+1].wall}")
			if chunk.grid[tile_coords[1]][tile_coords[0]+1].wall:
				front_wall = True
		elif self.direction == 90:  # facing up
			print(f"Checking up tile wall: {chunk.grid[tile_coords[1]-1][tile_coords[0]].wall}")
			if chunk.grid[tile_coords[1]-1][tile_coords[0]].wall:
				front_wall = True
		elif self.direction == 0:  # facing right
			print(f"Checking right tile wall: {chunk.grid[tile_coords[1]][tile_coords[0]-1].wall}")
			if chunk.grid[tile_coords[1]][tile_coords[0]-1].wall:
				front_wall = True
		elif self.direction == 270:  # facing down
			print(f"Checking down tile wall: {chunk.grid[tile_coords[1]+1][tile_coords[0]].wall}")
			if chunk.grid[tile_coords[1]+1][tile_coords[0]].wall:
				front_wall = True

		if front_wall:
			# Swing sword on opposite side
			if self.direction == 180:  # facing left, swing right
				self.Sword.pos = (self.sprite.pos - (25, 0))
				animate(self.Sword, tween='linear', duration=0.3, angle=3, on_finished=on_animation_finished)
			elif self.direction == 90:  # facing up, swing down
				self.Sword.pos = (self.sprite.pos + (0, 25))
				animate(self.Sword, tween='linear', duration=0.3, angle=-3, on_finished=on_animation_finished)
			elif self.direction == 0:  # facing right, swing left
				self.Sword.pos = (self.sprite.pos + (25, 0))
				animate(self.Sword, tween='linear', duration=0.3, angle=-3, on_finished=on_animation_finished)
			elif self.direction == 270:  # facing down, swing up
				self.Sword.pos = (self.sprite.pos - (0, 25))
				animate(self.Sword, tween='linear', duration=0.3, angle=3, on_finished=on_animation_finished)
		else:
			# Swing sword normally
			if self.direction == 180:  # Player is facing left
				self.Sword.pos = (self.sprite.pos + (25, 0))
				animate(self.Sword, tween='linear', duration=0.3, angle=-3, on_finished=on_animation_finished)
				
			elif self.direction == 90:  # Player is facing up
				self.Sword.pos = (self.sprite.pos - (0, 25))
				animate(self.Sword, tween='linear', duration=0.3, angle=3, on_finished=on_animation_finished)
				
			elif self.direction == 0:  # Player is facing right
				self.Sword.pos = (self.sprite.pos - (25, 0))
				animate(self.Sword, tween='linear', duration=0.3, angle=3, on_finished=on_animation_finished) 
				
			elif self.direction == 270:  # Player is facing down
				self.Sword.pos = (self.sprite.pos + (0, 25))
				animate(self.Sword, tween='linear', duration=0.3, angle=-3, on_finished=on_animation_finished)

	# def check_collision(self, new_x, new_y):
	# 	"""
	# 	Checks whether the player's next move will result in a collision with a wall.

	# 	Args:
	# 		new_x (int): The new x-coordinate of the player.
	# 		new_y (int): The new y-coordinate of the player.

	# 	Returns:
	# 		bool: True if there is a collision, False otherwise.
	# 	"""
	# 	# Calculate the tile coordinates of the player's next move
	# 	tile_x = int((new_x + TILE_LEN/ 2) // TILE_LEN)
	# 	tile_y = int((new_y + TILE_LEN/ 2) // TILE_LEN)
		
	# 	# Get the chunk that the player is currently in
	# 	chunk = self.maze.map[self.map_position[0]][self.map_position[1]]
		
	# 	# Get the cell that the player is trying to move into
	# 	cell = chunk.grid[tile_y][tile_x]
		
	# 	# Check if the cell is a wall
	# 	if cell.wall:
	# 		return True
	# 	else:
	# 		return False

player = Player()



@w2d.event
def on_key_down(key):
	if player.attacking == 1:
		pass
	elif player.attacking == 0:
		if key == w2d.keys.UP:
			player.up_pressed = True
		elif key == w2d.keys.DOWN:
			player.down_pressed = True
		elif key == w2d.keys.LEFT:
			player.left_pressed = True
		elif key == w2d.keys.RIGHT:
			player.right_pressed = True
		elif key == w2d.keys.SPACE:
			player.attack()
		elif key == w2d.keys.X:
			current_time = time.time()
			orb_type = player.orb_types[player.current_orb_index]
			if current_time - player.last_orb_time >= orb_type['cooldown']:
				new_orb = Orb(player, orb_type)
				player.active_orbs.append(new_orb)
				player.last_orb_time = current_time
		elif key == w2d.keys.E:
			player.current_orb_index = (player.current_orb_index + 1) % len(player.orb_types)
	else:
		print(player.attacking)



@w2d.event
def on_key_up(key):
	if player.attacking == 1:
		pass

	elif player.attacking == 0:
		if key == w2d.keys.UP:
			player.up_pressed = False
		elif key == w2d.keys.DOWN:
			player.down_pressed = False
		elif key == w2d.keys.LEFT:
			player.left_pressed = False
		elif key == w2d.keys.RIGHT:
			player.right_pressed = False

		

		if player.sprite.x % TILE_LEN != 0:
			for _ in range(4):
				scene.camera.pos = player.sprite.pos
				if player.last_hor_move_right == True:
					player.move_right()
					#time.sleep(1/60)
				else:
					player.move_left()
					#time.sleep(1/60)

				if player.sprite.x % TILE_LEN == 0:
					break
				scene.camera.pos = player.sprite.pos
		
		if player.sprite.y % TILE_LEN != 0:
			for _ in range(4):
				scene.camera.pos = player.sprite.pos
				if player.last_ver_move_up == True:
					player.move_up()
					#time.sleep(1/60)
				else:
					player.move_down()
					#time.sleep(1/60)

				if player.sprite.y % TILE_LEN == 0:
					break
				scene.camera.pos = player.sprite.pos


	

	else:
		print(player.attacking)
	

def update():
	scene.camera.pos = player.sprite.pos

	# Update orbs
	current_time = time.time()
	for orb in player.active_orbs[:]:
		orb.update()
		if orb.to_delete:
			player.active_orbs.remove(orb)

	if player.attacking == 1:
		pass
	elif player.attacking == 0:
		if player.up_pressed:
			player.move_up()
		elif player.down_pressed:
			player.move_down()
		elif player.left_pressed:
			player.move_left()
		elif player.right_pressed:
			player.move_right()
	else:
		pass
	w2d.clock.schedule(update, 1/60)



# Run the scene

update()
player.render_manager()
w2d.run()
