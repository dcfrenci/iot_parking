package org.iot.app.screen

import androidx.compose.runtime.Composable
import androidx.compose.runtime.remember
import androidx.compose.ui.Modifier
import androidx.compose.ui.interop.UIKitView
import kotlinx.cinterop.ExperimentalForeignApi
import org.iot.app.domain.model.Parking
import platform.Foundation.NSURL
import platform.WebKit.WKScriptMessage
import platform.WebKit.WKScriptMessageHandlerProtocol
import platform.WebKit.WKUserContentController
import platform.WebKit.WKWebView
import platform.WebKit.WKWebViewConfiguration
import platform.darwin.NSObject

@OptIn(ExperimentalForeignApi::class)
@Composable
actual fun WebMapView(
    modifier: Modifier,
    centerLat: Double,
    centerLon: Double,
    userLat: Double?,
    userLon: Double?,
    zoom: Int,
    parkings: List<Parking>,
    onPinClicked: (Parking) -> Unit,
) {
    val html = remember(centerLat, centerLon, zoom, parkings) {
        buildLeafletHtml(centerLat, centerLon, zoom, parkings)
    }

    UIKitView(
        modifier = modifier,
        factory  = {
            val config  = WKWebViewConfiguration()
            val handler = object : NSObject(), WKScriptMessageHandlerProtocol {
                override fun userContentController(
                    userContentController: WKUserContentController,
                    didReceiveScriptMessage: WKScriptMessage,
                ) {
                    val parkingId = didReceiveScriptMessage.body as? String ?: return
                    // FIXED: using parkingId instead of id
                    val parking   = parkings.firstOrNull { it.parkingId.toString() == parkingId }
                    if (parking != null) onPinClicked(parking)
                }
            }
            config.userContentController.addScriptMessageHandler(handler, name = "iosBridge")
            WKWebView(
                frame         = platform.CoreGraphics.CGRectZero,
                configuration = config
            ).apply {
                loadHTMLString(html, baseURL = NSURL(string = "https://unpkg.com"))
            }
        },
        update = { webView ->
            webView.loadHTMLString(html, baseURL = NSURL(string = "https://unpkg.com"))
        }
    )
}

private fun buildLeafletHtml(
    centerLat: Double,
    centerLon: Double,
    zoom: Int,
    parkings: List<Parking>,
): String {
    val markers = parkings.joinToString("\n") { p ->
        // FIXED: using availableSlot, parkingName, and parkingId properties
        val color = if (p.availableSlot > 0) "#4CAF50" else "#F44336"
        val name = p.parkingName.replace("'", "\\'")

        // Add disabled slot info if the parking has disabled slots
        val disabledInfo = if (p.disabledSlot > 0) "<br/>♿ ${p.availableDisabledSlot}/${p.disabledSlot} disabled slots" else ""

        """
        L.circleMarker([${p.latitude}, ${p.longitude}], {
            radius: 10, color: '$color', fillColor: '$color', fillOpacity: 0.85
        })
        .bindPopup('<b>$name</b><br/>€${p.pricePerHour}/h · ${p.availableSlot}/${p.totalSlot} slots$disabledInfo')
        .on('click', function() {
            window.webkit.messageHandlers.iosBridge.postMessage('${p.parkingId}');
        })
        .addTo(map);
        """.trimIndent()
    }

    return """
    <!DOCTYPE html>
    <html>
    <head>
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
      <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
      <style>html,body,#map{margin:0;padding:0;width:100%;height:100%;}</style>
    </head>
    <body>
      <div id="map"></div>
      <script>
        var map = L.map('map').setView([$centerLat, $centerLon], $zoom);
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            maxZoom: 19,
            attribution: '© OpenStreetMap contributors'
        }).addTo(map);
        $markers
      </script>
    </body>
    </html>
    """.trimIndent()
}