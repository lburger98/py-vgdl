import math
from .core import VGDLSprite

class AStarNode(object):

	def __init__(self, index, vgdlSprite):
		self.vgdlSprite = vgdlSprite
		self.sprite = vgdlSprite
		self.index = index


class AStarWorld(object):

	def __init__(self, game, speed):
		self.game = game
		#ghost_sprites = game.getSprites('ghost')
		#pacman_sprite = game.getSprites('pacman')[0]

		moving_types = [i for i in game.sprite_registry.sprite_keys if i not in ['wall', 'floor']]
		moving = []
		for mtype in moving_types:
			moving += game.get_sprites(mtype)
		self.moving = moving
		self.empty = game.get_sprites('floor')
		self.speed = speed
		self.walls = game.get_sprites('wall')

		self.save_walkable_tiles()

	def get_walkable_tiles(self):
		return self.moving + self.empty

	def save_walkable_tiles(self):

		self.walkable_tiles = {}
		self.walkable_tile_indices = []
		self.wall_tile_indices = []

		combined = self.moving + self.empty
		#print combined
		for sprite in combined:
			#print sprite
			tileX, tileY = self.get_sprite_tile_position(sprite)
			index = self.get_index(tileX, tileY)
			self.walkable_tile_indices.append(index)
			self.walkable_tiles[index] = AStarNode(index, sprite)
		for wall in self.walls:
			tileX, tileY = self.get_sprite_tile_position(wall)
			index = self.get_index(tileX, tileY)
			self.wall_tile_indices.append(index)



	def get_index(self, tileX, tileY):
		#return tileX  * self.game.width + tileY
		return tileY  * self.game.width + tileX

	def get_tile_from_index(self, index):
		return index/self.game.width, index%self.game.width

	def h(self, start, goal):
		#return self.euclidean(start, goal)
		return self.distance(start, goal)

	def euclidean(self, node1, node2):
		x1, y1 = self.get_sprite_tile_position(node1.sprite)
		x2, y2 = self.get_sprite_tile_position(node2.sprite)

		#print "x1:%s, y1:%s, x2:%s, y2:%s" %(x1,y1,x2,y2)
		a = x2-x1
		b = y2-y1

		#print "a:%s, b:%s" %(a,b)
		return math.sqrt(a*a + b*b)


	def get_sprite_tile_position(self, sprite):
		tileX = sprite.rect.left/self.game.block_size
		tileY = sprite.rect.top/self.game.block_size

		return tileX, tileY


	def get_lowest_f(self, nodes, f_score):
		f_best = 9999
		node_best = None
		for node in nodes:
			if f_score[node.index] < f_best:
				f_best = f_score[node.index]
				node_best = node

		return node_best


	def reconstruct_path(self, came_from, current):
		#print self.get_tile_from_index(current.index)
		if current.index in came_from:
			p = self.reconstruct_path(came_from, came_from[current.index])
			p.append(current)
			return p
		else:
			return [current]


	def neighbor_nodes(self, node):
		sprite = node.sprite;
		return self.neighbor_nodes_of_sprite(sprite)

	def neighbor_nodes_of_sprite(self, sprite):
		tileX, tileY = self.get_sprite_tile_position(sprite)
		neighbors = []

		tileSet = [[(tilex, tileY) for tilex in range(int(tileX+1), int(tileX+self.speed+1))]]
		tileSet.append([(tilex, tileY) for tilex in range(int(tileX-1), int(tileX-self.speed-1), -1)])
		tileSet.append([(tileX, tiley) for tiley in range(int(tileY+1), int(tileY+self.speed+1))])
		tileSet.append([(tileX, tiley) for tiley in range(int(tileY-1), int(tileY-self.speed-1), -1)])

		for tiles in tileSet:
			for (tilex, tiley) in tiles:
				tilex, tiley = float(tilex), float(tiley)
				if (tilex >= 0 and tilex < self.game.width and tiley >= 0 and tiley < self.game.height):
					index = self.get_index(tilex, tiley)
					if index in self.wall_tile_indices:
						break
					else:
						neighbors.append(self.walkable_tiles[index])

		# neighbor_indices = [neighbor.index for neighbor in neighbors]
		# print 'neighbors(%s,%s):%s' %(tileX, tileY, map(self.get_tile_from_index, neighbor_indices))
		return neighbors

	def distance(self, node1, node2):
		x1, y1 = self.get_sprite_tile_position(node1.sprite)
		x2, y2 = self.get_sprite_tile_position(node2.sprite)

		return abs(x2-x1) + abs(y2-y1)

	def getMoveFor(self, startSprite, goal_sprite):
		tileX, tileY = self.get_sprite_tile_position(startSprite)
		index = self.get_index(tileX, tileY)
		startNode = AStarNode(index, startSprite)

		goalX, goalY = self.get_sprite_tile_position(goal_sprite)
		goalIndex = self.get_index(goalX, goalY)
		goalNode = AStarNode(goalIndex, goal_sprite)

		return self.search(startNode, goalNode)

	def search(self, start, goal):

		# Initialize the variables.
		closedset = []
		openset = []
		came_from = {}
		g_score = {}
		f_score = {}

		openset = [start]
		g_score[start.index] = 0
		f_score[start.index] = g_score[start.index] + self.h(start, goal)

		while (len(openset) > 0):

			current = self.get_lowest_f(openset, f_score)
			if current.index == goal.index:
				# print came_from
				path = self.reconstruct_path(came_from, goal)
				# path_sprites = [node.sprite for node in path]
				# pathh = map(self.get_sprite_tile_position, path_sprites)
				# print pathh
				return path

			openset.remove(current)
			closedset.append(current)

			for neighbor in self.neighbor_nodes(current):
				temp_g = g_score[current.index] + self.distance(current, neighbor)
				if self.nodeInSet(neighbor, closedset) and temp_g >= g_score[neighbor.index]:
					continue
				if not self.nodeInSet(neighbor, openset) or temp_g < g_score[neighbor.index]:
					came_from[neighbor.index] = current
					#print 'came_from[%s]=%s' % (self.get_tile_from_index(neighbor.index), self.get_tile_from_index(current.index))
					g_score[neighbor.index] = temp_g
					f_score[neighbor.index] = g_score[neighbor.index] + self.h(neighbor, goal)
					if neighbor not in openset:
						openset.append(neighbor)

		return None

	def nodeInSet(self, node, nodeSet):
		nodeSetIndices = [n.index for n in nodeSet]
		return node.index in nodeSetIndices






