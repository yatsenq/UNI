const WIDTH = 20
const HEIGHT = 12
const DELAY_MS = 600
const MAX_TURNS = 600

const C = {
	reset: '\x1b[0m',
	empty: '\x1b[90m',
	web: '\x1b[33m',
	spider: '\x1b[31m',
	roach: '\x1b[32m',
	food: '\x1b[36m',
	stuckR: '\x1b[35m',
}

const rnd = n => Math.floor(Math.random() * n)
const dist = (a, b) => Math.abs(a.x - b.x) + Math.abs(a.y - b.y)
const inBounds = (x, y) => x >= 0 && x < WIDTH && y >= 0 && y < HEIGHT

const DIRS = [
	{ dx: 0, dy: -1 },
	{ dx: 0, dy: 1 },
	{ dx: -1, dy: 0 },
	{ dx: 1, dy: 0 },
]

const ADJ8 = [
	{ dx: -1, dy: -1 },
	{ dx: 0, dy: -1 },
	{ dx: 1, dy: -1 },
	{ dx: -1, dy: 0 },
	{ dx: 1, dy: 0 },
	{ dx: -1, dy: 1 },
	{ dx: 0, dy: 1 },
	{ dx: 1, dy: 1 },
]

let grid = []
let spiders = []
let roaches = []
let foods = []
let nextId = 1
let turn = 0

function uid() {
	return nextId++
}

function initGrid() {
	grid = Array.from({ length: HEIGHT }, () => Array(WIDTH).fill(null))
}

function isFreeCell(x, y, excludeRoach = null) {
	if (!inBounds(x, y)) return false
	if (spiders.find(s => s.x === x && s.y === y)) return false
	if (roaches.find(r => r !== excludeRoach && r.x === x && r.y === y))
		return false
	return true
}

function isFreeForFood(x, y) {
	if (!inBounds(x, y)) return false
	if (grid[y][x] === 'web') return false
	if (spiders.find(s => s.x === x && s.y === y)) return false
	if (roaches.find(r => r.x === x && r.y === y)) return false
	if (foods.find(f => f.x === x && f.y === y)) return false
	return true
}

function hasSpiderAt(x, y, excludeSpider = null) {
	return spiders.some(s => s !== excludeSpider && s.x === x && s.y === y)
}

function hasRoachAt(x, y, excludeRoach = null) {
	return roaches.some(r => r !== excludeRoach && r.x === x && r.y === y)
}

function place(count, factory) {
	for (let i = 0; i < count; i++) {
		let x, y
		do {
			x = rnd(WIDTH)
			y = rnd(HEIGHT)
		} while (!isFreeCell(x, y))
		factory(x, y)
	}
}

function placeFood(count) {
	for (let i = 0; i < count; i++) {
		let x,
			y,
			attempts = 0
		do {
			x = rnd(WIDTH)
			y = rnd(HEIGHT)
			attempts++
		} while (!isFreeForFood(x, y) && attempts < 200)
		if (attempts < 200) foods.push({ id: uid(), x, y })
	}
}

function init() {
	initGrid()
	spiders = []
	roaches = []
	foods = []
	nextId = 1
	turn = 0

	place(3, (x, y) => spiders.push({ id: uid(), x, y, eating: null }))
	place(6, (x, y) => roaches.push({ id: uid(), x, y, stuck: false }))
	place(10, (x, y) => {
		if (grid[y][x] === null) grid[y][x] = 'web'
	})

	for (const s of spiders) {
		for (const d of DIRS) {
			const nx = s.x + d.dx,
				ny = s.y + d.dy
			if (inBounds(nx, ny) && grid[ny][nx] === null && isFreeCell(nx, ny)) {
				grid[ny][nx] = 'web'
			}
		}
	}

	placeFood(4)
}

