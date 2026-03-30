package org.iot.app.screen

import androidx.compose.animation.core.animateDpAsState
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import app.composeapp.generated.resources.Res
import app.composeapp.generated.resources.close
import app.composeapp.generated.resources.search
import org.iot.app.domain.model.Parking
import org.iot.app.screen.map.MapUiState
import org.iot.app.screen.map.MapViewModel
import org.jetbrains.compose.resources.DrawableResource
import org.jetbrains.compose.resources.painterResource

// ── Root ──────────────────────────────────────────────────────────────────────

@Composable
fun MapScreen(viewModel: MapViewModel) {
    val uiState by viewModel.uiState.collectAsState()
    var searchQuery by remember { mutableStateOf("") }

    Column(
        modifier            = Modifier
            .fillMaxSize()
            .padding(horizontal = 16.dp, vertical = 12.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        OutlinedTextField(
            value         = searchQuery,
            onValueChange = { searchQuery = it },
            placeholder   = { Text("Search parking / place") },
            leadingIcon   = {
                Icon(
                    painter            = painterResource(Res.drawable.search),
                    contentDescription = "Search"
                )
            },
            modifier   = Modifier.fillMaxWidth(),
            singleLine = true,
            shape      = MaterialTheme.shapes.medium
        )

        OsmMapCard(
            uiState         = uiState,
            onToggleExpand  = { viewModel.toggleMapExpanded() },
            onSelectParking = { viewModel.selectParking(it) },
        )

        if (!uiState.isMapExpanded) {
            Text(
                text  = "Parking list based on position and preferences",
                style = MaterialTheme.typography.titleSmall,
                color = MaterialTheme.colorScheme.onSurface
            )
            MapContent(uiState = uiState, onRetry = { viewModel.fetchNearbyParkings(uiState.mapCenterLat, uiState.mapCenterLon) })
        }
    }
}

// ── OSM Map Card ──────────────────────────────────────────────────────────────

@Composable
private fun OsmMapCard(
    uiState: MapUiState,
    onToggleExpand: () -> Unit,
    onSelectParking: (Parking?) -> Unit,
) {
    val cardHeight by animateDpAsState(
        targetValue = if (uiState.isMapExpanded) 520.dp else 240.dp,
        label       = "map_height"
    )

    val stableCenterLat  = remember(uiState.mapCenterLat)  { uiState.mapCenterLat }
    val stableCenterLon  = remember(uiState.mapCenterLon)  { uiState.mapCenterLon }
    val stableZoom       = remember(uiState.isMapExpanded) { if (uiState.isMapExpanded) 15 else 14 }
    val stableParkings   = remember(uiState.parkings)      { uiState.parkings }

    Card(
        modifier  = Modifier
            .fillMaxWidth()
            .height(cardHeight)
            .clickable { onToggleExpand() },
        colors    = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceVariant),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
    ) {
        Box(modifier = Modifier.fillMaxSize()) {

            WebMapView(
                modifier     = Modifier.fillMaxSize(),
                centerLat    = stableCenterLat,
                centerLon    = stableCenterLon,
                zoom         = stableZoom,
                parkings     = stableParkings,
                onPinClicked = { parking -> onSelectParking(parking) },
            )

            // Expand/collapse hint badge
            Surface(
                modifier = Modifier
                    .align(Alignment.TopEnd)
                    .padding(8.dp),
                color = MaterialTheme.colorScheme.surface.copy(alpha = 0.85f),
                shape = MaterialTheme.shapes.small,
            ) {
                Text(
                    text     = if (uiState.isMapExpanded) "Tap to collapse" else "Tap to expand",
                    style    = MaterialTheme.typography.labelSmall,
                    modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp)
                )
            }

            // Parking info popup (shown when a pin is tapped)
            uiState.selectedParking?.let { parking ->
                ParkingPopup(
                    parking   = parking,
                    onDismiss = { onSelectParking(null) },
                    modifier  = Modifier
                        .align(Alignment.BottomCenter)
                        .padding(12.dp),
                )
            }
        }
    }
}

