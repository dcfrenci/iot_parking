package org.iot.app.domain.model

data class User(
    val id: String,
    val name: String,
    val email: String,
)

data class Plate(
    val id: String,
    val name: String,
    val plateText: String,
    val isActive: Boolean,
    val imageUri: String? = null,   // local URI or remote URL
)

data class PaymentMethod(
    val id: String,
    val lastFour: String,
    val brand: String,
)

data class ParkingPreferences(
    val maxDistanceKm: Double,
    val maxPricePerHour: Double,
)
