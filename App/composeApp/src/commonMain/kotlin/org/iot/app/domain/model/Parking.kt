package org.iot.app.domain.model

data class Parking(
    val id: String,
    val name: String,
    val address: String,
    val latitude: Double,
    val longitude: Double,
    val availableSlots: Int,
    val totalSlots: Int,
    val pricePerHour: Double,
    val distanceKm: Double,
)

data class Booking(
    val id: String,
    val parkingName: String,
    val date: String,
    val carPlate: String,
    val slotCode: String,
)

data class CurrentParking(
    val parkingName: String,
    val carPlate: String,
    val pricePerHour: Double,
    val startedAt: String,
)
