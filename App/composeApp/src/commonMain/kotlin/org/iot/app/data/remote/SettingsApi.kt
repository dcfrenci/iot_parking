package org.iot.app.data.remote

import io.ktor.client.HttpClient
import io.ktor.client.call.body
import io.ktor.client.request.get
import io.ktor.client.request.patch
import io.ktor.client.request.put
import io.ktor.client.request.setBody
import org.iot.app.data.remote.dto.ParkingPreferencesDto
import org.iot.app.data.remote.dto.PaymentMethodDto
import org.iot.app.data.remote.dto.PlateDto
import org.iot.app.data.remote.dto.UserDto

class SettingsApi(private val client: HttpClient) {

    suspend fun getUser(): UserDto =
        client.get("user").body()

    suspend fun getPlates(): List<PlateDto> =
        client.get("user/plates").body()

    suspend fun setPlateActive(plateId: String, isActive: Boolean) {
        client.patch("user/plates/$plateId") {
            setBody(mapOf("is_active" to isActive))
        }
    }

    suspend fun getPaymentMethod(): PaymentMethodDto =
        client.get("user/payment").body()

    suspend fun getPreferences(): ParkingPreferencesDto =
        client.get("user/preferences").body()

    suspend fun savePreferences(dto: ParkingPreferencesDto) {
        client.put("user/preferences") {
            setBody(dto)
        }
    }
}
