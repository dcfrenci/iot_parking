package org.iot.app

import androidx.compose.material3.MaterialTheme
import androidx.compose.runtime.Composable
import androidx.compose.runtime.remember
import org.iot.app.data.remote.HttpClientFactory
import org.iot.app.data.remote.ParkingApi
import org.iot.app.data.remote.SettingsApi
import org.iot.app.data.repository.ParkingRepositoryImpl
import org.iot.app.data.repository.SettingsRepositoryImpl
import org.iot.app.domain.usecase.*

@Composable
fun App() {
    val client = remember { HttpClientFactory.create() }

    val parkingApi  = remember { ParkingApi(client) }
    val settingsApi = remember { SettingsApi(client) }

    val parkingRepository  = remember { ParkingRepositoryImpl(parkingApi) }
    val settingsRepository = remember { SettingsRepositoryImpl(settingsApi) }

    // Parking use cases
    val getNearbyParkings  = remember { GetNearbyParkingsUseCase(parkingRepository) }
    val getCurrentParking  = remember { GetCurrentParkingUseCase(parkingRepository) }
    val getBookings        = remember { GetBookingsUseCase(parkingRepository) }
    val createBooking      = remember { CreateBookingUseCase(parkingRepository) }
    val updateBookingPlate = remember { UpdateBookingPlateUseCase(parkingRepository) }

    // Settings use cases
    val getUser          = remember { GetUserUseCase(settingsRepository) }
    val getPlates        = remember { GetPlatesUseCase(settingsRepository) }
    val setPlateActive   = remember { SetPlateActiveUseCase(settingsRepository) }
    val addPlate         = remember { AddPlateUseCase(settingsRepository) }
    val getPaymentMethod = remember { GetPaymentMethodUseCase(settingsRepository) }
    val getPreferences   = remember { GetPreferencesUseCase(settingsRepository) }
    val savePreferences  = remember { SavePreferencesUseCase(settingsRepository) }

    MaterialTheme {
        RootNavigation(
            getNearbyParkings  = getNearbyParkings,
            getCurrentParking  = getCurrentParking,
            getBookings        = getBookings,
            createBooking      = createBooking,
            updateBookingPlate = updateBookingPlate,
            getUser            = getUser,
            getPlates          = getPlates,
            setPlateActive     = setPlateActive,
            addPlate           = addPlate,
            getPaymentMethod   = getPaymentMethod,
            getPreferences     = getPreferences,
            savePreferences    = savePreferences,
        )
    }
}