function render() {
	process.stdout.write('\x1b[2J\x1b[H') //очищає весь екран, переміщує курсор в позицію (0,0) — верхній лівий кут
	console.log(`${'─'.repeat(WIDTH * 2 + 2)}`)
	console.log(
		` Хід: ${turn}  |  Таргани: ${roaches.length}  |  Павуки: ${spiders.length}`,
	)
	console.log(`${'─'.repeat(WIDTH * 2 + 2)}`)

	for (let y = 0; y < HEIGHT; y++) {
		let row = '│'
		for (let x = 0; x < WIDTH; x++) {
			const spider = spiders.find(s => s.x === x && s.y === y)
			const roach = roaches.find(r => r.x === x && r.y === y)
			const food = foods.find(f => f.x === x && f.y === y)
			const isWeb = grid[y][x] === 'web'

			if (spider) row += C.spider + 'X ' + C.reset
			else if (roach && roach.stuck) row += C.stuckR + '& ' + C.reset
			else if (roach) row += C.roach + '@ ' + C.reset
			else if (food) row += C.food + '0 ' + C.reset
			else if (isWeb) row += C.web + '# ' + C.reset
			else row += C.empty + '. ' + C.reset
		}
		row += '│'
		console.log(row)
	}

	console.log(`${'─'.repeat(WIDTH * 2 + 2)}`)
	console.log(
		`${C.spider}X${C.reset} павук  ${C.roach}@${C.reset} тарган  ${C.stuckR}&${C.reset} застряглий  ${C.web}#${C.reset} павутина  ${C.food}0${C.reset} їжа`,
	)
}

function killNearestSpider(origin) {
	if (spiders.length === 0) return
	let index = 0,
		best = dist(spiders[0], origin)
	for (let i = 1; i < spiders.length; i++) {
		const d = dist(spiders[i], origin)
		if (d < best) {
			best = d
			index = i
		}
	}
	spiders.splice(index, 1)
}

function processRescues() {
	for (const victim of roaches) {
		if (!victim.stuck) continue
		if (grid[victim.y][victim.x] !== 'web') {
			victim.stuck = false
			continue
		}

		const helpers = roaches.filter(r => {
			if (r.stuck || r.id === victim.id) return false
			return ADJ8.some(d => r.x === victim.x + d.dx && r.y === victim.y + d.dy)
		})

		if (helpers.length >= 2) {
			grid[victim.y][victim.x] = null
			victim.stuck = false
			killNearestSpider(victim)
		}
	}
}

function moveRoach(roach) {
	if (roach.stuck) return

	const adjVictim = roaches.find(
		//1
		r =>
			r.stuck &&
			ADJ8.some(d => r.x === roach.x + d.dx && r.y === roach.y + d.dy),
	)
	if (adjVictim) {
		const helpersNear = roaches.filter(r => {
			if (r.stuck || r.id === roach.id) return false
			return ADJ8.some(
				d => r.x === adjVictim.x + d.dx && r.y === adjVictim.y + d.dy,
			)
		}).length
		if (helpersNear >= 2) return
	}

	const stuckNear = roaches //2
		.filter(r => {
			if (!r.stuck || dist(roach, r) > 4) return false
			const alreadyAdj = ADJ8.some(
				d => r.x === roach.x + d.dx && r.y === roach.y + d.dy,
			)
			return !alreadyAdj
		})
		.sort((a, b) => dist(roach, a) - dist(roach, b))[0]
	if (stuckNear) {
		if (tryMoveRoach(roach, stuckNear, 2)) return
	}

	const nearFood = foods //3
		.filter(f => dist(roach, f) <= 6)
		.sort((a, b) => dist(roach, a) - dist(roach, b))[0]
	if (nearFood) {
		if (tryMoveRoach(roach, nearFood, 2)) return
	}

	for (let step = 0; step < 2; step++) {
		//4
		const dirs = [...DIRS].sort(() => Math.random() - 0.5)
		let moved = false
		for (const d of dirs) {
			const nx = roach.x + d.dx,
				ny = roach.y + d.dy
			if (!inBounds(nx, ny)) continue
			if (hasSpiderAt(nx, ny)) continue
			if (hasRoachAt(nx, ny, roach)) continue
			applyRoachMove(roach, nx, ny)
			moved = true
			break
		}
		if (!moved || roach.stuck) break
	}
}

