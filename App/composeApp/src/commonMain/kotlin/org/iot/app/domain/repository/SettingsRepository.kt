package org.iot.app.domain.repository

import org.iot.app.domain.model.ParkingPreferences
import org.iot.app.domain.model.PaymentMethod
import org.iot.app.domain.model.Plate
import org.iot.app.domain.model.User

interface SettingsRepository {
    suspend fun getUser(accountId: Int): Result<User>
    suspend fun getPlates(accountId: Int): Result<List<Plate>>
    suspend fun addPlate(accountId: Int, name: String, plateText: String, imageUri: String?): Result<Plate>
    suspend fun deletePlate(accountId: Int, plateId: Int): Result<Unit>
    suspend fun getPaymentMethod(accountId: Int): Result<PaymentMethod>
    suspend fun updatePaymentMethod(accountId: Int, payment: PaymentMethod): Result<PaymentMethod>
    suspend fun getPreferences(accountId: Int): Result<ParkingPreferences>
    suspend fun updatePreferences(accountId: Int, prefs: ParkingPreferences): Result<ParkingPreferences>
}