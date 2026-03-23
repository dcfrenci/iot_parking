package org.iot.app.screen.settings

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import org.iot.app.domain.model.ParkingPreferences
import org.iot.app.domain.model.PaymentMethod
import org.iot.app.domain.model.Plate
import org.iot.app.domain.model.User
import org.iot.app.domain.usecase.GetPaymentMethodUseCase
import org.iot.app.domain.usecase.GetPlatesUseCase
import org.iot.app.domain.usecase.GetPreferencesUseCase
import org.iot.app.domain.usecase.GetUserUseCase
import org.iot.app.domain.usecase.SavePreferencesUseCase
import org.iot.app.domain.usecase.SetPlateActiveUseCase

data class SettingsUiState(
    val user: User? = null,
    val plates: List<Plate> = emptyList(),
    val paymentMethod: PaymentMethod? = null,
    val preferences: ParkingPreferences = ParkingPreferences(2.5, 5.0),
    val isLoading: Boolean = false,
    val error: String? = null,
)

class SettingsViewModel(
    private val getUser: GetUserUseCase,
    private val getPlates: GetPlatesUseCase,
    private val setPlateActive: SetPlateActiveUseCase,
    private val getPaymentMethod: GetPaymentMethodUseCase,
    private val getPreferences: GetPreferencesUseCase,
    private val savePreferences: SavePreferencesUseCase,
) : ViewModel() {

    private val _uiState = MutableStateFlow(SettingsUiState())
    val uiState: StateFlow<SettingsUiState> = _uiState.asStateFlow()

    init {
        loadData()
    }

    fun loadData() {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true, error = null) }

            getUser().onSuccess { user ->
                _uiState.update { it.copy(user = user) }
            }
            getPlates().onSuccess { plates ->
                _uiState.update { it.copy(plates = plates) }
            }
            getPaymentMethod().onSuccess { payment ->
                _uiState.update { it.copy(paymentMethod = payment) }
            }
            getPreferences().onSuccess { prefs ->
                _uiState.update { it.copy(preferences = prefs) }
            }

            _uiState.update { it.copy(isLoading = false) }
        }
    }

    fun togglePlate(plateId: String, isActive: Boolean) {
        viewModelScope.launch {
            setPlateActive(plateId, isActive).onSuccess {
                _uiState.update { state ->
                    state.copy(
                        plates = state.plates.map { plate ->
                            if (plate.id == plateId) plate.copy(isActive = isActive) else plate
                        }
                    )
                }
            }
        }
    }

    fun updatePreferences(maxDistanceKm: Double, maxPricePerHour: Double) {
        val newPrefs = ParkingPreferences(maxDistanceKm, maxPricePerHour)
        viewModelScope.launch {
            savePreferences(newPrefs).onSuccess {
                _uiState.update { it.copy(preferences = newPrefs) }
            }
        }
    }
}
