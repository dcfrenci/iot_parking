package org.iot.app.screen.home

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import org.iot.app.domain.SessionManager
import org.iot.app.domain.model.Booking
import org.iot.app.domain.model.Plate
import org.iot.app.domain.model.Session
import org.iot.app.domain.model.Parking
import org.iot.app.domain.usecase.*

data class SecurityAlerts(
    val notifyOnCarExit: Boolean = false,
    val notifyAfter12h: Boolean = false,
    val notifyAfter24h: Boolean = false
)

data class HomeUiState(
    val isLoading: Boolean = false,
    val error: String? = null,
    val activeSessions: List<Session> = emptyList(),
    val bookings: List<Booking> = emptyList(),
    val plates: List<Plate> = emptyList(),
    val securityAlerts: SecurityAlerts = SecurityAlerts(),
    val isParkingDetailExpanded: Boolean = false,
    val expandedBookingId: Int? = null,
    val isNewBookingDialogOpen: Boolean = false,
    val editingBookingId: Int? = null
)

class HomeViewModel(
    private val getActiveSessions: GetActiveSessionsUseCase,
    private val getBookings: GetBookingsUseCase,
    private val getPlates: GetPlatesUseCase,
    private val createBooking: CreateBookingUseCase,
    private val updateBooking: UpdateBookingUseCase,
    private val deleteBooking: DeleteBookingUseCase
) : ViewModel() {

    private val accountId get() = SessionManager.currentAccountId

    private val _uiState = MutableStateFlow(HomeUiState())
    val uiState: StateFlow<HomeUiState> = _uiState.asStateFlow()

    init {
        loadData()
    }

    fun loadData() {
        if (accountId == -1) return

        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true, error = null) }
            try {
                val sessions = getActiveSessions(accountId).getOrNull() ?: emptyList()
                val bookingsList = getBookings(accountId).getOrNull() ?: emptyList()
                val platesList = getPlates(accountId).getOrNull() ?: emptyList()

                _uiState.update {
                    it.copy(
                        isLoading = false,
                        activeSessions = sessions,
                        bookings = bookingsList,
                        plates = platesList
                    )
                }
            } catch (e: Exception) {
                _uiState.update { it.copy(isLoading = false, error = e.message) }
            }
        }
    }

    fun toggleParkingDetail() {
        _uiState.update { it.copy(isParkingDetailExpanded = !it.isParkingDetailExpanded) }
    }

    fun updateSecurityAlerts(alerts: SecurityAlerts) {
        _uiState.update { it.copy(securityAlerts = alerts) }
    }

    fun toggleBookingExpanded(bookingId: Int) {
        _uiState.update {
            it.copy(expandedBookingId = if (it.expandedBookingId == bookingId) null else bookingId)
        }
    }

    fun openEditPlateDialog(bookingId: Int) {
        _uiState.update { it.copy(editingBookingId = bookingId) }
    }

    fun closeEditPlateDialog() {
        _uiState.update { it.copy(editingBookingId = null) }
    }

    fun openNewBookingDialog() {
        _uiState.update { it.copy(isNewBookingDialogOpen = true) }
    }

    fun closeNewBookingDialog() {
        _uiState.update { it.copy(isNewBookingDialogOpen = false) }
    }

    fun submitNewBooking(
        name: String,
        parkingId: Int,
        carPlate: String,
        days: Int,
        onSuccess: () -> Unit,
        onError: (String) -> Unit
    ) {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true) }

            val selectedPlate = _uiState.value.plates.firstOrNull { it.plateText == carPlate }
            if (selectedPlate == null) {
                _uiState.update { it.copy(isLoading = false, error = "Plate not found") }
                return@launch
            }

            // Dummy Parking object to satisfy the Domain Model structure for creation
            val dummyParking = Parking(parkingId, "", "", 0.0, 0.0, 0, 0, 0.0)
            val newBooking = Booking(0, name, dummyParking, selectedPlate, "", days, 0)

            createBooking(accountId, newBooking).onSuccess {
                closeNewBookingDialog()
                loadData()
                onSuccess()
            }.onFailure { err ->
                _uiState.update { it.copy(isLoading = false, error = err.message) }
                onError(err.message ?: "Error creating booking")
            }
        }
    }

    fun changeBookingPlate(bookingId: Int, newPlateText: String) {
        viewModelScope.launch {
            val booking = _uiState.value.bookings.firstOrNull { it.bookingId == bookingId } ?: return@launch
            val plate = _uiState.value.plates.firstOrNull { it.plateText == newPlateText } ?: return@launch

            val updatedBooking = booking.copy(plate = plate)
            updateBooking(accountId, updatedBooking).onSuccess {
                closeEditPlateDialog()
                loadData()
            }
        }
    }
}