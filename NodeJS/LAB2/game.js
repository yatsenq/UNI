const DIRECTIONS = [
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
	const copy = [...array]
	for (let i = copy.length - 1; i > 0; i--) {
		const j = randInt(0, i)
		;[copy[i], copy[j]] = [copy[j], copy[i]]
	}
	return copy
}

function keyOf(x, y) {
	return `${x},${y}`
}

function clamp(value, min, max) {
	return Math.max(min, Math.min(max, value))
}

class DungeonRoom {
	constructor({
		monsters = 0,
		gold = 0,
		collapsed = false,
		doors = null,
		x = 0,
		y = 0,
		entry = false,
	}) {
		this.monsters = monsters
		this.gold = gold
		this.collapsed = collapsed
		this.doors = doors || { N: false, E: false, S: false, W: false }
		this.x = x
		this.y = y
		this.entry = entry
	}

	clone() {
		return new DungeonRoom({
			monsters: this.monsters,
			gold: this.gold,
			collapsed: this.collapsed,
			doors: { ...this.doors },
			x: this.x,
			y: this.y,
			entry: this.entry,
		})
	}

	doorCount() {
		return Object.values(this.doors).filter(Boolean).length
	}
}

class DungeonGame {
	constructor(size = 5, options = {}) {
		if (!Number.isInteger(size) || size < 4 || size > 6) {
			throw new Error('Dungeon size must be an integer from 4 to 6')
		}

		this.size = size
		this.options = options
		const generated = createRandomDungeon(size, options)
		this.grid = generated.grid
		this.entry = generated.entry
	}

	render() {
		return renderDungeon(this.grid, this.entry)
	}

	dungeonCrawl(hp, options = {}) {
		return maxDungeonCrawl(this.grid, hp, { ...options, allowHeal: false })
	}

	maxDungeonCrawl(hp, options = {}) {
		return maxDungeonCrawl(this.grid, hp, { ...options, allowHeal: true })
	}
}

function makeRoomStats(size) {
	const emptyChance = clamp(0.18 + size * 0.02, 0.2, 0.35)
	const monsterBase = randInt(1, size + 4)
	const goldBase = randInt(8, size * 10)

	if (Math.random() < emptyChance) {
		return { monsters: 0, gold: 0 }
	}

	return {
		monsters: randInt(0, monsterBase),
		gold: randInt(1, goldBase),
	}
}

