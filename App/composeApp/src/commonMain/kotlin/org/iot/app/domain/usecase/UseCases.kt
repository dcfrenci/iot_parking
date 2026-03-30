package org.iot.app.domain.usecase

import org.iot.app.domain.model.*
import org.iot.app.domain.repository.ParkingRepository
import org.iot.app.domain.repository.SettingsRepository
import org.iot.app.data.remote.dto.LoginRequest
import org.iot.app.data.remote.dto.RegisterRequest
import org.iot.app.domain.repository.AuthRepository

// ── Auth ──────────────────────────────────────────────────────────────────────

class LoginUseCase(private val repository: AuthRepository) {
    suspend operator fun invoke(request: LoginRequest) = repository.login(request)
}

class RegisterUseCase(private val repository: AuthRepository) {
    suspend operator fun invoke(request: RegisterRequest) = repository.register(request)
}

// ── Parking ───────────────────────────────────────────────────────────────────

class GetNearbyParkingsUseCase(private val repository: ParkingRepository) {
    suspend operator fun invoke(lat: Double, lon: Double, range: Int = 5000): Result<List<ParkingRange>> =
        repository.getNearbyParkings(lat, lon, range)
}

class GetActiveSessionsUseCase(private val repository: ParkingRepository) {
    suspend operator fun invoke(accountId: Int): Result<List<Session>> =
        repository.getActiveSessions(accountId)
}

class GetBookingsUseCase(private val repository: ParkingRepository) {
    suspend operator fun invoke(accountId: Int): Result<List<Booking>> =
        repository.getBookings(accountId)
}

class CreateBookingUseCase(private val repository: ParkingRepository) {
    suspend operator fun invoke(accountId: Int, booking: Booking): Result<Booking> =
        repository.createBooking(accountId, booking)
}

class UpdateBookingUseCase(private val repository: ParkingRepository) {
    suspend operator fun invoke(accountId: Int, booking: Booking): Result<Booking> =
        repository.updateBooking(accountId, booking)
}

class DeleteBookingUseCase(private val repository: ParkingRepository) {
    suspend operator fun invoke(accountId: Int, bookingId: Int): Result<Unit> =
        repository.deleteBooking(accountId, bookingId)
}

// ── Settings ──────────────────────────────────────────────────────────────────

class GetUserUseCase(private val repository: SettingsRepository) {
    suspend operator fun invoke(accountId: Int): Result<User> =
        repository.getUser(accountId)
}

class GetPlatesUseCase(private val repository: SettingsRepository) {
    suspend operator fun invoke(accountId: Int): Result<List<Plate>> =
        repository.getPlates(accountId)
}

class AddPlateUseCase(private val repository: SettingsRepository) {
    suspend operator fun invoke(
        accountId: Int,
        name: String,
        plateText: String,
        imageUri: String?,
    ): Result<Plate> = repository.addPlate(accountId, name, plateText, imageUri)
}

class DeletePlateUseCase(private val repository: SettingsRepository) {
    suspend operator fun invoke(accountId: Int, plateId: Int): Result<Unit> =
        repository.deletePlate(accountId, plateId)
}

class GetPaymentMethodUseCase(private val repository: SettingsRepository) {
    suspend operator fun invoke(accountId: Int): Result<PaymentMethod> =
        repository.getPaymentMethod(accountId)
}

class UpdatePaymentMethodUseCase(private val repository: SettingsRepository) {
    suspend operator fun invoke(accountId: Int, payment: PaymentMethod): Result<PaymentMethod> =
        repository.updatePaymentMethod(accountId, payment)
}

class GetPreferencesUseCase(private val repository: SettingsRepository) {
    suspend operator fun invoke(accountId: Int): Result<ParkingPreferences> =
        repository.getPreferences(accountId)
}

class SavePreferencesUseCase(private val repository: SettingsRepository) {
    suspend operator fun invoke(accountId: Int, prefs: ParkingPreferences): Result<ParkingPreferences> =
        repository.updatePreferences(accountId, prefs)
}