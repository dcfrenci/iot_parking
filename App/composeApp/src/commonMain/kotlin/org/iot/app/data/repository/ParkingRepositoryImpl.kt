package org.iot.app.data.repository

import org.iot.app.data.remote.ParkingApi
import org.iot.app.data.remote.dto.BookingDto
import org.iot.app.data.remote.dto.CurrentParkingDto
import org.iot.app.data.remote.dto.ParkingDto
import org.iot.app.domain.model.Booking
import org.iot.app.domain.model.CurrentParking
import org.iot.app.domain.model.Parking
import org.iot.app.domain.repository.ParkingRepository

class ParkingRepositoryImpl(
    private val api: ParkingApi
) : ParkingRepository {

    override suspend fun getNearbyParkings(lat: Double, lon: Double): Result<List<Parking>> =
        runCatching {
            api.getNearbyParkings(lat, lon).map { it.toDomain() }
        }

    override suspend fun getCurrentParking(): Result<CurrentParking?> =
        runCatching {
            api.getCurrentParking()?.toDomain()
        }

    override suspend fun getBookings(): Result<List<Booking>> =
        runCatching {
            api.getBookings().map { it.toDomain() }
        }

    // ── Mappers ──────────────────────────────────────────────────────────────

    private fun ParkingDto.toDomain() = Parking(
        id            = id,
        name          = name,
        address       = address,
        latitude      = latitude,
        longitude     = longitude,
        availableSlots = availableSlots,
        totalSlots    = totalSlots,
        pricePerHour  = pricePerHour,
        distanceKm    = distanceKm,
    )

    private fun BookingDto.toDomain() = Booking(
        id          = id,
        parkingName = parkingName,
        date        = date,
        carPlate    = carPlate,
        slotCode    = slotCode,
    )

    private fun CurrentParkingDto.toDomain() = CurrentParking(
        parkingName  = parkingName,
        carPlate     = carPlate,
        pricePerHour = pricePerHour,
        startedAt    = startedAt,
    )
}
