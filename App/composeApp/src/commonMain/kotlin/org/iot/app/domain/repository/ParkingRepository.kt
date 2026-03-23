package org.iot.app.domain.repository

import org.iot.app.domain.model.Booking
import org.iot.app.domain.model.CurrentParking
import org.iot.app.domain.model.Parking

interface ParkingRepository {
    suspend fun getNearbyParkings(lat: Double, lon: Double): Result<List<Parking>>
    suspend fun getCurrentParking(): Result<CurrentParking?>
    suspend fun getBookings(): Result<List<Booking>>
}
