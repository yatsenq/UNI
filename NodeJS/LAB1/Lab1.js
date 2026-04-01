const readline = require('readline')

const rl = readline.createInterface({
	input: process.stdin,
	output: process.stdout,
})
const ask = q => new Promise(res => rl.question(q, res))

// Task 1 — Квадратне рівняння
async function task1() {
	console.log('\n=== Завдання 1: Квадратне рівняння ===')

	const a = parseFloat(await ask('Введіть a: '))
	const b = parseFloat(await ask('Введіть b: '))
	const c = parseFloat(await ask('Введіть c: '))

	if (a === 0) {
		console.log('Це не квадратне рівняння (a = 0)')
		return
	}

	const D = b * b - 4 * a * c

	if (D < 0) {
		console.log('Дійсних коренів немає (D < 0)')
	} else if (D === 0) {
		const x = -b / (2 * a)
		console.log(`Один корінь: x = ${x}`)
	} else {
		const x1 = (-b + Math.sqrt(D)) / (2 * a)
		const x2 = (-b - Math.sqrt(D)) / (2 * a)
		console.log(`Два корені: x1 = ${x1}, x2 = ${x2}`)
	}
}

// Task 2 — Найдовший підмасив з чисел у вкладеному масиві
function findLongestNumberSubarray(arr) {
	let longest = []
	let current = []

	function traverse(a) {
		for (const item of a) {
			if (Array.isArray(item)) {
				if (current.length > longest.length) {
					longest = [...current]
				}
				traverse(item)
				if (current.length > longest.length) {
					longest = [...current]
				}
				current = []
			} else if (typeof item === 'number') {
				current.push(item)
			} else {
				if (current.length > longest.length) {
					longest = [...current]
				}
				current = []
			}
		}
	}

	traverse(arr)
	if (current.length > longest.length) {
		longest = [...current]
	}

	return longest
}

async function task2() {
	console.log('\n=== Завдання 2: Найдовший підмасив з чисел ===')
	console.log('1 — тестовий приклад')
	console.log('2 — ввести свій масив')

	const choice = (await ask('Вибір: ')).trim()

	if (choice === '1') {
		const testArrays = [
			[1, 2, [3, 4], 5, 'a', 6, 7],
			[[1, 2], 3, 4, 5, [6, 7, 8]],
			[1, [2, [3, 4, 5]], 'b', 6, 7, 8, 9],
		]
		for (const arr of testArrays) {
			const result = findLongestNumberSubarray(arr)
			console.log(`Масив: ${JSON.stringify(arr)}`)
			console.log(
				`Найдовший підмасив: ${JSON.stringify(result)} (довжина: ${result.length})\n`,
			)
		}
	} else if (choice === '2') {
		console.log(
			'Введіть масив у форматі JSON, наприклад: [1, [2, 3], 4, "a", 5, 6]',
		)
		const raw = await ask('Масив: ')
		try {
			const arr = JSON.parse(raw)
			if (!Array.isArray(arr)) throw new Error()
			const result = findLongestNumberSubarray(arr)
			console.log(`Масив: ${JSON.stringify(arr)}`)
			console.log(
				`Найдовший підмасив: ${JSON.stringify(result)} (довжина: ${result.length})`,
			)
		} catch {
			console.log('Невірний формат JSON.')
		}
	} else {
		console.log('Невірний вибір.')
	}
}

// Task 3 — Скалярний добуток двох векторів
function scalarProduct(v1, v2) {
	if (!Array.isArray(v1) || !Array.isArray(v2)) {
		console.log('Помилка: обидва аргументи мають бути масивами')
		return null
	}

	if (v1.length !== v2.length) {
		console.log(
			`Помилка: вектори мають різні розміри (${v1.length} і ${v2.length})`,
		)
		return null
	}

	let sum = 0
	for (let i = 0; i < v1.length; i++) {
		if (typeof v1[i] !== 'number' || typeof v2[i] !== 'number') {
			console.log('Помилка: координати мають бути числами')
			return null
		}
		sum += v1[i] * v2[i]
	}

	return sum
}

