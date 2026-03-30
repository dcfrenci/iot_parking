package org.iot.app.location

import androidx.compose.runtime.Composable
import androidx.compose.runtime.remember
import kotlinx.coroutines.suspendCancellableCoroutine
import platform.CoreLocation.*
import platform.Foundation.NSError
import platform.darwin.NSObject
import kotlin.coroutines.resume

@Composable
actual fun rememberLocationService(): LocationService {
    return remember { IOSLocationService() }
}

class IOSLocationService : LocationService {
    private val locationManager = CLLocationManager()
    private var delegate: LocationDelegate? = null

    override suspend fun getCurrentLocation(): LocationCoordinates? = suspendCancellableCoroutine { continuation ->
        locationManager.desiredAccuracy = kCLLocationAccuracyBest

        delegate = LocationDelegate(
            onLocation = { location ->
                locationManager.stopUpdatingLocation()
                if (continuation.isActive) continuation.resume(location)
                delegate = null
            },
            onError = {
                locationManager.stopUpdatingLocation()
                if (continuation.isActive) continuation.resume(null)
                delegate = null
            }
        )

        locationManager.delegate = delegate
        locationManager.requestLocation()

        continuation.invokeOnCancellation {
            locationManager.stopUpdatingLocation()
            delegate = null
        }
    }
}

class LocationDelegate(
    private val onLocation: (LocationCoordinates) -> Unit,
    private val onError: () -> Unit
) : NSObject(), CLLocationManagerDelegateProtocol {
    override fun locationManager(manager: CLLocationManager, didUpdateLocations: List<*>) {
        val location = didUpdateLocations.lastOrNull() as? CLLocation
        if (location != null) {
            onLocation(LocationCoordinates(location.coordinate.latitude, location.coordinate.longitude))
        } else {
            onError()
        }
    }
    override fun locationManager(manager: CLLocationManager, didFailWithError: NSError) {
        onError()
    }
}