function tryMoveRoach(roach, target, steps) {
	let anyMoved = false
	for (let i = 0; i < steps; i++) {
		if (roach.stuck) break
		const dx = target.x - roach.x
		const dy = target.y - roach.y
		if (dx === 0 && dy === 0) break

		const candidates = []
		if (Math.abs(dx) >= Math.abs(dy)) {
			if (dx !== 0) candidates.push({ dx: Math.sign(dx), dy: 0 }) //горизонтально
			if (dy !== 0) candidates.push({ dx: 0, dy: Math.sign(dy) })
		} else {
			if (dy !== 0) candidates.push({ dx: 0, dy: Math.sign(dy) }) //вертикально
			if (dx !== 0) candidates.push({ dx: Math.sign(dx), dy: 0 })
		}
		for (const d of DIRS) {
			if (!candidates.find(c => c.dx === d.dx && c.dy === d.dy))
				candidates.push(d)
		}

		let moved = false
		for (const d of candidates) {
			const nx = roach.x + d.dx,
				ny = roach.y + d.dy
			if (!inBounds(nx, ny)) continue
			if (hasSpiderAt(nx, ny)) continue
			if (hasRoachAt(nx, ny, roach)) continue
			applyRoachMove(roach, nx, ny)
			moved = true
			anyMoved = true
			break
		}
		if (!moved) break
	}
	return anyMoved
}

function applyRoachMove(roach, nx, ny) {
	roach.x = nx
	roach.y = ny

	if (grid[ny][nx] === 'web') {
		roach.stuck = true
		return
	}

	const fi = foods.findIndex(f => f.x === nx && f.y === ny)
	if (fi !== -1) {
		foods.splice(fi, 1)
		let born = 0
		const shuffled = [...DIRS].sort(() => Math.random() - 0.5)
		for (const d of shuffled) {
			if (born >= 2) break
			const bx = nx + d.dx,
				by = ny + d.dy
			if (isFreeCell(bx, by)) {
				roaches.push({ id: uid(), x: bx, y: by, stuck: false })
				born++
			}
		}
	}
}

function moveSpider(spider) {
	if (spider.eating) {
		const target = roaches.find(r => r.id === spider.eating.roachId)
		if (!target || dist(spider, target) !== 1) {
			spider.eating = null
		} else {
			spider.eating.turns++
			if (spider.eating.turns >= 3) {
				const ri = roaches.findIndex(r => r.id === target.id)
				if (ri !== -1) roaches.splice(ri, 1)
				spider.x = target.x
				spider.y = target.y
				spider.eating = null
			}
			return
		}
	}

	const neighbor = roaches.find(r => dist(spider, r) === 1) //1
	if (neighbor) {
		spider.eating = { roachId: neighbor.id, turns: 1 }
		return
	}

	const stuckViaWeb = roaches //2
		.filter(r => r.stuck && isWebConnected(spider, r))
		.sort((a, b) => dist(spider, a) - dist(spider, b))[0]
	if (stuckViaWeb) {
		moveSpiderToward(spider, stuckViaWeb)
		return
	}

	const anyRoach = roaches.sort((a, b) => dist(spider, a) - dist(spider, b))[0]
	if (anyRoach) {
		if (dist(spider, anyRoach) <= 6) {
			moveSpiderToward(spider, anyRoach)
			return
		}
	}

	const emptyAdj = DIRS.map(d => ({
		//3
		x: spider.x + d.dx,
		y: spider.y + d.dy,
	})).filter(
		p => inBounds(p.x, p.y) && grid[p.y][p.x] === null && isFreeCell(p.x, p.y),
	)

	if (emptyAdj.length > 0) {
		const target = emptyAdj[rnd(emptyAdj.length)]
		spider.x = target.x
		spider.y = target.y
		grid[target.y][target.x] = 'web'
	} else {
		// немає пустих сусідніх, шукаємо на всьому полі
		let best = null,
			bestD = Infinity
		for (let y = 0; y < HEIGHT; y++) {
			for (let x = 0; x < WIDTH; x++) {
				if (grid[y][x] === null && isFreeCell(x, y)) {
					const d = dist(spider, { x, y })
					if (d < bestD) {
						bestD = d
						best = { x, y }
					}
				}
			}
		}
		if (best) {
			const options = DIRS.map(d => ({
				x: spider.x + d.dx,
				y: spider.y + d.dy,
			}))
				.filter(p => inBounds(p.x, p.y) && !hasSpiderAt(p.x, p.y, spider))
				.sort((a, b) => dist(a, best) - dist(b, best))
			if (options.length > 0) {
				spider.x = options[0].x
				spider.y = options[0].y
				grid[spider.y][spider.x] = 'web'
			}
		}
	}
}

