var DIRECTIONS = [
	{ name: 'N', dx: 0, dy: -1, opposite: 'S' },
	{ name: 'E', dx: 1, dy: 0, opposite: 'W' },
	{ name: 'S', dx: 0, dy: 1, opposite: 'N' },
	{ name: 'W', dx: -1, dy: 0, opposite: 'E' },
]

function randInt(min, max) {
	return Math.floor(Math.random() * (max - min + 1)) + min
}

function pick(array) {
	return array[randInt(0, array.length - 1)]
}

function shuffle(array) {
	var copy = array.slice()
	for (var i = copy.length - 1; i > 0; i--) {
		var j = randInt(0, i)
		var tmp = copy[i]
		copy[i] = copy[j]
		copy[j] = tmp
	}
	return copy
}

function keyOf(x, y) {
	return x + ',' + y
}

function clamp(value, min, max) {
	return Math.max(min, Math.min(max, value))
}

function DungeonRoom(opts) {
	opts = opts || {}
	this.monsters = opts.monsters || 0
	this.gold = opts.gold || 0
	this.collapsed = !!opts.collapsed
	this.doors = opts.doors || { N: false, E: false, S: false, W: false }
	this.x = opts.x || 0
	this.y = opts.y || 0
	this.entry = !!opts.entry
}

DungeonRoom.prototype.clone = function () {
	return new DungeonRoom({
		monsters: this.monsters,
		gold: this.gold,
		collapsed: this.collapsed,
		doors: {
			N: !!this.doors.N,
			E: !!this.doors.E,
			S: !!this.doors.S,
			W: !!this.doors.W,
		},
		x: this.x,
		y: this.y,
		entry: this.entry,
	})
}

function DungeonGame(size, options) {
	if (!Number.isInteger(size) || size < 4 || size > 6) {
		throw new Error('Dungeon size must be an integer from 4 to 6')
	}
	options = options || {}
	this.size = size
	this.options = options
	var generated = createRandomDungeon(size, options)
	this.grid = generated.grid
	this.entry = generated.entry
}

DungeonGame.prototype.render = function () {
	return renderDungeon(this.grid, this.entry)
}

DungeonGame.prototype.dungeonCrawl = function (hp) {
	return maxDungeonCrawl(this.grid, hp, { allowHeal: false })
}

DungeonGame.prototype.maxDungeonCrawl = function (hp) {
	return maxDungeonCrawl(this.grid, hp, { allowHeal: true })
}

function makeRoomStats(size) {
	var emptyChance = clamp(0.18 + size * 0.02, 0.2, 0.35)
	var monsterBase = randInt(1, size + 4)
	var goldBase = randInt(8, size * 10)
	if (Math.random() < emptyChance) return { monsters: 0, gold: 0 }
	return { monsters: randInt(0, monsterBase), gold: randInt(1, goldBase) }
}

