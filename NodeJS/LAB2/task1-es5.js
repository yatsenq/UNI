function BaseCipherES5() {
	this.alphabet = 'abcdefghijklmnopqrstuvwxyz'
}

BaseCipherES5.prototype.validateText = function (text, label) {
	if (typeof text !== 'string') {
		throw new Error(label + ' must be a string')
	}
	if (text.length === 0) {
		throw new Error(label + ' must not be empty')
	}
}

BaseCipherES5.prototype.validateCipherText = function (text) {
	this.validateText(text, 'Cipher text')
	if (!/^[#0-9]+$/.test(text)) {
		throw new Error('Cipher text may contain only digits and #')
	}
}

BaseCipherES5.prototype.encodeLetter = function (letter) {
	const index = this.alphabet.indexOf(letter.toLowerCase())
	if (index === -1) {
		throw new Error('Unsupported character: ' + letter)
	}
	const value = index + 1
	return value <= 9 ? String(value) : '#' + value
}

BaseCipherES5.prototype.decodeToken = function (token) {
	if (!/^(?:[1-9]|#(?:1[0-9]|2[0-6]))$/.test(token)) {
		throw new Error('Invalid token: ' + token)
	}
	const value = Number(token.replace('#', ''))
	return this.alphabet[value - 1]
}

BaseCipherES5.prototype.encrypt = function (text) {
	this.validateText(text, 'Plain text')
	let result = ''
	for (let i = 0; i < text.length; i++) {
		const ch = text[i]
		if (ch === ' ') {
			throw new Error('Base cipher does not support spaces')
		}
		result += this.encodeLetter(ch)
	}
	return result
}

BaseCipherES5.prototype.decrypt = function (text) {
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

function SpecialSymbolCipherES5() {
	BaseCipherES5.call(this)
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
	this.reverseSpecialMap = {}
	for (const key in this.specialMap) {
		this.reverseSpecialMap[this.specialMap[key]] = key
	}
}

SpecialSymbolCipherES5.prototype = Object.create(BaseCipherES5.prototype)
SpecialSymbolCipherES5.prototype.constructor = SpecialSymbolCipherES5

SpecialSymbolCipherES5.prototype.encrypt = function (text) {
	this.validateText(text, 'Plain text')
	let result = ''
	for (let i = 0; i < text.length; i++) {
		const ch = text[i]
		if (/[a-z]/i.test(ch)) {
			result += this.encodeLetter(ch)
		} else if (this.specialMap[ch]) {
			result += this.specialMap[ch]
		} else {
			throw new Error('Unsupported character: ' + ch)
		}
	}
	return result
}

SpecialSymbolCipherES5.prototype.decrypt = function (text) {
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

function CaseAwareCipherES5() {
	BaseCipherES5.call(this)
	this.upperMarker = '#98'
}

CaseAwareCipherES5.prototype = Object.create(BaseCipherES5.prototype)
CaseAwareCipherES5.prototype.constructor = CaseAwareCipherES5

CaseAwareCipherES5.prototype.encrypt = function (text) {
	this.validateText(text, 'Plain text')
	let result = ''
	for (let i = 0; i < text.length; i++) {
		const ch = text[i]
		if (!/[a-z]/i.test(ch)) {
			throw new Error('Unsupported character: ' + ch)
		}
		const token = this.encodeLetter(ch)
		result += ch === ch.toUpperCase() ? this.upperMarker + token : token
	}
	return result
}

CaseAwareCipherES5.prototype.decrypt = function (text) {
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

function demo() {
	const base = new BaseCipherES5()
	const special = new SpecialSymbolCipherES5()
	const caseAware = new CaseAwareCipherES5()

	const basePlain = 'hello'
	const specialPlain = 'hello, world!'
	const casePlain = 'Code'

	console.log('Task 1 ES5')
	console.log(
		basePlain +
			' -> ' +
			base.encrypt(basePlain) +
			' -> ' +
			base.decrypt(base.encrypt(basePlain)),
	)
	console.log(
		specialPlain +
			' -> ' +
			special.encrypt(specialPlain) +
			' -> ' +
			special.decrypt(special.encrypt(specialPlain)),
	)
	console.log(
		casePlain +
			' -> ' +
			caseAware.encrypt(casePlain) +
			' -> ' +
			caseAware.decrypt(caseAware.encrypt(casePlain)),
	)
}

if (require.main === module) {
	demo()
}

module.exports = {
	BaseCipherES5,
	SpecialSymbolCipherES5,
	CaseAwareCipherES5,
}
