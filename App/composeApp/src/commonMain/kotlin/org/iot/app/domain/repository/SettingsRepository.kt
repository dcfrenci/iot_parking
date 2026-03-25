package org.iot.app.domain.repository

import org.iot.app.domain.model.ParkingPreferences
import org.iot.app.domain.model.PaymentMethod
import org.iot.app.domain.model.Plate
import org.iot.app.domain.model.User

interface SettingsRepository {
    suspend fun getUser(): Result<User>
    suspend fun getPlates(): Result<List<Plate>>
    suspend fun setPlateActive(plateId: String, isActive: Boolean): Result<Unit>
    suspend fun addPlate(name: String, plateText: String, imageUri: String?): Result<Plate>
    suspend fun getPaymentMethod(): Result<PaymentMethod>
    suspend fun getPreferences(): Result<ParkingPreferences>
    suspend fun savePreferences(prefs: ParkingPreferences): Result<Unit>
}