function createRandomDungeon(size, options) {
	options = options || {}
	if (!Number.isInteger(size) || size < 4 || size > 6) {
		throw new Error('Dungeon size must be an integer from 4 to 6')
	}
	var grid = []
	for (var i = 0; i < size; i++) {
		grid.push(new Array(size))
		for (var j = 0; j < size; j++) grid[i][j] = null
	}

	var targetRooms = clamp(
		options.roomCount || randInt(size + 4, Math.min(size * size, size * 3 + 4)),
		size + 3,
		size * size,
	)

	var edgeCandidates = []
	for (var x = 0; x < size; x++) {
		edgeCandidates.push({ x: x, y: 0 })
		edgeCandidates.push({ x: x, y: size - 1 })
	}
	for (var y = 1; y < size - 1; y++) {
		edgeCandidates.push({ x: 0, y: y })
		edgeCandidates.push({ x: size - 1, y: y })
	}

	var entry = pick(edgeCandidates)
	var frontiers = []
	var created = []

	function attachRoom(x, y, parent, incomingDir) {
		if (x < 0 || x >= size || y < 0 || y >= size) return null
		var room = new DungeonRoom({
			monsters: makeRoomStats(size).monsters,
			gold: makeRoomStats(size).gold,
			x: x,
			y: y,
			entry: x === entry.x && y === entry.y,
		})
		grid[y][x] = room
		created.push(room)
		if (parent && incomingDir) {
			room.doors[incomingDir.opposite] = true
			parent.doors[incomingDir.name] = true
		}
		frontiers.push(room)
		return room
	}

	attachRoom(entry.x, entry.y)

	while (created.length < targetRooms && frontiers.length > 0) {
		var current = frontiers[randInt(0, frontiers.length - 1)]
		var candidates = shuffle(DIRECTIONS)
			.map(function (dir) {
				return { dir: dir, x: current.x + dir.dx, y: current.y + dir.dy }
			})
			.filter(function (c) {
				return (
					c.x >= 0 && c.x < size && c.y >= 0 && c.y < size && !grid[c.y][c.x]
				)
			})
		if (candidates.length === 0) {
			frontiers.splice(frontiers.indexOf(current), 1)
			continue
		}
		var next = pick(candidates)
		var child = attachRoom(next.x, next.y, current, next.dir)
		if (!child) continue
		if (Math.random() < 0.28) {
			var extras = shuffle(DIRECTIONS)
			for (var ei = 0; ei < extras.length; ei++) {
				var extraDir = extras[ei]
				var ex = child.x + extraDir.dx
				var ey = child.y + extraDir.dy
				if (ex < 0 || ex >= size || ey < 0 || ey >= size) continue
				var neighbor = grid[ey][ex]
				if (!neighbor || neighbor.collapsed) continue
				if (child.doors[extraDir.name]) continue
				if (Math.random() < 0.5) {
					child.doors[extraDir.name] = true
					neighbor.doors[extraDir.opposite] = true
					break
				}
			}
		}
		if (frontiers.length < targetRooms) frontiers.push(current)
	}

	return { grid: grid, entry: entry }
}

function normalizeCell(cell, x, y) {
	if (!cell || cell.collapsed) return null
	var room = cell instanceof DungeonRoom ? cell.clone() : new DungeonRoom(cell)
	room.x = x
	room.y = y
	room.entry = !!cell.entry
	return room
}

function normalizeGrid(grid) {
	if (!Array.isArray(grid) || grid.length === 0 || !Array.isArray(grid[0]))
		throw new Error('Grid must be a non-empty 2D array')
	var size = grid.length
	for (var i = 0; i < grid.length; i++)
		if (!Array.isArray(grid[i]) || grid[i].length !== size)
			throw new Error('Dungeon must be a square grid')
	var out = []
	for (var y = 0; y < grid.length; y++) {
		out[y] = []
		for (var x = 0; x < grid.length; x++)
			out[y][x] = normalizeCell(grid[y][x], x, y)
	}
	return out
}

function isOpenDoor(room, dirName) {
	if (!room) return false
	if (!room.doors) return true
	return !!room.doors[dirName]
}

function buildGraph(grid) {
	var normalized = normalizeGrid(grid)
	var rooms = []
	var byPos = {}
	for (var y = 0; y < normalized.length; y++) {
		for (var x = 0; x < normalized.length; x++) {
			var room = normalized[y][x]
			if (!room) continue
			room.index = rooms.length
			rooms.push(room)
			byPos[keyOf(x, y)] = room
		}
	}
	var edges = []
	for (var ri = 0; ri < rooms.length; ri++) {
		var r = rooms[ri]
		r.neighbors = []
		for (var di = 0; di < DIRECTIONS.length; di++) {
			var dir = DIRECTIONS[di]
			if (!isOpenDoor(r, dir.name)) continue
			var nx = r.x + dir.dx
			var ny = r.y + dir.dy
			var neighbor = byPos[keyOf(nx, ny)]
			if (!neighbor) continue
			if (!isOpenDoor(neighbor, dir.opposite)) continue
			r.neighbors.push(neighbor.index)
		}
		if (isEdgeRoom(r, normalized.length)) edges.push(r.index)
	}
	return { rooms: rooms, edges: edges, size: normalized.length }
}

function isEdgeRoom(room, size) {
	return (
		room.x === 0 || room.y === 0 || room.x === size - 1 || room.y === size - 1
	)
}

function formatCoords(room) {
	return '(' + room.x + ',' + room.y + ')'
}
function formatPath(rooms) {
	return rooms
		.map(function (r) {
			return formatCoords(r)
		})
		.join(' -> ')
}

