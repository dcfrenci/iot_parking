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
    val isMapExpanded: Boolean = false,
    val mapCenterLat: Double = 44.6471,
    val mapCenterLon: Double = 10.9252,
    val userLat: Double? = null,
    val userLon: Double? = null,
    val parkings: List<Parking> = emptyList(),
    val selectedParking: Parking? = null
)

class MapViewModel(
    private val getNearbyParkings: GetNearbyParkingsUseCase
) : ViewModel() {

    private val _uiState = MutableStateFlow(MapUiState())
    var hasLoadedOnce = false
        private set
    val uiState: StateFlow<MapUiState> = _uiState.asStateFlow()

    // REMOVED THE INIT BLOCK! The UI's LaunchedEffect now handles the first load.

    fun updateUserLocation(lat: Double, lon: Double, isRefresh: Boolean = false) {
        _uiState.update {
            it.copy(
                mapCenterLat = lat,
                mapCenterLon = lon,
                userLat = lat,
                userLon = lon
            )
        }
        // Pass the flag down to the fetch function
        fetchNearbyParkings(lat, lon, isRefresh)
    }

    fun updateMapCenter(lat: Double, lon: Double) {
        _uiState.update { it.copy(mapCenterLat = lat, mapCenterLon = lon) }
        fetchNearbyParkings(lat, lon)
    }

    fun fetchNearbyParkings(lat: Double, lon: Double, isRefresh: Boolean = false, range: Int = 5000) {
        if (hasLoadedOnce && !isRefresh) return

        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true, error = null) }
            try {
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

                // Lock the screen so it doesn't reload automatically next time you switch tabs
                hasLoadedOnce = true
            } catch (e: Exception) {
                _uiState.update { it.copy(isLoading = false, error = e.message) }
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