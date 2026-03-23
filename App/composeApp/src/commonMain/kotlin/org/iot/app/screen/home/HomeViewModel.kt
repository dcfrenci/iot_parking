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
import org.iot.app.domain.usecase.GetBookingsUseCase
import org.iot.app.domain.usecase.GetCurrentParkingUseCase

data class HomeUiState(
    val currentParking: CurrentParking? = null,
    val bookings: List<Booking> = emptyList(),
    val isLoading: Boolean = false,
    val error: String? = null,
)

class HomeViewModel(
    private val getCurrentParking: GetCurrentParkingUseCase,
    private val getBookings: GetBookingsUseCase,
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
                    _uiState.update { it.copy(bookings = bookings, isLoading = false) }
                }
                .onFailure { e ->
                    _uiState.update { it.copy(error = e.message, isLoading = false) }
                }
        }
    }
}