function buildAction(room, state) {
	return {
		type: 'enter',
		room: { x: room.x, y: room.y },
		hp: state.hp,
		gold: state.gold,
		monsters: room.monsters,
		treasure: room.gold,
	}
}

function buildHealAction(room, hpBefore, hpAfter, goldAfter) {
	return {
		type: 'heal',
		room: { x: room.x, y: room.y },
		hpBefore: hpBefore,
		hpAfter: hpAfter,
		goldAfter: goldAfter,
	}
}

function actionToLine(action) {
	if (action.type === 'enter')
		return (
			'Room [' +
			action.room.x +
			',' +
			action.room.y +
			']: Found ' +
			action.treasure +
			'g, lost ' +
			action.monsters +
			'hp. Status: ' +
			action.hp +
			'hp, ' +
			action.gold +
			'g'
		)
	if (action.type === 'heal')
		return (
			'Room [' +
			action.room.x +
			',' +
			action.room.y +
			']: Spent 100g to heal (' +
			action.hpBefore +
			'hp -> ' +
			action.hpAfter +
			'hp). Status: ' +
			action.hpAfter +
			'hp, ' +
			action.goldAfter +
			'g'
		)
	return 'The tale continues...'
}

function renderDungeon(grid, entry) {
	var normalized = normalizeGrid(grid)
	var size = normalized.length
	var header = []
	header.push('Dungeon ' + size + 'x' + size)
	header.push(
		'Legend: ## collapsed, E entry, -- empty room, g/m = gold/monsters',
	)
	if (entry) header.push('Entry: ' + formatCoords(entry))
	var rows = normalized.map(function (row, y) {
		return row
			.map(function (room, x) {
				if (!room) return ' ## '
				if (entry && room.x === entry.x && room.y === entry.y) return ' E  '
				if (room.gold === 0 && room.monsters === 0) return ' -- '
				var g = String(room.gold)
				if (g.length < 2) g = '0' + g
				var m = String(room.monsters)
				if (m.length < 2) m = '0' + m
				return g + '/' + m
			})
			.join(' ')
	})
	return header.concat(rows).join('\n')
}

function chooseEntryRooms(rooms, edges) {
	return edges.length > 0
		? edges
		: rooms.map(function (r) {
				return r.index
			})
}

