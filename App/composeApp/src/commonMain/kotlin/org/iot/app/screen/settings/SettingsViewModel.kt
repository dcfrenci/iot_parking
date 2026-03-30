package org.iot.app.screen.settings

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import org.iot.app.domain.SessionManager
import org.iot.app.domain.model.ParkingPreferences
import org.iot.app.domain.model.PaymentMethod
import org.iot.app.domain.model.Plate
import org.iot.app.domain.model.User
import org.iot.app.domain.usecase.*

data class SettingsUiState(
    val isLoading: Boolean = false,
    val error: String? = null,
    val user: User? = null,
    val plates: List<Plate> = emptyList(),
    val paymentMethod: PaymentMethod? = null,
    val preferences: ParkingPreferences? = null,
    val isAddPlateDialogOpen: Boolean = false
)

class SettingsViewModel(
    private val getUser: GetUserUseCase,
    private val getPlates: GetPlatesUseCase,
    private val addPlate: AddPlateUseCase,
    private val deletePlate: DeletePlateUseCase,
    private val getPaymentMethod: GetPaymentMethodUseCase,
    private val updatePaymentMethod: UpdatePaymentMethodUseCase,
    private val getPreferences: GetPreferencesUseCase,
    private val savePreferences: SavePreferencesUseCase
) : ViewModel() {

    private val accountId get() = SessionManager.currentAccountId

    private val _uiState = MutableStateFlow(SettingsUiState())
    val uiState: StateFlow<SettingsUiState> = _uiState.asStateFlow()

    init {
        loadSettings()
    }

    fun loadSettings() {
        if (accountId.value == -1) return

        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true, error = null) }
            try {
                val user = getUser(accountId.value).getOrNull()
                val plates = getPlates(accountId.value).getOrNull() ?: emptyList()
                val payment = getPaymentMethod(accountId.value).getOrNull()
                val prefs = getPreferences(accountId.value).getOrNull()

                _uiState.update {
                    it.copy(
                        isLoading = false,
                        user = user,
                        plates = plates,
                        paymentMethod = payment,
                        preferences = prefs
                    )
                }
            } catch (e: Exception) {
                _uiState.update { it.copy(isLoading = false, error = e.message) }
            }
        }
    }

    fun togglePlate(plateId: Int, isActive: Boolean) {
        // Here you would implement your SetPlateActive logic if needed
        // For now, it just reloads settings to sync state
        loadSettings()
    }

    fun openAddPlateDialog() {
        _uiState.update { it.copy(isAddPlateDialogOpen = true) }
    }

    fun closeAddPlateDialog() {
        _uiState.update { it.copy(isAddPlateDialogOpen = false) }
    }

    fun addNewPlate(name: String, plateText: String, imageUri: String?) {
        viewModelScope.launch {
            addPlate(accountId.value, name, plateText, imageUri).onSuccess {
                closeAddPlateDialog()
                loadSettings()
            }
        }
    }

    fun removePlate(plateId: Int) {
        viewModelScope.launch {
            deletePlate(accountId.value, plateId).onSuccess { loadSettings() }
        }
    }

    fun updatePayment(paymentMethod: PaymentMethod) {
        viewModelScope.launch {
            updatePaymentMethod(accountId.value, paymentMethod).onSuccess { loadSettings() }
        }
    }

    fun updatePrefs(distance: Double, price: Double) {
        viewModelScope.launch {
            val newPrefs = ParkingPreferences(distance, price)
            savePreferences(accountId.value, newPrefs).onSuccess { loadSettings() }
        }
    }

    fun logout() {
        SessionManager.logout()
    }
}