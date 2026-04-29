class Shipment {
	constructor(sender, destination, weightKg, distanceKm, baseRatePerKm) {
		this.sender = sender
		this.destination = destination
		this.weightKg = weightKg
		this.distanceKm = distanceKm
		this.baseRatePerKm = baseRatePerKm
	}

	validateBaseState() {
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

	estimateTravelHours(speedKmH) {
		this.validateBaseState()
		if (!Number.isFinite(speedKmH) || speedKmH <= 0) {
			throw new Error('speedKmH must be a positive number')
		}
		return this.distanceKm / speedKmH
	}

	calculateShippingPrice() {
		this.validateBaseState()
		return this.weightKg * this.distanceKm * this.baseRatePerKm
	}

	description() {
		this.validateBaseState()
		return `${this.sender} -> ${this.destination}, ${this.weightKg}kg, ${this.distanceKm}km`
	}
}

class ExpressShipment extends Shipment {
	constructor(
		sender,
		destination,
		weightKg,
		distanceKm,
		baseRatePerKm,
		expressMultiplier = 1.4,
	) {
		super(sender, destination, weightKg, distanceKm, baseRatePerKm)
		this.expressMultiplier = expressMultiplier
	}

	calculateShippingPrice() {
		if (
			!Number.isFinite(this.expressMultiplier) ||
			this.expressMultiplier < 1
		) {
			throw new Error('expressMultiplier must be at least 1')
		}
		return super.calculateShippingPrice() * this.expressMultiplier + 5
	}

	estimateTravelHours(speedKmH) {
		const hours = super.estimateTravelHours(speedKmH)
		return Math.max(1, hours * 0.7)
	}

	priorityLabel() {
		return 'express'
	}
}

class FragileShipment extends Shipment {
	constructor(
		sender,
		destination,
		weightKg,
		distanceKm,
		baseRatePerKm,
		insuranceFee = 10,
	) {
		super(sender, destination, weightKg, distanceKm, baseRatePerKm)
		this.insuranceFee = insuranceFee
	}

	calculateShippingPrice() {
		if (!Number.isFinite(this.insuranceFee) || this.insuranceFee < 0) {
			throw new Error('insuranceFee must not be negative')
		}
		return (
			super.calculateShippingPrice() + this.insuranceFee + this.weightKg * 2
		)
	}

	description() {
		return super.description() + ', fragile cargo'
	}

	requiresSpecialPackaging() {
		return true
	}
}

function demo() {
	const shipments = [
		new Shipment('Warehouse A', 'Center B', 12, 80, 0.5),
		new ExpressShipment('Warehouse A', 'Center B', 12, 80, 0.5),
		new FragileShipment('Warehouse A', 'Center B', 12, 80, 0.5),
	]

	console.log('Task 2 ES6')
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
	Shipment,
	ExpressShipment,
	FragileShipment,
}
