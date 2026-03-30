package org.iot.app.location

import androidx.compose.runtime.Composable

data class LocationCoordinates(val lat: Double, val lon: Double)

interface LocationService {
    suspend fun getCurrentLocation(): LocationCoordinates?
}

@Composable
expect fun rememberLocationService(): LocationService