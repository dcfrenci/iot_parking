package org.iot.app.domain.usecase

import org.iot.app.domain.model.Booking
import org.iot.app.domain.model.CurrentParking
import org.iot.app.domain.model.Parking
import org.iot.app.domain.model.ParkingPreferences
import org.iot.app.domain.model.PaymentMethod
import org.iot.app.domain.model.Plate
import org.iot.app.domain.model.User
import org.iot.app.domain.repository.ParkingRepository
import org.iot.app.domain.repository.SettingsRepository

// ── Parking ───────────────────────────────────────────────────────────────────

class GetNearbyParkingsUseCase(private val repository: ParkingRepository) {
    suspend operator fun invoke(lat: Double, lon: Double): Result<List<Parking>> =
        repository.getNearbyParkings(lat, lon)
}

class GetCurrentParkingUseCase(private val repository: ParkingRepository) {
    suspend operator fun invoke(): Result<CurrentParking?> =
        repository.getCurrentParking()
}

class GetBookingsUseCase(private val repository: ParkingRepository) {
    suspend operator fun invoke(): Result<List<Booking>> =
        repository.getBookings()
}

class CreateBookingUseCase(private val repository: ParkingRepository) {
    suspend operator fun invoke(
        name: String,
        parkingId: String,
        carPlate: String,
        days: Int,
    ): Result<Booking> = repository.createBooking(name, parkingId, carPlate, days)
}

class UpdateBookingPlateUseCase(private val repository: ParkingRepository) {
    suspend operator fun invoke(bookingId: String, carPlate: String): Result<Booking> =
        repository.updateBookingPlate(bookingId, carPlate)
}

// ── Settings ──────────────────────────────────────────────────────────────────

class GetUserUseCase(private val repository: SettingsRepository) {
    suspend operator fun invoke(): Result<User> =
        repository.getUser()
}

class GetPlatesUseCase(private val repository: SettingsRepository) {
    suspend operator fun invoke(): Result<List<Plate>> =
        repository.getPlates()
}

class SetPlateActiveUseCase(private val repository: SettingsRepository) {
    suspend operator fun invoke(plateId: String, isActive: Boolean): Result<Unit> =
        repository.setPlateActive(plateId, isActive)
}

class AddPlateUseCase(private val repository: SettingsRepository) {
    suspend operator fun invoke(
        name: String,
        plateText: String,
        imageUri: String?,
    ): Result<Plate> = repository.addPlate(name, plateText, imageUri)
}

class GetPaymentMethodUseCase(private val repository: SettingsRepository) {
    suspend operator fun invoke(): Result<PaymentMethod> =
        repository.getPaymentMethod()
}

class GetPreferencesUseCase(private val repository: SettingsRepository) {
    suspend operator fun invoke(): Result<ParkingPreferences> =
        repository.getPreferences()
}

class SavePreferencesUseCase(private val repository: SettingsRepository) {
    suspend operator fun invoke(prefs: ParkingPreferences): Result<Unit> =
        repository.savePreferences(prefs)
}
