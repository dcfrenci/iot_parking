package org.iot.app.data.repository

import kotlinx.coroutines.async
import kotlinx.coroutines.coroutineScope
import org.iot.app.data.remote.SettingsApi
import org.iot.app.data.remote.dto.*
import org.iot.app.domain.model.*
import org.iot.app.domain.repository.SettingsRepository

class SettingsRepositoryImpl(
    private val api: SettingsApi
) : SettingsRepository {

    override suspend fun getUser(accountId: Int): Result<User> =
        runCatching { api.getUser(accountId).toDomain() }

    override suspend fun getPlates(accountId: Int): Result<List<Plate>> =
        runCatching { api.getPlates(accountId).map { it.toDomain() } }

    override suspend fun addPlate(
        accountId: Int,
        name: String,
        plateText: String,
        imageUri: String?,
    ): Result<Plate> = runCatching {
        api.addPlate(CreatePlateDto(accountId, plateText, name, imageUri ?: "")).toDomain()
    }

    override suspend fun deletePlate(accountId: Int, plateId: Int): Result<Unit> =
        runCatching { api.deletePlate(accountId, plateId) }

    override suspend fun getPaymentMethod(accountId: Int): Result<PaymentMethod> =
        runCatching { api.getPaymentMethod(accountId).toDomain() }

    override suspend fun updatePaymentMethod(accountId: Int, payment: PaymentMethod): Result<PaymentMethod> =
        runCatching { api.updatePaymentMethod(UpdatePaymentDto(accountId, payment.toDto())).toDomain() }

    override suspend fun getPreferences(accountId: Int): Result<ParkingPreferences> = runCatching {
        // Run concurrent requests since distance and price are separate endpoints now
        coroutineScope {
            val distance = async { api.getDistancePreference(accountId) }
            val price = async { api.getPricePreference(accountId) }
            ParkingPreferences(distance.await().distanceValue, price.await().priceValue)
        }
    }

    override suspend fun updatePreferences(accountId: Int, prefs: ParkingPreferences): Result<ParkingPreferences> = runCatching {
        coroutineScope {
            val dist = async { api.updateDistancePreference(UpdateDistancePreferenceDto(accountId, prefs.distanceValue)) }
            val pr = async { api.updatePricePreference(UpdatePricePreferenceDto(accountId, prefs.priceValue)) }
            ParkingPreferences(dist.await().distanceValue, pr.await().priceValue)
        }
    }

    // ── Mappers ───────────────────────────────────────────────────────────────

    private fun UserDto.toDomain() = User(accountId = accountId, name = name, email = email)

    private fun PlateDto.toDomain() = Plate(
        plateId   = plateId,
        name      = plateName,
        plateText = plateText,
        isActive  = isActive,
        imageUri  = imageUri,
    )

    private fun PaymentMethodDto.toDomain() = PaymentMethod(
        circuit  = circuit,
        cardNumber = cardNumber,
    )

    private fun PaymentMethod.toDto() = PaymentMethodDto(
        circuit = circuit,
        cardNumber = cardNumber,
    )
}