function moveSpiderToward(spider, target) {
	const options = DIRS.map(d => ({ x: spider.x + d.dx, y: spider.y + d.dy }))
		.filter(p => inBounds(p.x, p.y) && !hasSpiderAt(p.x, p.y, spider))
		.sort((a, b) => dist(a, target) - dist(b, target))
	if (options.length > 0) {
		spider.x = options[0].x
		spider.y = options[0].y
	}
}

function isWebConnected(spider, target) {
	if (grid[target.y][target.x] !== 'web') return false

	const visited = new Set()
	const queue = []

	for (const d of DIRS) {
		const nx = spider.x + d.dx,
			ny = spider.y + d.dy
		if (inBounds(nx, ny) && grid[ny][nx] === 'web') {
			const key = `${nx},${ny}`
			visited.add(key)
			queue.push({ x: nx, y: ny })
		}
	}

	while (queue.length) {
		const cur = queue.shift()
		if (cur.x === target.x && cur.y === target.y) return true
		for (const d of DIRS) {
			const nx = cur.x + d.dx,
				ny = cur.y + d.dy
			const key = `${nx},${ny}`
			if (inBounds(nx, ny) && !visited.has(key) && grid[ny][nx] === 'web') {
				visited.add(key)
				queue.push({ x: nx, y: ny })
			}
		}
	}
	return false
}

function gameTick() {
	turn++
	processRescues()

	const roachOrder = [...roaches].sort(() => Math.random() - 0.5)
	for (const r of roachOrder) {
		if (roaches.find(x => x.id === r.id)) moveRoach(r)
	}

	processRescues()

	for (const s of [...spiders]) {
		if (spiders.find(x => x.id === s.id)) moveSpider(s)
	}
}

function sleep(ms) {
	return new Promise(res => setTimeout(res, ms))
}

async function main() {
	init()
	render()

	while (roaches.length > 0 && spiders.length > 0 && turn < MAX_TURNS) {
		await sleep(DELAY_MS)
		gameTick()
		render()
	}

	if (roaches.length === 0 && spiders.length > 0) {
		console.log(
			`\n${C.spider}Павуки перемогли! Всіх тарганів знищено за ${turn} ходів.${C.reset}\n`,
		)
	} else if (spiders.length === 0 && roaches.length > 0) {
		console.log(
			`\n${C.roach}Таргани перемогли! Усі павуки знищені за ${turn} ходів.${C.reset}\n`,
		)
	} else {
		console.log(
			`\n${C.empty}Нічия! Гра завершена після ${MAX_TURNS} ходів. Таргани: ${roaches.length}, Павуки: ${spiders.length}${C.reset}\n`,
		)
	}
}

main()
