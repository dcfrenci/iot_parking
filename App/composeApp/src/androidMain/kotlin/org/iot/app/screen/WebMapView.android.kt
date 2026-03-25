package org.iot.app.screen

import android.webkit.JavascriptInterface
import android.webkit.WebView
import android.webkit.WebViewClient
import androidx.compose.runtime.Composable
import androidx.compose.runtime.remember
import androidx.compose.ui.Modifier
import androidx.compose.ui.viewinterop.AndroidView
import org.iot.app.domain.model.Parking

/**
 * Android actual for the `expect fun WebMapView` declared in MapScreen.kt (commonMain).
 * File location: androidMain/kotlin/org/iot/app/screen/WebMapView.android.kt
 *
 * If you get "Conflicting overloads", make sure there is NO other file in any
 * source set that also declares `actual fun WebMapView(...)`.
 */
@Composable
actual fun WebMapView(
    modifier: Modifier,
    centerLat: Double,
    centerLon: Double,
    zoom: Int,
    parkings: List<Parking>,
    onPinClicked: (Parking) -> Unit,
) {
    val stableParkings = remember(parkings) { parkings }

    AndroidView(
        modifier = modifier,
        factory  = { context ->
            WebView(context).apply {
                settings.javaScriptEnabled = true
                settings.domStorageEnabled = true
                settings.setSupportZoom(true)
                settings.builtInZoomControls = true
                settings.displayZoomControls = false
                addJavascriptInterface(
                    MapJsBridge(stableParkings, onPinClicked),
                    "AndroidBridge"
                )
                webViewClient = WebViewClient()
            }
        },
        update = { webView ->
            webView.loadDataWithBaseURL(
                "https://unpkg.com",
                buildMapHtml(centerLat, centerLon, zoom, stableParkings),
                "text/html",
                "UTF-8",
                null
            )
        }
    )
}

// Named class required by Android 4.2+ for @JavascriptInterface to be visible at runtime
private class MapJsBridge(
    private val parkings: List<Parking>,
    private val onPinClicked: (Parking) -> Unit,
) {
    @JavascriptInterface
    fun onParkingSelected(parkingId: String) {
        parkings.firstOrNull { it.id == parkingId }?.let { onPinClicked(it) }
    }
}

private fun buildMapHtml(
    centerLat: Double,
    centerLon: Double,
    zoom: Int,
    parkings: List<Parking>,
): String {
    val markers = parkings.joinToString("\n") { p ->
        val color = if (p.availableSlots > 0) "#4CAF50" else "#F44336"
        val name  = p.name.replace("'", "\\'")
        """L.circleMarker([${p.latitude},${p.longitude}],{radius:12,color:'$color',fillColor:'$color',fillOpacity:0.85,weight:2})
          .bindPopup('<b>$name</b><br/>€${p.pricePerHour}/h · ${p.availableSlots}/${p.totalSlots} slots')
          .on('click',function(){AndroidBridge.onParkingSelected('${p.id}');})
          .addTo(map);"""
    }
    return """<!DOCTYPE html><html><head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no"/>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"
  integrity="sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY=" crossorigin=""/>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"
  integrity="sha256-20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV/XN2GqBg=" crossorigin=""></script>
<style>*{margin:0;padding:0}html,body,#map{width:100%;height:100%}</style>
</head><body><div id="map"></div><script>
var map=L.map('map',{zoomControl:true}).setView([$centerLat,$centerLon],$zoom);
L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png',{maxZoom:19,attribution:'© OpenStreetMap'}).addTo(map);
$markers
</script></body></html>"""
}