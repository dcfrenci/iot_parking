package org.iot.app

import androidx.compose.material3.MaterialTheme
import androidx.compose.runtime.Composable
import androidx.compose.runtime.remember
import org.iot.app.data.remote.AuthApi
import org.iot.app.data.remote.HttpClientFactory
import org.iot.app.data.remote.ParkingApi
import org.iot.app.data.remote.SettingsApi
import org.iot.app.data.repository.AuthRepositoryImpl
import org.iot.app.data.repository.ParkingRepositoryImpl
import org.iot.app.data.repository.SettingsRepositoryImpl
import org.iot.app.domain.usecase.*

@Composable
fun App() {
    val client = remember { HttpClientFactory.create() }

    val authApi     = remember { AuthApi(client) }
    val parkingApi  = remember { ParkingApi(client) }
    val settingsApi = remember { SettingsApi(client) }

    val authRepository     = remember { AuthRepositoryImpl(authApi) }
    val parkingRepository  = remember { ParkingRepositoryImpl(parkingApi) }
    val settingsRepository = remember { SettingsRepositoryImpl(settingsApi) }

    // Auth use cases
    val login    = remember { LoginUseCase(authRepository) }
    val register = remember { RegisterUseCase(authRepository) }

    // Parking use cases
    val getNearbyParkings = remember { GetNearbyParkingsUseCase(parkingRepository) }
    val getActiveSessions = remember { GetActiveSessionsUseCase(parkingRepository) }
    val getBookings       = remember { GetBookingsUseCase(parkingRepository) }
    val createBooking     = remember { CreateBookingUseCase(parkingRepository) }
    val updateBooking     = remember { UpdateBookingUseCase(parkingRepository) }
    val deleteBooking     = remember { DeleteBookingUseCase(parkingRepository) }

    // Settings use cases
    val getUser             = remember { GetUserUseCase(settingsRepository) }
    val getPlates           = remember { GetPlatesUseCase(settingsRepository) }
    val addPlate            = remember { AddPlateUseCase(settingsRepository) }
    val deletePlate         = remember { DeletePlateUseCase(settingsRepository) }
    val getPaymentMethod    = remember { GetPaymentMethodUseCase(settingsRepository) }
    val updatePaymentMethod = remember { UpdatePaymentMethodUseCase(settingsRepository) }
    val getPreferences      = remember { GetPreferencesUseCase(settingsRepository) }
    val savePreferences     = remember { SavePreferencesUseCase(settingsRepository) }

    MaterialTheme {
        RootNavigation(
            login               = login,
            register            = register,
            getNearbyParkings   = getNearbyParkings,
            getActiveSessions   = getActiveSessions,
            getBookings         = getBookings,
            createBooking       = createBooking,
            updateBooking       = updateBooking,
            deleteBooking       = deleteBooking,
            getUser             = getUser,
            getPlates           = getPlates,
            addPlate            = addPlate,
            deletePlate         = deletePlate,
            getPaymentMethod    = getPaymentMethod,
            updatePaymentMethod = updatePaymentMethod,
            getPreferences      = getPreferences,
            savePreferences     = savePreferences,
        )
    }
}