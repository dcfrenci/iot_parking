package org.iot.app.domain.model

data class User(
    val accountId: Int,
    val name: String,
    val email: String,
)

data class Plate(
    val plateId: Int,
    val name: String,
    val plateText: String,
    val isActive: Boolean,
    val imageUri: String? = null,
)

data class PaymentMethod(
    val circuit: String,
    val cardNumber: String,
)

data class ParkingPreferences(
    val distanceValue: Double,
    val priceValue: Double,
)