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
    val isLoading: Boolean = false,
    val error: String? = null,
    val isMapExpanded: Boolean = true,
    val mapCenterLat: Double = 44.6471, // Modena coordinates
    val mapCenterLon: Double = 10.9252,
    val parkings: List<Parking> = emptyList(),
    val selectedParking: Parking? = null
)

class MapViewModel(
    private val getNearbyParkings: GetNearbyParkingsUseCase
) : ViewModel() {

    private val _uiState = MutableStateFlow(MapUiState())
    val uiState: StateFlow<MapUiState> = _uiState.asStateFlow()

    init {
        // Fetch initially based on the default coordinates
        fetchNearbyParkings(_uiState.value.mapCenterLat, _uiState.value.mapCenterLon)
    }

    fun fetchNearbyParkings(lat: Double, lon: Double, range: Int = 5000) {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true, error = null) }
            getNearbyParkings(lat, lon, range).onSuccess { parkingRanges ->
                _uiState.update {
                    it.copy(
                        isLoading = false,
                        parkings = parkingRanges.map { pr -> pr.parking }
                    )
                }
            }.onFailure { err ->
                _uiState.update { it.copy(isLoading = false, error = err.message) }
            }
        }
    }

    fun toggleMapExpanded() {
        _uiState.update { it.copy(isMapExpanded = !it.isMapExpanded) }
    }

    fun selectParking(parking: Parking?) {
        _uiState.update { it.copy(selectedParking = parking) }
    }
}