package org.iot.app.domain.repository

import org.iot.app.domain.model.Booking
import org.iot.app.domain.model.CurrentParking
import org.iot.app.domain.model.Parking

interface ParkingRepository {
    suspend fun getNearbyParkings(lat: Double, lon: Double): Result<List<Parking>>
    suspend fun getCurrentParking(): Result<CurrentParking?>
    suspend fun getBookings(): Result<List<Booking>>
    suspend fun createBooking(
        name: String,
        parkingId: String,
        carPlate: String,
        days: Int,
    ): Result<Booking>
    suspend fun updateBookingPlate(bookingId: String, carPlate: String): Result<Booking>
}