async function task3() {
	console.log('\n=== Завдання 3: Скалярний добуток векторів ===')
	console.log('1 — тестові приклади')
	console.log('2 — ввести свої вектори')

	const choice = (await ask('Вибір: ')).trim()

	if (choice === '1') {
		const testCases = [
			{ v1: [1, 2, 3], v2: [4, 5, 6] },
			{ v1: [2, 0], v2: [3, 4] },
			{ v1: [1, -1, 2], v2: [3, 2, -1] },
			{ v1: [0, 0, 0], v2: [1, 2, 3] },
		]
		for (const { v1, v2 } of testCases) {
			const result = scalarProduct(v1, v2)
			console.log(
				`v1 = ${JSON.stringify(v1)}, v2 = ${JSON.stringify(v2)} → добуток = ${result}`,
			)
		}
	} else if (choice === '2') {
		try {
			const raw1 = await ask('Введіть перший вектор (JSON: [1, 2, 3]): ')
			const v1 = JSON.parse(raw1)
			const raw2 = await ask('Введіть другий вектор (JSON: [4, 5, 6]): ')
			const v2 = JSON.parse(raw2)

			const result = scalarProduct(v1, v2)
			if (result !== null) {
				console.log(
					`Скалярний добуток: ${JSON.stringify(v1)} · ${JSON.stringify(v2)} = ${result}`,
				)
			}
		} catch {
			console.log('Невірний формат JSON.')
		}
	} else {
		console.log('Невірний вибір.')
	}
}

// Task 4
const cars = [
	{
		make: 'Toyota',
		model: 'Camry',
		year: 2022,
		type: 'sedan',
		price: 25000,
		power: 203,
	},
	{
		make: 'BMW',
		model: 'X5',
		year: 2023,
		type: 'SUV',
		price: 65000,
		power: 335,
	},
	{
		make: 'Ford',
		model: 'Mustang',
		year: 2022,
		type: 'coupe',
		price: 52000,
		power: 450,
	},
	{
		make: 'Tesla',
		model: 'Model 3',
		year: 2023,
		type: 'sedan',
		price: 45000,
		power: 283,
	},
	{
		make: 'Mercedes',
		model: 'C-Class',
		year: 2022,
		type: 'sedan',
		price: 42000,
		power: 255,
	},
	{
		make: 'Audi',
		model: 'Q7',
		year: 2022,
		type: 'SUV',
		price: 60000,
		power: 335,
	},
	{
		make: 'Mazda',
		model: 'CX-5',
		year: 2023,
		type: 'SUV',
		price: 32000,
		power: 250,
	},
	{
		make: 'Porsche',
		model: '911',
		year: 2023,
		type: 'coupe',
		price: 120000,
		power: 379,
	},
	{
		make: 'Ford',
		model: 'F-150',
		year: 2023,
		type: 'truck',
		price: 40000,
		power: 290,
	},

	{ make: 'Volkswagen', model: 'Golf', year: 2020, type: 'hatchback' },
	{ make: 'Hyundai', model: 'Elantra', year: 2020, type: 'sedan' },
	{ make: 'Honda', model: 'CR-V', year: 2021, type: 'SUV' },
]

const findByType = type => cars.filter(c => c.type === type)

const findBeforeYear = year => cars.filter(c => c.year <= year)

const findByTypeAndPrice = (type, maxPrice) =>
	cars.filter(c => c.type === type && c.price <= maxPrice)

const findByMakeMinPower = (make, minPower) =>
	cars.filter(c => c.make === make && c.power >= minPower)

const findAfterYearWithPower = (year, minPower) =>
	cars.filter(
		c => c.year > year && c.power !== undefined && c.power >= minPower,
	)

function printCars(label, list) {
	console.log(`\n${label}:`)
	if (!list.length) {
		console.log('  — нічого не знайдено')
		return
	}
	for (const c of list) {
		const pr = c.price !== undefined ? ` | ціна: $${c.price}` : ''
		const pw = c.power !== undefined ? ` | потужність: ${c.power} HP` : ''
		console.log(`  • ${c.make} ${c.model} (${c.type}, ${c.year})${pr}${pw}`)
	}
}

function task4() {
	console.log('\n=== Завдання 4: Пошук машин ===')
	printCars('Тип "sedan"', findByType('sedan'))
	printCars('До 2021 року включно', findBeforeYear(2021))
	printCars('Тип "SUV" + до $40000', findByTypeAndPrice('SUV', 40000))
	printCars('Toyota з потужністю ≥ 200 HP', findByMakeMinPower('Toyota', 200))
	printCars(
		'Після 2021 + потужність ≥ 300 HP',
		findAfterYearWithPower(2021, 300),
	)
}

function printMenu() {
	console.log('=        ОБЕРІТЬ ЗАВДАННЯ      =')
	console.log('=  1 — Квадратне рівняння      =')
	console.log('=  2 — Найдовший підмасив      =')
	console.log('=  3 — Скалярний добуток       =')
	console.log('=  4 — Пошук авто              =')
	console.log('=  0 — Вихід                   =')
}

async function main() {
	let running = true

	while (running) {
		printMenu()
		const choice = (await ask('Ваш вибір: ')).trim()

		switch (choice) {
			case '1':
				await task1()
				break
			case '2':
				await task2()
				break
			case '3':
				await task3()
				break
			case '4':
				task4()
				break
			case '0':
				console.log('exit')
				running = false
				break
			default:
				console.log('Невідомий вибір, спробуйте ще раз.')
		}
	}

	rl.close()
}

main()
