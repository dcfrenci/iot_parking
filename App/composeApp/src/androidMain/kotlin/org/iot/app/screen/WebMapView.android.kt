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
                // 1. Force the native view to fill the Compose space
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
                // 2. WebChromeClient is often required for HTML5 canvas/map rendering
                webChromeClient = WebChromeClient()

                // 3. Use the named class to prevent minification/ProGuard issues
                addJavascriptInterface(
                    MapJsBridge { parkingId ->
                        currentParkings.firstOrNull { it.id == parkingId }
                            ?.let { currentOnPinClicked(it) }
                    },
                    "AndroidBridge"
                )

                // 4. Provide a valid Base URL instead of null to prevent CORS/Origin blocking
                loadDataWithBaseURL(
                    "https://unpkg.com",
                    buildMapHtml(centerLat, centerLon, zoom, parkings),
                    "text/html",
                    "UTF-8",
                    null
                )
            }
        },
        update = { webView ->
            webView.loadDataWithBaseURL(
                "https://unpkg.com",
                buildMapHtml(centerLat, centerLon, zoom, currentParkings),
                "text/html",
                "UTF-8",
                null
            )
        }
    )
}

// Named class required by Android 4.2+ for @JavascriptInterface to be visible at runtime
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
    zoom: Int,
    parkings: List<Parking>,
): String {
    val markers = parkings.joinToString("\n") { p ->
        val color = if (p.availableSlots > 0) "#4CAF50" else "#F44336"
        val name = p.name.replace("'", "\\'")
        """L.circleMarker([${p.latitude},${p.longitude}],{radius:12,color:'$color',fillColor:'$color',fillOpacity:0.85,weight:2})
          .bindPopup('<b>$name</b><br/>€${p.pricePerHour}/h · ${p.availableSlots}/${p.totalSlots} slots')
          .on('click',function(){AndroidBridge.onParkingSelected('${p.id}');})
          .addTo(map);"""
    }
    return """<!DOCTYPE html><html><head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no"/>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<style>*{margin:0;padding:0}html,body,#map{width:100%;height:100%}</style>
</head><body><div id="map"></div><script>
var map=L.map('map',{zoomControl:true}).setView([$centerLat,$centerLon],$zoom);
L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png',{maxZoom:19,attribution:'© OpenStreetMap'}).addTo(map);
$markers
</script></body></html>"""
}