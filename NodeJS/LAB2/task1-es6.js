class BaseCipher {
	constructor() {
		this.alphabet = 'abcdefghijklmnopqrstuvwxyz'
	}

	validateText(text, label) {
		if (typeof text !== 'string') {
			throw new Error(`${label} must be a string`)
		}
		if (text.length === 0) {
			throw new Error(`${label} must not be empty`)
		}
	}

	validateCipherText(text) {
		this.validateText(text, 'Cipher text')
		if (!/^[#0-9]+$/.test(text)) {
			throw new Error('Cipher text may contain only digits and #')
		}
	}

	encodeLetter(letter) {
		const index = this.alphabet.indexOf(letter.toLowerCase())
		if (index === -1) {
			throw new Error(`Unsupported character: ${letter}`)
		}
		const value = index + 1
		return value <= 9 ? String(value) : `#${value}`
	}

	decodeToken(token) {
		if (!/^(?:[1-9]|#(?:1[0-9]|2[0-6]))$/.test(token)) {
			throw new Error(`Invalid token: ${token}`)
		}
		const value = Number(token.replace('#', ''))
		return this.alphabet[value - 1]
	}

	encrypt(text) {
		this.validateText(text, 'Plain text')
		return Array.from(text)
			.map(ch => {
				if (ch === ' ') {
					throw new Error('Base cipher does not support spaces')
				}
				return this.encodeLetter(ch)
			})
			.join('')
	}

	decrypt(text) {
		this.validateCipherText(text)
		let result = ''
		for (let i = 0; i < text.length; ) {
			if (text[i] === '#') {
				const token = text.slice(i, i + 3)
				result += this.decodeToken(token)
				i += 3
			} else {
				const token = text[i]
				result += this.decodeToken(token)
				i += 1
			}
		}
		return result
	}
}

class SpecialSymbolCipher extends BaseCipher {
	constructor() {
		super()
		this.specialMap = {
			' ': '#27',
			'.': '#28',
			',': '#29',
			'!': '#30',
			'?': '#31',
			':': '#32',
			';': '#33',
			'-': '#34',
			"'": '#35',
			'(': '#36',
			')': '#37',
		}
		this.reverseSpecialMap = Object.fromEntries(
			Object.entries(this.specialMap).map(([symbol, code]) => [code, symbol]),
		)
	}

	encrypt(text) {
		this.validateText(text, 'Plain text')
		return Array.from(text)
			.map(ch => {
				if (/[a-z]/i.test(ch)) {
					return this.encodeLetter(ch)
				}
				if (this.specialMap[ch]) {
					return this.specialMap[ch]
				}
				throw new Error(`Unsupported character: ${ch}`)
			})
			.join('')
	}

	decrypt(text) {
		this.validateCipherText(text)
		let result = ''
		for (let i = 0; i < text.length; ) {
			if (text[i] === '#') {
				const token = text.slice(i, i + 3)
				if (this.reverseSpecialMap[token]) {
					result += this.reverseSpecialMap[token]
				} else {
					result += this.decodeToken(token)
				}
				i += 3
			} else {
				result += this.decodeToken(text[i])
				i += 1
			}
		}
		return result
	}
}

class CaseAwareCipher extends BaseCipher {
	constructor() {
		super()
		this.upperMarker = '#98'
	}

	encrypt(text) {
		this.validateText(text, 'Plain text')
		return Array.from(text)
			.map(ch => {
				if (!/[a-z]/i.test(ch)) {
					throw new Error(`Unsupported character: ${ch}`)
				}
				const token = this.encodeLetter(ch)
				return ch === ch.toUpperCase() ? `${this.upperMarker}${token}` : token
			})
			.join('')
	}

	decrypt(text) {
		this.validateCipherText(text)
		let result = ''
		for (let i = 0; i < text.length; ) {
			let upper = false
			if (text.slice(i, i + 3) === this.upperMarker) {
				upper = true
				i += 3
			}
			const token = text[i] === '#' ? text.slice(i, i + 3) : text[i]
			const decoded = this.decodeToken(token)
			result += upper ? decoded.toUpperCase() : decoded
			i += token.length
		}
		return result
	}
}

function demo() {
	const base = new BaseCipher()
	const special = new SpecialSymbolCipher()
	const caseAware = new CaseAwareCipher()

	const basePlain = 'hello'
	const specialPlain = 'hello, world!'
	const casePlain = 'Code'

	console.log('Task 1 ES6')
	console.log(
		`${basePlain} -> ${base.encrypt(basePlain)} -> ${base.decrypt(base.encrypt(basePlain))}`,
	)
	console.log(
		`${specialPlain} -> ${special.encrypt(specialPlain)} -> ${special.decrypt(special.encrypt(specialPlain))}`,
	)
	console.log(
		`${casePlain} -> ${caseAware.encrypt(casePlain)} -> ${caseAware.decrypt(caseAware.encrypt(casePlain))}`,
	)
}

if (require.main === module) {
	demo()
}

module.exports = {
	BaseCipher,
	SpecialSymbolCipher,
	CaseAwareCipher,
}
