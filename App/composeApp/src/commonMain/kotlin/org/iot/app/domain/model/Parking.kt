package org.iot.app.domain.model

data class Parking(
    val parkingId: Int,
    val parkingName: String,
    val address: String,
    val latitude: Double,
    val longitude: Double,
    val availableSlot: Int,
    val totalSlot: Int,
    val pricePerHour: Double,
)

data class ParkingRange(
    val parking: Parking,
    val distance: Double
)

data class Booking(
    val bookingId: Int,
    val bookingName: String,
    val parking: Parking,
    val plate: Plate,
    val date: String,
    val days: Int,
    val slotCode: Int,
)

data class Session(
    val plate: Plate,
    val parking: Parking,
    val entryTime: String,
    val amount: Double,
    val isPaid: Boolean
)