function createRandomDungeon(size = 5, options = {}) {
	if (!Number.isInteger(size) || size < 4 || size > 6) {
		throw new Error('Dungeon size must be an integer from 4 to 6')
	}

	const grid = Array.from({ length: size }, () => Array(size).fill(null))
	const targetRooms = clamp(
		options.roomCount ?? randInt(size + 4, Math.min(size * size, size * 3 + 4)),
		size + 3,
		size * size,
	)

	const edgeCandidates = []
	for (let x = 0; x < size; x++) {
		edgeCandidates.push({ x, y: 0 })
		edgeCandidates.push({ x, y: size - 1 })
	}
	for (let y = 1; y < size - 1; y++) {
		edgeCandidates.push({ x: 0, y })
		edgeCandidates.push({ x: size - 1, y })
	}

	const entry = pick(edgeCandidates)
	const frontiers = []
	const created = []

	function attachRoom(x, y, parent = null, incomingDir = null) {
		if (x < 0 || x >= size || y < 0 || y >= size) return null
		const room = new DungeonRoom({
			...makeRoomStats(size),
			x,
			y,
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
		const current = frontiers[randInt(0, frontiers.length - 1)]
		const candidates = shuffle(DIRECTIONS)
			.map(dir => ({ dir, x: current.x + dir.dx, y: current.y + dir.dy }))
			.filter(
				({ x, y }) => x >= 0 && x < size && y >= 0 && y < size && !grid[y][x],
			)

		if (candidates.length === 0) {
			frontiers.splice(frontiers.indexOf(current), 1)
			continue
		}

		const next = pick(candidates)
		const child = attachRoom(next.x, next.y, current, next.dir)
		if (!child) continue

		if (Math.random() < 0.28) {
			const extras = shuffle(DIRECTIONS)
			for (const extraDir of extras) {
				const ex = child.x + extraDir.dx
				const ey = child.y + extraDir.dy
				if (ex < 0 || ex >= size || ey < 0 || ey >= size) continue
				const neighbor = grid[ey][ex]
				if (!neighbor || neighbor.collapsed) continue
				if (child.doors[extraDir.name]) continue
				if (Math.random() < 0.5) {
					child.doors[extraDir.name] = true
					neighbor.doors[extraDir.opposite] = true
					break
				}
			}
		}

		if (frontiers.length < targetRooms) {
			frontiers.push(current)
		}
	}

	return { grid, entry }
}

function normalizeCell(cell, x, y) {
	if (!cell || cell.collapsed) return null

	const room =
		cell instanceof DungeonRoom ? cell.clone() : new DungeonRoom(cell)
	room.x = x
	room.y = y
	room.entry = Boolean(cell.entry)
	return room
}

function normalizeGrid(grid) {
	if (!Array.isArray(grid) || grid.length === 0 || !Array.isArray(grid[0])) {
		throw new Error('Grid must be a non-empty 2D array')
	}

	const size = grid.length
	if (!grid.every(row => Array.isArray(row) && row.length === size)) {
		throw new Error('Dungeon must be a square grid')
	}

	return grid.map((row, y) => row.map((cell, x) => normalizeCell(cell, x, y)))
}

function isOpenDoor(room, dirName) {
	if (!room) return false
	if (!room.doors) return true
	return Boolean(room.doors[dirName])
}

function buildGraph(grid) {
	const normalized = normalizeGrid(grid)
	const rooms = []
	const byPos = new Map()

	for (let y = 0; y < normalized.length; y++) {
		for (let x = 0; x < normalized.length; x++) {
			const room = normalized[y][x]
			if (!room) continue
			room.index = rooms.length
			rooms.push(room)
			byPos.set(keyOf(x, y), room)
		}
	}

	const edges = []
	for (const room of rooms) {
		room.neighbors = []
		for (const dir of DIRECTIONS) {
			if (!isOpenDoor(room, dir.name)) continue
			const nx = room.x + dir.dx
			const ny = room.y + dir.dy
			const neighbor = byPos.get(keyOf(nx, ny))
			if (!neighbor) continue
			if (!isOpenDoor(neighbor, dir.opposite)) continue
			room.neighbors.push(neighbor.index)
		}
		if (isEdgeRoom(room, normalized.length)) {
			edges.push(room.index)
		}
	}

	return { rooms, edges, size: normalized.length }
}

function isEdgeRoom(room, size) {
	return (
		room.x === 0 || room.y === 0 || room.x === size - 1 || room.y === size - 1
	)
}

function formatCoords(room) {
	return `(${room.x},${room.y})`
}

function formatPath(rooms) {
	return rooms.map(formatCoords).join(' -> ')
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
		hpBefore,
		hpAfter,
		goldAfter,
	}
}

function actionToLine(action) {
	if (action.type === 'enter') {
		return `Room [${action.room.x},${action.room.y}]: Found ${action.treasure}g, lost ${action.monsters}hp. Status: ${action.hp}hp, ${action.gold}g`
	}
	if (action.type === 'heal') {
		return `Room [${action.room.x},${action.room.y}]: Spent 100g to heal (${action.hpBefore}hp -> ${action.hpAfter}hp). Status: ${action.hpAfter}hp, ${action.goldAfter}g`
	}
	return 'The tale continues...'
}

function renderDungeon(grid, entry = null) {
	const normalized = normalizeGrid(grid)
	const size = normalized.length
	const header = []
	header.push(`Dungeon ${size}x${size}`)
	header.push(
		'Legend: ## collapsed, E entry, -- empty room, g/m = gold/monsters',
	)
	if (entry) header.push(`Entry: ${formatCoords(entry)}`)

	const rows = normalized.map((row, y) => {
		return row
			.map((room, x) => {
				if (!room) return ' ## '
				if (entry && room.x === entry.x && room.y === entry.y) return ' E  '
				if (room.gold === 0 && room.monsters === 0) return ' -- '
				return `${String(room.gold).padStart(2, '0')}/${String(room.monsters).padStart(2, '0')}`
			})
			.join(' ')
	})

	return [...header, ...rows].join('\n')
}

function chooseEntryRooms(rooms, edges) {
	if (edges.length > 0) return edges
	return rooms.map(room => room.index)
}

function maxDungeonCrawl(grid, hp, options = {}) {
	if (!Number.isFinite(hp) || hp <= 0) {
		throw new Error('hp must be a positive number')
	}

	const allowHeal = Boolean(options.allowHeal)
	if (!allowHeal) {
		search.memo = new Map()
	}
	const { rooms, edges } = buildGraph(grid)
	if (rooms.length === 0) {
		throw new Error('Dungeon must contain at least one accessible room')
	}

	const startCandidates = chooseEntryRooms(rooms, edges)
	const maxHp = options.maxHp ?? hp
	const totalGold = rooms.reduce((sum, room) => sum + room.gold, 0)

	let best = {
		gold: -1,
		hp: 0,
		entry: null,
		path: [],
		actions: [],
		healsUsed: 0,
		exited: false,
	}

	for (const startIndex of startCandidates) {
		const room = rooms[startIndex]
		const startHp = hp - room.monsters
		const startGold = room.gold
		if (startHp <= 0) continue

		const startMask = 1n << BigInt(room.index)
		const startRemaining = totalGold - room.gold
		const path = [room]
		const actions = [buildAction(room, { hp: startHp, gold: startGold })]

		search({
			rooms,
			currentIndex: room.index,
			hp: startHp,
			gold: startGold,
			remainingGold: startRemaining,
			visitedMask: startMask,
			path,
			actions,
			healsUsed: 0,
			allowHeal,
			maxHp,
			bestRef: best,
			updateBest(next) {
				best = next
			},
		})
	}

	if (best.gold < 0) {
		throw new Error('Hero cannot survive even the entry room')
	}

	return {
		maxGold: best.gold,
		finalHp: best.hp,
		entry: best.entry,
		path: best.path,
		actions: best.actions,
		song: best.actions.map(actionToLine),
		healsUsed: best.healsUsed,
		exited: best.exited,
		allowHeal,
	}
}

function search(state) {
	const {
		rooms,
		currentIndex,
		hp,
		gold,
		remainingGold,
		visitedMask,
		path,
		actions,
		healsUsed,
		allowHeal,
		maxHp,
		bestRef,
		updateBest,
	} = state

	const key = allowHeal
		? `${currentIndex}|${hp}|${gold}|${visitedMask.toString()}`
		: `${currentIndex}|${hp}|${visitedMask.toString()}`

	if (!allowHeal) {
		if (!search.memo) search.memo = new Map()
		const memo = search.memo
		const prevBest = memo.get(key)
		if (prevBest !== undefined && prevBest >= gold) return
		memo.set(key, gold)
	}

	if (gold + remainingGold <= bestRef.gold) return

	const currentRoom = rooms[currentIndex]
	const canStop =
		gold > bestRef.gold || (gold === bestRef.gold && hp > bestRef.hp)
	if (canStop) {
		updateBest({
			gold,
			hp,
			entry: path[0] ? { x: path[0].x, y: path[0].y } : null,
			path: path.map(room => ({ x: room.x, y: room.y })),
			actions: [...actions],
			healsUsed,
			exited: true,
		})
	}

	if (allowHeal && gold >= 100 && hp < maxHp) {
		actions.push(buildHealAction(currentRoom, hp, maxHp, gold - 100))
		search({
			rooms,
			currentIndex,
			hp: maxHp,
			gold: gold - 100,
			remainingGold,
			visitedMask,
			path,
			actions,
			healsUsed: healsUsed + 1,
			allowHeal,
			maxHp,
			bestRef,
			updateBest,
		})
		actions.pop()
	}

	for (const nextIndex of currentRoom.neighbors || []) {
		const bit = 1n << BigInt(nextIndex)
		if (visitedMask & bit) continue

		const nextRoom = rooms[nextIndex]
		const nextHp = hp - nextRoom.monsters
		if (nextHp <= 0) continue

		const nextGold = gold + nextRoom.gold
		const nextRemaining = remainingGold - nextRoom.gold
		path.push(nextRoom)
		actions.push(buildAction(nextRoom, { hp: nextHp, gold: nextGold }))
		search({
			rooms,
			currentIndex: nextIndex,
			hp: nextHp,
			gold: nextGold,
			remainingGold: nextRemaining,
			visitedMask: visitedMask | bit,
			path,
			actions,
			healsUsed,
			allowHeal,
			maxHp,
			bestRef,
			updateBest,
		})
		actions.pop()
		path.pop()
	}
}

function dungeonCrawl(grid, hp) {
	return maxDungeonCrawl(grid, hp, { allowHeal: false })
}

function compareHealingImpact(grid, hp) {
	const withoutHeal = maxDungeonCrawl(grid, hp, { allowHeal: false })
	const withHeal = maxDungeonCrawl(grid, hp, { allowHeal: true })
	return {
		withoutHeal,
		withHeal,
		delta: withHeal.maxGold - withoutHeal.maxGold,
	}
}

function printRun(title, grid, hp, result) {
	console.log(`\n=== ${title} ===`)
	console.log(renderDungeon(grid, result.entry))
	console.log(`Starting HP: ${hp}`)
	console.log('BARD SONGS')
	for (const line of result.song) {
		console.log(line)
	}
	console.log(`MAX GOLD: ${result.maxGold}`)
	console.log(`Final HP: ${result.finalHp}`)
	console.log(`Heals used: ${result.healsUsed}`)
	console.log(`Path: ${formatPath(result.path.map(p => ({ x: p.x, y: p.y })))}`)
}

if (require.main === module) {
	const size = 5
	const hp = 100
	const game = new DungeonGame(size)

	console.log(game.render())

	const withoutHeal = game.dungeonCrawl(hp)
	const withHeal = game.maxDungeonCrawl(hp)

	printRun('Dungeon crawl without heal', game.grid, hp, withoutHeal)
	printRun('Dungeon crawl with heal', game.grid, hp, withHeal)
	console.log(
		`\nHealing impact (+gold with heal): ${withHeal.maxGold - withoutHeal.maxGold}`,
	)
}

module.exports = {
	DungeonRoom,
	DungeonGame,
	createRandomDungeon,
	dungeonCrawl,
	maxDungeonCrawl,
	compareHealingImpact,
	renderDungeon,
}
