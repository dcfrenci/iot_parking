package org.iot.app.data.remote.dto

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

@Serializable
data class UserDto(
    @SerialName("account_id") val accountId: Int,
    val name: String,
    val email: String,
)

@Serializable
data class PlateDto(
    @SerialName("plate_id") val plateId: Int,
    @SerialName("plate_text") val plateText: String,
    @SerialName("plate_name") val plateName: String,
    @SerialName("is_active") val isActive: Boolean,
    @SerialName("image_uri") val imageUri: String? = null,
)

@Serializable
data class CreatePlateDto(
    @SerialName("account_id") val accountId: Int,
    @SerialName("plate_text") val plateText: String,
    @SerialName("plate_name") val plateName: String,
    @SerialName("image_uri") val imageUri: String = "",
)

@Serializable
data class PaymentMethodDto(
    val circuit: String,
    @SerialName("card_number") val cardNumber: String,
)

@Serializable
data class UpdatePaymentDto(
    @SerialName("account_id") val accountId: Int,
    val payment: PaymentMethodDto
)

@Serializable
data class DistancePreferenceDto(
    @SerialName("distance_value") val distanceValue: Double
)

@Serializable
data class UpdateDistancePreferenceDto(
    @SerialName("account_id") val accountId: Int,
    @SerialName("new_distance") val newDistance: Double
)

@Serializable
data class PricePreferenceDto(
    @SerialName("price_value") val priceValue: Double
)

@Serializable
data class UpdatePricePreferenceDto(
    @SerialName("account_id") val accountId: Int,
    @SerialName("new_price") val newPrice: Double
)