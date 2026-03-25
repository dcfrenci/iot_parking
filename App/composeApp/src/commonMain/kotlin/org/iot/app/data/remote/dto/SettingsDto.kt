package org.iot.app.data.remote.dto

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

@Serializable
data class UserDto(
    val id: String,
    val name: String,
    val email: String,
)

@Serializable
data class PlateDto(
    val id: String,
    val name: String,
    @SerialName("plate_text") val plateText: String,
    @SerialName("is_active") val isActive: Boolean,
    @SerialName("image_uri") val imageUri: String? = null,
)

@Serializable
data class CreatePlateDto(
    val name: String,
    @SerialName("plate_text") val plateText: String,
    @SerialName("image_uri") val imageUri: String? = null,
)

@Serializable
data class PlateActiveUpdate(
    @SerialName("is_active") val isActive: Boolean,
)

@Serializable
data class PaymentMethodDto(
    val id: String,
    @SerialName("last_four") val lastFour: String,
    val brand: String,
)

@Serializable
data class ParkingPreferencesDto(
    @SerialName("max_distance_km") val maxDistanceKm: Double,
    @SerialName("max_price_per_hour") val maxPricePerHour: Double,
)
