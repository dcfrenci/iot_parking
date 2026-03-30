package org.iot.app.data.repository

import org.iot.app.data.remote.ParkingApi
import org.iot.app.data.remote.dto.*
import org.iot.app.domain.model.*
import org.iot.app.domain.repository.ParkingRepository

class ParkingRepositoryImpl(
    private val api: ParkingApi
) : ParkingRepository {

    override suspend fun getNearbyParkings(lat: Double, lon: Double, range: Int): Result<List<ParkingRange>> =
        runCatching { api.getNearbyParkings(lat, lon, range).map { ParkingRange(it.parking.toDomain(), it.distance) } }

    override suspend fun getActiveSessions(accountId: Int): Result<List<Session>> =
        runCatching { api.getActiveSessions(accountId).map { it.toDomain() } }

    override suspend fun getBookings(accountId: Int): Result<List<Booking>> =
        runCatching { api.getBookings(accountId).map { it.toDomain() } }

    override suspend fun createBooking(accountId: Int, booking: Booking): Result<Booking> = runCatching {
        api.createBooking(BookingRequest(accountId, booking.toDto())).toDomain()
    }

    override suspend fun updateBooking(accountId: Int, booking: Booking): Result<Booking> = runCatching {
        api.updateBooking(BookingRequest(accountId, booking.toDto())).toDomain()
    }

    override suspend fun deleteBooking(accountId: Int, bookingId: Int): Result<Unit> =
        runCatching { api.deleteBooking(accountId, bookingId) }

    // ── Mappers ───────────────────────────────────────────────────────────────

    private fun ParkingDto.toDomain() = Parking(
        parkingId = parkingId,
        parkingName = parkingName,
        address = address,
        latitude = lat,
        longitude = lon,
        availableSlot = availableSlot,
        totalSlot = totalSlot,
        pricePerHour = pricePerHour,
    )

    private fun Parking.toDto() = ParkingDto(
        parkingId = parkingId,
        parkingName = parkingName,
        address = address,
        lat = latitude,
        lon = longitude,
        availableSlot = availableSlot,
        totalSlot = totalSlot,
        pricePerHour = pricePerHour,
    )

    private fun PlateDto.toDomain() = Plate(plateId, plateName, plateText, isActive, imageUri)
    private fun Plate.toDto() = PlateDto(plateId, plateText, name, isActive, imageUri)

    private fun BookingDto.toDomain() = Booking(
        bookingId = bookingId,
        bookingName = bookingName,
        parking = parking.toDomain(),
        plate = plate.toDomain(),
        date = date,
        days = days,
        slotCode = slotCode,
    )

    private fun Booking.toDto() = BookingDto(
        bookingId = bookingId,
        bookingName = bookingName,
        parking = parking.toDto(),
        plate = plate.toDto(),
        date = date,
        days = days,
        slotCode = slotCode,
    )

    private fun SessionDto.toDomain() = Session(
        plate = plate.toDomain(),
        parking = parking.toDomain(),
        entryTime = entryTime,
        amount = amount,
        isPaid = isPaid,
    )
}