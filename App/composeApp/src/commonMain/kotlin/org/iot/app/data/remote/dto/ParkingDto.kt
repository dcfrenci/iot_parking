package org.iot.app.data.remote.dto

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

@Serializable
data class ParkingDto(
    @SerialName("parking_id") val parkingId: Int,
    @SerialName("parking_name") val parkingName: String,
    @SerialName("total_slot") val totalSlot: Int,
    @SerialName("available_slot") val availableSlot: Int,
    @SerialName("disabled_slot") val disabledSlot: Int = 0,
    @SerialName("available_disabled_slot") val availableDisabledSlot: Int = 0,
    @SerialName("price_per_hour") val pricePerHour: Double,
    val lat: Double,
    val lon: Double,
    val address: String
)

@Serializable
data class ParkingRangeResponse(
    val parking: ParkingDto,
    val distance: Double
)

@Serializable
data class BookingDto(
    @SerialName("booking_id") val bookingId: Int,
    @SerialName("booking_name") val bookingName: String,
    val parking: ParkingDto,
    val plate: PlateDto,
    val date: String,
    val days: Int,
    @SerialName("slot_code") val slotCode: Int,
)

@Serializable
data class SessionDto(
    val plate: PlateDto,
    val parking: ParkingDto,
    @SerialName("entry_time") val entryTime: String,
    val amount: Double,
    @SerialName("is_paid") val isPaid: Boolean,
    @SerialName("used_disabled_slot") val usedDisabledSlot: Boolean = false
)

@Serializable
data class BookingRequest(
    @SerialName("account_id") val accountId: Int,
    val booking: BookingDto
)