function maxDungeonCrawl(grid, hp, options) {
	options = options || {}
	if (!isFinite(hp) || hp <= 0) throw new Error('hp must be a positive number')
	var allowHeal = !!options.allowHeal
	var memo = {}
	var g = buildGraph(grid)
	var rooms = g.rooms
	var edges = g.edges
	if (rooms.length === 0)
		throw new Error('Dungeon must contain at least one accessible room')
	var startCandidates = chooseEntryRooms(rooms, edges)
	var maxHp = options.maxHp || hp
	var totalGold = 0
	for (var i = 0; i < rooms.length; i++) totalGold += rooms[i].gold
	var best = {
		gold: -1,
		hp: 0,
		entry: null,
		path: [],
		actions: [],
		healsUsed: 0,
		exited: false,
	}

	function visitedKey(arr) {
		return arr.join(',')
	}

	for (var si = 0; si < startCandidates.length; si++) {
		var startIndex = startCandidates[si]
		var room = rooms[startIndex]
		var startHp = hp - room.monsters
		var startGold = room.gold
		if (startHp <= 0) continue
		var visited = new Array(rooms.length)
		for (var v = 0; v < visited.length; v++) visited[v] = 0
		visited[startIndex] = 1
		var path = [room]
		var actions = [buildAction(room, { hp: startHp, gold: startGold })]
		var remaining = totalGold - Number(room.gold || 0)

		;(function search(
			currentIndex,
			hpCur,
			goldCur,
			visitedArr,
			pathArr,
			actionsArr,
			healsUsed,
		) {
			var key = currentIndex + '|' + hpCur + '|' + visitedKey(visitedArr)
			if (!allowHeal) {
				if (memo[key] !== undefined && memo[key] >= goldCur) return
				memo[key] = goldCur
			}
			if (goldCur + remaining <= best.gold) return
			var currentRoom = rooms[currentIndex]
			if (goldCur > best.gold || (goldCur === best.gold && hpCur > best.hp)) {
				best = {
					gold: goldCur,
					hp: hpCur,
					entry: { x: pathArr[0].x, y: pathArr[0].y },
					path: pathArr.map(function (r) {
						return { x: r.x, y: r.y }
					}),
					actions: actionsArr.slice(),
					healsUsed: healsUsed,
					exited: true,
				}
			}
			if (allowHeal && goldCur >= 100 && hpCur < maxHp) {
				actionsArr.push(
					buildHealAction(currentRoom, hpCur, maxHp, goldCur - 100),
				)
				search(
					currentIndex,
					maxHp,
					goldCur - 100,
					visitedArr,
					pathArr,
					actionsArr,
					healsUsed + 1,
				)
				actionsArr.pop()
			}
			for (var ni = 0; ni < (currentRoom.neighbors || []).length; ni++) {
				var nextIndex = currentRoom.neighbors[ni]
				if (visitedArr[nextIndex]) continue
				var nextRoom = rooms[nextIndex]
				var nextHp = hpCur - nextRoom.monsters
				if (nextHp <= 0) continue
				var nextGold = goldCur + nextRoom.gold
				visitedArr[nextIndex] = 1
				pathArr.push(nextRoom)
				actionsArr.push(buildAction(nextRoom, { hp: nextHp, gold: nextGold }))
				search(
					nextIndex,
					nextHp,
					nextGold,
					visitedArr,
					pathArr,
					actionsArr,
					healsUsed,
				)
				actionsArr.pop()
				pathArr.pop()
				visitedArr[nextIndex] = 0
			}
		})(startIndex, startHp, startGold, visited, path, actions, 0)
	}
	if (best.gold < 0) throw new Error('Hero cannot survive even the entry room')
	return {
		maxGold: best.gold,
		finalHp: best.hp,
		entry: best.entry,
		path: best.path,
		actions: best.actions,
		song: best.actions.map(actionToLine),
		healsUsed: best.healsUsed,
		exited: best.exited,
		allowHeal: allowHeal,
	}
}

function dungeonCrawl(grid, hp) {
	return maxDungeonCrawl(grid, hp, { allowHeal: false })
}

function compareHealingImpact(grid, hp) {
	var withoutHeal = maxDungeonCrawl(grid, hp, { allowHeal: false })
	var withHeal = maxDungeonCrawl(grid, hp, { allowHeal: true })
	return {
		withoutHeal: withoutHeal,
		withHeal: withHeal,
		delta: withHeal.maxGold - withoutHeal.maxGold,
	}
}

function printRun(title, grid, hp, result) {
	console.log('\n=== ' + title + ' ===')
	console.log(renderDungeon(grid, result.entry))
	console.log('Starting HP: ' + hp)
	console.log('BARD SONGS')
	for (var i = 0; i < result.song.length; i++) console.log(result.song[i])
	console.log('MAX GOLD: ' + result.maxGold)
	console.log('Final HP: ' + result.finalHp)
	console.log('Heals used: ' + result.healsUsed)
	console.log(
		'Path: ' +
			formatPath(
				result.path.map(function (p) {
					return { x: p.x, y: p.y }
				}),
			),
	)
}

if (require.main === module) {
	var size = 5
	var hp = 100
	var game = new DungeonGame(size)
	console.log(game.render())
	var withoutHeal = game.dungeonCrawl(hp)
	var withHeal = game.maxDungeonCrawl(hp)
	printRun('Dungeon crawl without heal (ES5)', game.grid, hp, withoutHeal)
	printRun('Dungeon crawl with heal (ES5)', game.grid, hp, withHeal)
	console.log(
		'\nHealing impact (+gold with heal): ' +
			(withHeal.maxGold - withoutHeal.maxGold),
	)
}

module.exports = {
	DungeonRoom: DungeonRoom,
	DungeonGame: DungeonGame,
	createRandomDungeon: createRandomDungeon,
	dungeonCrawl: dungeonCrawl,
	maxDungeonCrawl: maxDungeonCrawl,
	compareHealingImpact: compareHealingImpact,
	renderDungeon: renderDungeon,
}
