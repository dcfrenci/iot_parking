package org.iot.app.data.remote

import io.ktor.client.HttpClient
import io.ktor.client.call.body
import io.ktor.client.request.delete
import io.ktor.client.request.get
import io.ktor.client.request.parameter
import io.ktor.client.request.patch
import io.ktor.client.request.post
import io.ktor.client.request.setBody
import org.iot.app.data.remote.dto.*

class ParkingApi(private val client: HttpClient) {

    suspend fun getNearbyParkings(lat: Double, lon: Double, range: Int = 5000): List<ParkingRangeResponse> =
        client.get("parkings/range") {
            parameter("lat", lat)
            parameter("lon", lon)
            parameter("range", range)
        }.body()

    suspend fun getActiveSessions(accountId: Int): List<SessionDto> =
        client.get("paying") {
            parameter("account_id", accountId)
        }.body()

    suspend fun getBookings(accountId: Int): List<BookingDto> =
        client.get("bookings"){
            parameter("account_id", accountId)
        }.body()

    suspend fun createBooking(request: BookingRequest): BookingDto =
        client.post("bookings") {
            setBody(request)
        }.body()

    suspend fun updateBooking(request: BookingRequest): BookingDto =
        client.patch("bookings") {
            setBody(request)
        }.body()

    suspend fun deleteBooking(accountId: Int, bookingId: Int) {
        client.delete("bookings") {
            parameter("account_id", accountId)
            parameter("booking_id", bookingId)
        }
    }
}