package org.iot.app.domain.repository

import org.iot.app.domain.model.Booking
import org.iot.app.domain.model.Session
import org.iot.app.domain.model.ParkingRange

interface ParkingRepository {
    suspend fun getNearbyParkings(lat: Double, lon: Double, range: Int): Result<List<ParkingRange>>
    suspend fun getActiveSessions(accountId: Int): Result<List<Session>>
    suspend fun getBookings(accountId: Int): Result<List<Booking>>
    suspend fun createBooking(accountId: Int, booking: Booking): Result<Booking>
    suspend fun updateBooking(accountId: Int, booking: Booking): Result<Booking>
    suspend fun deleteBooking(accountId: Int, bookingId: Int): Result<Unit>
}