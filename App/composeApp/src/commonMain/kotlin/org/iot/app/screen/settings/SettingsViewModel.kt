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
    private val addPaymentMethod: AddPaymentMethodUseCase,
    private val updatePaymentMethod: UpdatePaymentMethodUseCase,
    private val getPreferences: GetPreferencesUseCase,
    private val savePreferences: SavePreferencesUseCase
) : ViewModel() {

    private val accountId get() = SessionManager.currentAccountId.value

    private val _uiState = MutableStateFlow(SettingsUiState())
    private var hasLoadedOnce = false

    val uiState: StateFlow<SettingsUiState> = _uiState.asStateFlow()

    init {
        // Start observing the session ID the moment the ViewModel is created
        viewModelScope.launch {
            SessionManager.currentAccountId.collect { currentId ->
                // As soon as the accountId is valid (not -1), and we haven't loaded yet, fetch the data
                if (currentId != -1 && !hasLoadedOnce) {
                    loadSettings(accountId = currentId, isRefresh = false)
                }
            }
        }
    }

    fun loadSettings(accountId: Int = SessionManager.currentAccountId.value, isRefresh: Boolean = false) {
        if (accountId == -1) return
        if (hasLoadedOnce && !isRefresh) return

        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true, error = null) }
            try {
                val user = getUser(accountId).getOrNull()
                val plates = getPlates(accountId).getOrNull() ?: emptyList()
                val payment = getPaymentMethod(accountId).getOrNull()
                val prefs = getPreferences(accountId).getOrNull()

                _uiState.update {
                    it.copy(
                        isLoading = false,
                        user = user,
                        plates = plates,
                        paymentMethod = payment,
                        preferences = prefs
                    )
                }

                hasLoadedOnce = true
            } catch (e: Exception) {
                _uiState.update { it.copy(isLoading = false, error = e.message) }
            }
        }
    }

    fun togglePlate(plateId: Int, isActive: Boolean) {
        // Here you would implement your SetPlateActive logic if needed
        // For now, it just reloads settings to sync state
        loadSettings(isRefresh = true)
    }

    fun openAddPlateDialog() {
        _uiState.update { it.copy(isAddPlateDialogOpen = true) }
    }

    fun closeAddPlateDialog() {
        _uiState.update { it.copy(isAddPlateDialogOpen = false) }
    }

    fun addNewPlate(name: String, plateText: String, imageUri: String?) {
        viewModelScope.launch {
            addPlate(accountId, name, plateText, imageUri).onSuccess {
                closeAddPlateDialog()
                loadSettings(isRefresh = true)
            }
        }
    }

    fun removePlate(plateId: Int) {
        viewModelScope.launch {
            deletePlate(accountId, plateId).onSuccess { loadSettings(isRefresh = true) }
        }
    }

    fun updatePayment(paymentMethod: PaymentMethod) {
        viewModelScope.launch {
            if (_uiState.value.paymentMethod == null) {
                addPaymentMethod(accountId, paymentMethod).onSuccess { loadSettings(isRefresh = true) }
            } else {
                updatePaymentMethod(accountId, paymentMethod).onSuccess { loadSettings(isRefresh = true) }
            }
        }
    }

    fun updatePrefs(distance: Double, price: Double) {
        viewModelScope.launch {
            val newPrefs = ParkingPreferences(distance, price)
            savePreferences(accountId, newPrefs).onSuccess { loadSettings(isRefresh = true) }
        }
    }

    fun logout() {
        SessionManager.logout()
    }
}