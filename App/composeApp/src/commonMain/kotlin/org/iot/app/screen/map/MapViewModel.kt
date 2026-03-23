package org.iot.app.screen.map

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import org.iot.app.domain.model.Parking
import org.iot.app.domain.usecase.GetNearbyParkingsUseCase

data class MapUiState(
    val parkings: List<Parking> = emptyList(),
    val isLoading: Boolean = false,
    val error: String? = null,
)

class MapViewModel(
    private val getNearbyParkings: GetNearbyParkingsUseCase,
) : ViewModel() {

    private val _uiState = MutableStateFlow(MapUiState())
    val uiState: StateFlow<MapUiState> = _uiState.asStateFlow()

    init {
        loadParkings()
    }

    fun loadParkings(lat: Double = 44.4949, lon: Double = 11.3426) {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true, error = null) }
            getNearbyParkings(lat, lon)
                .onSuccess { parkings ->
                    _uiState.update { it.copy(parkings = parkings, isLoading = false) }
                }
                .onFailure { e ->
                    _uiState.update { it.copy(error = e.message, isLoading = false) }
                }
        }
    }
}
