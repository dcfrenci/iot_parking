package org.iot.app.screen.home

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import org.iot.app.domain.model.Booking
import org.iot.app.domain.model.CurrentParking
import org.iot.app.domain.model.Plate
import org.iot.app.domain.usecase.CreateBookingUseCase
import org.iot.app.domain.usecase.GetBookingsUseCase
import org.iot.app.domain.usecase.GetCurrentParkingUseCase
import org.iot.app.domain.usecase.GetPlatesUseCase
import org.iot.app.domain.usecase.UpdateBookingPlateUseCase

data class SecurityAlerts(
    val notifyOnCarExit: Boolean = false,
    val notifyAfter12h: Boolean = false,
    val notifyAfter24h: Boolean = false,
)

data class HomeUiState(
    val currentParking: CurrentParking? = null,
    val bookings: List<Booking> = emptyList(),
    val plates: List<Plate> = emptyList(),
    val isLoading: Boolean = false,
    val error: String? = null,
    // Currently parked card expansion
    val isParkingDetailExpanded: Boolean = false,
    val securityAlerts: SecurityAlerts = SecurityAlerts(),
    // Booking expansion state: bookingId -> expanded
    val expandedBookingId: String? = null,
    // New booking dialog
    val isNewBookingDialogOpen: Boolean = false,
    // Edit plate dialog
    val editingBookingId: String? = null,
)

class HomeViewModel(
    private val getCurrentParking: GetCurrentParkingUseCase,
    private val getBookings: GetBookingsUseCase,
    private val getPlates: GetPlatesUseCase,
    private val createBooking: CreateBookingUseCase,
    private val updateBookingPlate: UpdateBookingPlateUseCase,
) : ViewModel() {

    private val _uiState = MutableStateFlow(HomeUiState())
    val uiState: StateFlow<HomeUiState> = _uiState.asStateFlow()

    init {
        loadData()
    }

    fun loadData() {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true, error = null) }
            getCurrentParking()
                .onSuccess { current ->
                    _uiState.update { it.copy(currentParking = current) }
                }
                .onFailure { e ->
                    _uiState.update { it.copy(error = e.message) }
                }
            getBookings()
                .onSuccess { bookings ->
                    _uiState.update { it.copy(bookings = bookings) }
                }
                .onFailure { e ->
                    _uiState.update { it.copy(error = e.message) }
                }
            getPlates()
                .onSuccess { plates ->
                    _uiState.update { it.copy(plates = plates, isLoading = false) }
                }
                .onFailure { e ->
                    _uiState.update { it.copy(error = e.message, isLoading = false) }
                }
        }
    }

    fun toggleParkingDetail() {
        _uiState.update { it.copy(isParkingDetailExpanded = !it.isParkingDetailExpanded) }
    }

    fun updateSecurityAlerts(alerts: SecurityAlerts) {
        _uiState.update { it.copy(securityAlerts = alerts) }
    }

    fun toggleBookingExpanded(bookingId: String) {
        _uiState.update { state ->
            state.copy(
                expandedBookingId = if (state.expandedBookingId == bookingId) null else bookingId
            )
        }
    }

    fun openNewBookingDialog() {
        _uiState.update { it.copy(isNewBookingDialogOpen = true) }
    }

    fun closeNewBookingDialog() {
        _uiState.update { it.copy(isNewBookingDialogOpen = false) }
    }

    fun submitNewBooking(
        name: String,
        parkingId: String,
        carPlate: String,
        days: Int,
        onSuccess: () -> Unit,
        onError: (String) -> Unit,
    ) {
        viewModelScope.launch {
            createBooking(name, parkingId, carPlate, days)
                .onSuccess { booking ->
                    _uiState.update { state ->
                        state.copy(
                            bookings = state.bookings + booking,
                            isNewBookingDialogOpen = false
                        )
                    }
                    onSuccess()
                }
                .onFailure { e -> onError(e.message ?: "Error creating booking") }
        }
    }

    fun openEditPlateDialog(bookingId: String) {
        _uiState.update { it.copy(editingBookingId = bookingId) }
    }

    fun closeEditPlateDialog() {
        _uiState.update { it.copy(editingBookingId = null) }
    }

    fun changeBookingPlate(bookingId: String, newPlate: String) {
        viewModelScope.launch {
            updateBookingPlate(bookingId, newPlate)
                .onSuccess { updated ->
                    _uiState.update { state ->
                        state.copy(
                            bookings = state.bookings.map {
                                if (it.id == bookingId) updated else it
                            },
                            editingBookingId = null,
                        )
                    }
                }
        }
    }
}