@Composable
private fun ParkingPopup(
    parking: Parking,
    onDismiss: () -> Unit,
    modifier: Modifier = Modifier,
) {
    Card(
        modifier  = modifier.fillMaxWidth(),
        colors    = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface),
        elevation = CardDefaults.cardElevation(defaultElevation = 8.dp)
    ) {
        Row(
            modifier              = Modifier
                .fillMaxWidth()
                .padding(12.dp),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment     = Alignment.Top
        ) {
            Column(
                modifier            = Modifier.weight(1f),
                verticalArrangement = Arrangement.spacedBy(4.dp)
            ) {
                Text(text = parking.parkingName,    style = MaterialTheme.typography.titleSmall)
                Text(
                    text  = parking.address,
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
                Row(horizontalArrangement = Arrangement.spacedBy(16.dp)) {
                    LabeledInfo(label = "Price",     value = "€ ${parking.pricePerHour}/h")
                    LabeledInfo(label = "Available", value = "${parking.availableSlot}/${parking.totalSlot} slots")
                }
            }
            IconButton(onClick = onDismiss) {
                Icon(
                    painter            = painterResource(Res.drawable.close),
                    contentDescription = "Close"
                )
            }
        }
    }
}

@Composable
private fun LabeledInfo(label: String, value: String) {
    Column {
        Text(
            text  = label,
            style = MaterialTheme.typography.labelSmall,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )
        Text(
            text  = value,
            style = MaterialTheme.typography.bodySmall,
            color = MaterialTheme.colorScheme.onSurface
        )
    }
}

// ── Parking list ──────────────────────────────────────────────────────────────

@Composable
private fun MapContent(uiState: MapUiState, onRetry: () -> Unit) {
    when {
        uiState.isLoading -> {
            Box(modifier = Modifier.fillMaxWidth(), contentAlignment = Alignment.Center) {
                CircularProgressIndicator()
            }
        }
        uiState.error != null -> {
            Column(
                modifier            = Modifier.fillMaxWidth(),
                horizontalAlignment = Alignment.CenterHorizontally,
                verticalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                Text(
                    text  = "Error: ${uiState.error}",
                    color = MaterialTheme.colorScheme.error,
                    style = MaterialTheme.typography.bodySmall
                )
                Button(onClick = onRetry) { Text("Try again") }
            }
        }
        else -> {
            LazyColumn(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                items(uiState.parkings) { parking ->
                    ParkingListItem(parking = parking)
                }
            }
        }
    }
}

@Composable
private fun ParkingListItem(parking: Parking) {
    Card(
        modifier  = Modifier.fillMaxWidth(),
        colors    = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface),
        elevation = CardDefaults.cardElevation(defaultElevation = 1.dp)
    ) {
        Row(
            modifier              = Modifier
                .fillMaxWidth()
                .padding(horizontal = 16.dp, vertical = 12.dp),
            verticalAlignment     = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.SpaceBetween
        ) {
            Column {
                Text(text = parking.parkingName,    style = MaterialTheme.typography.bodyMedium)
                Text(
                    text  = parking.address,
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }
            Column(horizontalAlignment = Alignment.End) {
                Text(
                    text  = "€ ${parking.pricePerHour}/h",
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
                Text(
                    text  = "${parking.availableSlot}/${parking.totalSlot} slots",
                    style = MaterialTheme.typography.labelSmall,
                    color = if (parking.availableSlot > 0)
                        MaterialTheme.colorScheme.tertiary
                    else
                        MaterialTheme.colorScheme.error
                )
            }
        }
    }
}

@Composable
expect fun WebMapView(
    modifier: Modifier,
    centerLat: Double,
    centerLon: Double,
    zoom: Int,
    parkings: List<Parking>,
    onPinClicked: (Parking) -> Unit,
)