package org.iot.app.data.repository

import org.iot.app.data.remote.SettingsApi
import org.iot.app.data.remote.dto.CreatePlateDto
import org.iot.app.data.remote.dto.ParkingPreferencesDto
import org.iot.app.data.remote.dto.PaymentMethodDto
import org.iot.app.data.remote.dto.PlateDto
import org.iot.app.data.remote.dto.UserDto
import org.iot.app.domain.model.ParkingPreferences
import org.iot.app.domain.model.PaymentMethod
import org.iot.app.domain.model.Plate
import org.iot.app.domain.model.User
import org.iot.app.domain.repository.SettingsRepository

class SettingsRepositoryImpl(
    private val api: SettingsApi
) : SettingsRepository {

    override suspend fun getUser(): Result<User> =
        runCatching { api.getUser().toDomain() }

    override suspend fun getPlates(): Result<List<Plate>> =
        runCatching { api.getPlates().map { it.toDomain() } }

    override suspend fun setPlateActive(plateId: String, isActive: Boolean): Result<Unit> =
        runCatching { api.setPlateActive(plateId, isActive) }

    override suspend fun addPlate(
        name: String,
        plateText: String,
        imageUri: String?,
    ): Result<Plate> = runCatching {
        api.addPlate(CreatePlateDto(name, plateText, imageUri)).toDomain()
    }

    override suspend fun getPaymentMethod(): Result<PaymentMethod> =
        runCatching { api.getPaymentMethod().toDomain() }

    override suspend fun getPreferences(): Result<ParkingPreferences> =
        runCatching { api.getPreferences().toDomain() }

    override suspend fun savePreferences(prefs: ParkingPreferences): Result<Unit> =
        runCatching { api.savePreferences(prefs.toDto()) }

    // ── Mappers ───────────────────────────────────────────────────────────────

    private fun UserDto.toDomain() = User(id = id, name = name, email = email)

    private fun PlateDto.toDomain() = Plate(
        id        = id,
        name      = name,
        plateText = plateText,
        isActive  = isActive,
        imageUri  = imageUri,
    )

    private fun PaymentMethodDto.toDomain() = PaymentMethod(
        id       = id,
        lastFour = lastFour,
        brand    = brand,
    )

    private fun ParkingPreferencesDto.toDomain() = ParkingPreferences(
        maxDistanceKm   = maxDistanceKm,
        maxPricePerHour = maxPricePerHour,
    )

    private fun ParkingPreferences.toDto() = ParkingPreferencesDto(
        maxDistanceKm   = maxDistanceKm,
        maxPricePerHour = maxPricePerHour,
    )
}
