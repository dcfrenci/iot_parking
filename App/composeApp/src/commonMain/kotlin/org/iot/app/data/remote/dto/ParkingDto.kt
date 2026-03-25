package org.iot.app.data.remote.dto

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

@Serializable
data class ParkingDto(
    val id: String,
    val name: String,
    val address: String,
    val latitude: Double,
    val longitude: Double,
    @SerialName("available_slots") val availableSlots: Int,
    @SerialName("total_slots") val totalSlots: Int,
    @SerialName("price_per_hour") val pricePerHour: Double,
    @SerialName("distance_km") val distanceKm: Double,
)

@Serializable
data class BookingDto(
    val id: String,
    val name: String,
    @SerialName("parking_id") val parkingId: String,
    @SerialName("parking_name") val parkingName: String,
    val date: String,
    @SerialName("car_plate") val carPlate: String,
    @SerialName("slot_code") val slotCode: String,
    val days: Int,
    @SerialName("price_per_hour") val pricePerHour: Double,
)

@Serializable
data class CreateBookingDto(
    val name: String,
    @SerialName("parking_id") val parkingId: String,
    @SerialName("car_plate") val carPlate: String,
    val days: Int,
)

@Serializable
data class UpdateBookingPlateDto(
    @SerialName("car_plate") val carPlate: String,
)

@Serializable
data class CurrentParkingDto(
    @SerialName("parking_name") val parkingName: String,
    @SerialName("car_plate") val carPlate: String,
    @SerialName("price_per_hour") val pricePerHour: Double,
    @SerialName("started_at") val startedAt: String,
    val latitude: Double,
    val longitude: Double,
)
