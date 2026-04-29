function ShipmentES5(sender, destination, weightKg, distanceKm, baseRatePerKm) {
	this.sender = sender
	this.destination = destination
	this.weightKg = weightKg
	this.distanceKm = distanceKm
	this.baseRatePerKm = baseRatePerKm
}

ShipmentES5.prototype.validateBaseState = function () {
	if (typeof this.sender !== 'string' || this.sender.trim().length === 0) {
		throw new Error('sender must be a non-empty string')
	}
	if (
		typeof this.destination !== 'string' ||
		this.destination.trim().length === 0
	) {
		throw new Error('destination must be a non-empty string')
	}
	if (!Number.isFinite(this.weightKg) || this.weightKg <= 0) {
		throw new Error('weightKg must be a positive number')
	}
	if (!Number.isFinite(this.distanceKm) || this.distanceKm <= 0) {
		throw new Error('distanceKm must be a positive number')
	}
	if (!Number.isFinite(this.baseRatePerKm) || this.baseRatePerKm <= 0) {
		throw new Error('baseRatePerKm must be a positive number')
	}
}

ShipmentES5.prototype.estimateTravelHours = function (speedKmH) {
	this.validateBaseState()
	if (!Number.isFinite(speedKmH) || speedKmH <= 0) {
		throw new Error('speedKmH must be a positive number')
	}
	return this.distanceKm / speedKmH
}

ShipmentES5.prototype.calculateShippingPrice = function () {
	this.validateBaseState()
	return this.weightKg * this.distanceKm * this.baseRatePerKm
}

ShipmentES5.prototype.description = function () {
	this.validateBaseState()
	return (
		this.sender +
		' -> ' +
		this.destination +
		', ' +
		this.weightKg +
		'kg, ' +
		this.distanceKm +
		'km'
	)
}

function ExpressShipmentES5(
	sender,
	destination,
	weightKg,
	distanceKm,
	baseRatePerKm,
	expressMultiplier,
) {
	ShipmentES5.call(
		this,
		sender,
		destination,
		weightKg,
		distanceKm,
		baseRatePerKm,
	)
	this.expressMultiplier =
		expressMultiplier === undefined ? 1.4 : expressMultiplier
}

ExpressShipmentES5.prototype = Object.create(ShipmentES5.prototype)
ExpressShipmentES5.prototype.constructor = ExpressShipmentES5

ExpressShipmentES5.prototype.calculateShippingPrice = function () {
	if (!Number.isFinite(this.expressMultiplier) || this.expressMultiplier < 1) {
		throw new Error('expressMultiplier must be at least 1')
	}
	return (
		ShipmentES5.prototype.calculateShippingPrice.call(this) *
			this.expressMultiplier +
		5
	)
}

ExpressShipmentES5.prototype.estimateTravelHours = function (speedKmH) {
	const hours = ShipmentES5.prototype.estimateTravelHours.call(this, speedKmH)
	return Math.max(1, hours * 0.7)
}

ExpressShipmentES5.prototype.priorityLabel = function () {
	return 'express'
}

function FragileShipmentES5(
	sender,
	destination,
	weightKg,
	distanceKm,
	baseRatePerKm,
	insuranceFee,
) {
	ShipmentES5.call(
		this,
		sender,
		destination,
		weightKg,
		distanceKm,
		baseRatePerKm,
	)
	this.insuranceFee = insuranceFee === undefined ? 10 : insuranceFee
}

FragileShipmentES5.prototype = Object.create(ShipmentES5.prototype)
FragileShipmentES5.prototype.constructor = FragileShipmentES5

FragileShipmentES5.prototype.calculateShippingPrice = function () {
	if (!Number.isFinite(this.insuranceFee) || this.insuranceFee < 0) {
		throw new Error('insuranceFee must not be negative')
	}
	return (
		ShipmentES5.prototype.calculateShippingPrice.call(this) +
		this.insuranceFee +
		this.weightKg * 2
	)
}

FragileShipmentES5.prototype.description = function () {
	return ShipmentES5.prototype.description.call(this) + ', fragile cargo'
}

FragileShipmentES5.prototype.requiresSpecialPackaging = function () {
	return true
}

function demo() {
	const shipments = [
		new ShipmentES5('Warehouse A', 'Center B', 12, 80, 0.5),
		new ExpressShipmentES5('Warehouse A', 'Center B', 12, 80, 0.5),
		new FragileShipmentES5('Warehouse A', 'Center B', 12, 80, 0.5),
	]

	console.log('Task 2 ES5')
	for (const shipment of shipments) {
		console.log(shipment.description())
		console.log('price:', shipment.calculateShippingPrice())
		console.log('time at 40 km/h:', shipment.estimateTravelHours(40))
	}
}

if (require.main === module) {
	demo()
}

module.exports = {
	ShipmentES5,
	ExpressShipmentES5,
	FragileShipmentES5,
}
