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

class SettingsApi(private val client: HttpClient) {

    suspend fun getUser(accountId: Int): UserDto =
        client.get("user") {
            parameter("account_id", accountId)
        }.body()

    suspend fun getPlates(accountId: Int): List<PlateDto> =
        client.get("user/plates") {
            parameter("account_id", accountId)
        }.body()

    suspend fun addPlate(dto: CreatePlateDto): PlateDto =
        client.post("user/plates") {
            setBody(dto)
        }.body()

    suspend fun deletePlate(accountId: Int, plateId: Int) {
        client.delete("user/plates") {
            parameter("account_id", accountId)
            parameter("plate_id", plateId)
        }
    }

    suspend fun getPaymentMethod(accountId: Int): PaymentMethodDto =
        client.get("user/payment") {
            parameter("account_id", accountId)
        }.body()

    suspend fun updatePaymentMethod(dto: UpdatePaymentDto): PaymentMethodDto =
        client.patch("user/payment") {
            setBody(dto)
        }.body()

    suspend fun getDistancePreference(accountId: Int): DistancePreferenceDto =
        client.get("user/preferences/distance") {
            parameter("account_id", accountId)
        }.body()

    suspend fun updateDistancePreference(dto: UpdateDistancePreferenceDto): DistancePreferenceDto =
        client.patch("user/preferences/distance") {
            setBody(dto)
        }.body()

    suspend fun getPricePreference(accountId: Int): PricePreferenceDto =
        client.get("user/preferences/price") {
            parameter("account_id", accountId)
        }.body()

    suspend fun updatePricePreference(dto: UpdatePricePreferenceDto): PricePreferenceDto =
        client.patch("user/preferences/price") {
            setBody(dto)
        }.body()
}