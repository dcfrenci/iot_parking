package org.iot.app

import androidx.compose.material3.MaterialTheme
import androidx.compose.runtime.Composable
import androidx.compose.runtime.remember
import androidx.compose.ui.tooling.preview.Preview
import org.iot.app.data.remote.HttpClientFactory
import org.iot.app.data.remote.ParkingApi
import org.iot.app.data.remote.SettingsApi
import org.iot.app.data.repository.ParkingRepositoryImpl
import org.iot.app.data.repository.SettingsRepositoryImpl
import org.iot.app.domain.usecase.GetBookingsUseCase
import org.iot.app.domain.usecase.GetCurrentParkingUseCase
import org.iot.app.domain.usecase.GetNearbyParkingsUseCase
import org.iot.app.domain.usecase.GetPaymentMethodUseCase
import org.iot.app.domain.usecase.GetPlatesUseCase
import org.iot.app.domain.usecase.GetPreferencesUseCase
import org.iot.app.domain.usecase.GetUserUseCase
import org.iot.app.domain.usecase.SavePreferencesUseCase
import org.iot.app.domain.usecase.SetPlateActiveUseCase

@Composable
@Preview
fun App() {
    // ── Network ───────────────────────────────────────────────────────────────
    val client = remember { HttpClientFactory.create() }

    // ── API ───────────────────────────────────────────────────────────────────
    val parkingApi  = remember { ParkingApi(client) }
    val settingsApi = remember { SettingsApi(client) }

    // ── Repository ────────────────────────────────────────────────────────────
    val parkingRepository  = remember { ParkingRepositoryImpl(parkingApi) }
    val settingsRepository = remember { SettingsRepositoryImpl(settingsApi) }

    // ── Use cases ─────────────────────────────────────────────────────────────
    val getNearbyParkings  = remember { GetNearbyParkingsUseCase(parkingRepository) }
    val getCurrentParking  = remember { GetCurrentParkingUseCase(parkingRepository) }
    val getBookings        = remember { GetBookingsUseCase(parkingRepository) }

    val getUser            = remember { GetUserUseCase(settingsRepository) }
    val getPlates          = remember { GetPlatesUseCase(settingsRepository) }
    val setPlateActive     = remember { SetPlateActiveUseCase(settingsRepository) }
    val getPaymentMethod   = remember { GetPaymentMethodUseCase(settingsRepository) }
    val getPreferences     = remember { GetPreferencesUseCase(settingsRepository) }
    val savePreferences    = remember { SavePreferencesUseCase(settingsRepository) }

    MaterialTheme {
        RootNavigation(
            getNearbyParkings = getNearbyParkings,
            getCurrentParking = getCurrentParking,
            getBookings       = getBookings,
            getUser           = getUser,
            getPlates         = getPlates,
            setPlateActive    = setPlateActive,
            getPaymentMethod  = getPaymentMethod,
            getPreferences    = getPreferences,
            savePreferences   = savePreferences,
        )
    }
}
