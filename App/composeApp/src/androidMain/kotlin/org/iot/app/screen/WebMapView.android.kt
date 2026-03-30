package org.iot.app.screen

import android.annotation.SuppressLint
import android.view.ViewGroup
import android.webkit.JavascriptInterface
import android.webkit.WebChromeClient
import android.webkit.WebView
import android.webkit.WebViewClient
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.rememberUpdatedState
import androidx.compose.ui.Modifier
import androidx.compose.ui.viewinterop.AndroidView
import org.iot.app.domain.model.Parking

@SuppressLint("SetJavaScriptEnabled")
@Composable
actual fun WebMapView(
    modifier: Modifier,
    centerLat: Double,
    centerLon: Double,
    userLat: Double?, // Added
    userLon: Double?, // Added
    zoom: Int,
    parkings: List<Parking>,
    onPinClicked: (Parking) -> Unit,
) {
    val currentOnPinClicked by rememberUpdatedState(onPinClicked)
    val currentParkings by rememberUpdatedState(parkings)

    AndroidView(
        modifier = modifier,
        factory = { context ->
            WebView(context).apply {
                layoutParams = ViewGroup.LayoutParams(
                    ViewGroup.LayoutParams.MATCH_PARENT,
                    ViewGroup.LayoutParams.MATCH_PARENT
                )

                settings.javaScriptEnabled = true
                settings.domStorageEnabled = true
                settings.setSupportZoom(false)
                settings.builtInZoomControls = false
                settings.displayZoomControls = false

                webViewClient = WebViewClient()
                webChromeClient = WebChromeClient()

                addJavascriptInterface(
                    MapJsBridge { parkingId ->
                        currentParkings.firstOrNull { it.parkingId.toString() == parkingId }
                            ?.let { currentOnPinClicked(it) }
                    },
                    "AndroidBridge"
                )

                loadDataWithBaseURL(
                    "https://unpkg.com",
                    // Pass the new variables here
                    buildMapHtml(centerLat, centerLon, userLat, userLon, zoom, parkings),
                    "text/html",
                    "UTF-8",
                    null
                )
            }
        },
        update = { webView ->
            webView.loadDataWithBaseURL(
                "https://unpkg.com",
                // Pass the new variables here too
                buildMapHtml(centerLat, centerLon, userLat, userLon, zoom, currentParkings),
                "text/html",
                "UTF-8",
                null
            )
        }
    )
}

private class MapJsBridge(
    private val onParkingSelectedAction: (String) -> Unit
) {
    @JavascriptInterface
    fun onParkingSelected(parkingId: String) {
        onParkingSelectedAction(parkingId)
    }
}

private fun buildMapHtml(
    centerLat: Double,
    centerLon: Double,
    userLat: Double?,
    userLon: Double?,
    zoom: Int,
    parkings: List<Parking>,
): String {
    val markers = parkings.joinToString("\n") { p ->
        val color = if (p.availableSlot > 0) "#4CAF50" else "#F44336"
        val name = p.parkingName.replace("'", "\\'")
        """L.circleMarker([${p.latitude},${p.longitude}],{radius:12,color:'$color',fillColor:'$color',fillOpacity:0.85,weight:2})
          .bindPopup('<b>$name</b><br/>€${p.pricePerHour}/h · ${p.availableSlot}/${p.totalSlot} slots')
          .on('click',function(){AndroidBridge.onParkingSelected('${p.parkingId}');})
          .addTo(map);"""
    }

    // Evaluate the user pin logic in Kotlin using a custom CSS divIcon
    val userMarkerScript = if (userLat != null && userLon != null) {
        """
        // Define a custom animated blue dot
        var userIcon = L.divIcon({
            className: 'custom-user-marker',
            html: '<div class="pulse"></div><div class="dot"></div>',
            iconSize: [20, 20],
            iconAnchor: [10, 10]
        });
        
        // Add the user marker to the map
        L.marker([$userLat, $userLon], {icon: userIcon, zIndexOffset: 1000})
            .addTo(map)
            .bindPopup('<b>You are here</b>');
        """
    } else ""

    return """<!DOCTYPE html><html><head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no"/>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<style>
    *{margin:0;padding:0}html,body,#map{width:100%;height:100%}
    
    /* Current Location Blue Dot Styles */
    .custom-user-marker { position: relative; }
    .custom-user-marker .dot {
        width: 14px; height: 14px;
        background-color: #4285F4;
        border: 2px solid white;
        border-radius: 50%;
        position: absolute;
        top: 3px; left: 3px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.3);
        z-index: 2;
    }
    .custom-user-marker .pulse {
        width: 40px; height: 40px;
        background-color: rgba(66, 133, 244, 0.4);
        border-radius: 50%;
        position: absolute;
        top: -10px; left: -10px;
        animation: pulsate 2s ease-out infinite;
        z-index: 1;
        pointer-events: none;
    }
    @keyframes pulsate {
        0% { transform: scale(0.1); opacity: 1; }
        100% { transform: scale(1.0); opacity: 0; }
    }
</style>
</head><body><div id="map"></div><script>
var map=L.map('map',{zoomControl:true}).setView([$centerLat,$centerLon],$zoom);
L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png',{maxZoom:19,attribution:'© OpenStreetMap'}).addTo(map);

// Inject the Kotlin-evaluated scripts here
$userMarkerScript
$markers

</script></body></html>"""
}