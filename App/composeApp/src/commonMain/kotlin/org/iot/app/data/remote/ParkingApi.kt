package org.iot.app.data.remote

import io.ktor.client.HttpClient
import io.ktor.client.call.body
import io.ktor.client.request.get
import io.ktor.client.request.parameter
import io.ktor.client.request.patch
import io.ktor.client.request.post
import io.ktor.client.request.setBody
import org.iot.app.data.remote.dto.BookingDto
import org.iot.app.data.remote.dto.CreateBookingDto
import org.iot.app.data.remote.dto.CurrentParkingDto
import org.iot.app.data.remote.dto.ParkingDto
import org.iot.app.data.remote.dto.UpdateBookingPlateDto

class ParkingApi(private val client: HttpClient) {

    suspend fun getNearbyParkings(lat: Double, lon: Double): List<ParkingDto> =
        client.get("parkings") {
            parameter("lat", lat)
            parameter("lon", lon)
        }.body()

    suspend fun getCurrentParking(): CurrentParkingDto? =
        client.get("parking/current").body()

    suspend fun getBookings(): List<BookingDto> =
        client.get("bookings").body()

    suspend fun createBooking(dto: CreateBookingDto): BookingDto =
        client.post("bookings") {
            setBody(dto)
        }.body()

    suspend fun updateBookingPlate(bookingId: String, dto: UpdateBookingPlateDto): BookingDto =
        client.patch("bookings/$bookingId") {
            setBody(dto)
        }.body()
}
