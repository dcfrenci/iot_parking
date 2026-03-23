package org.iot.app.screen

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import app.composeapp.generated.resources.Res
import app.composeapp.generated.resources.location_on
import app.composeapp.generated.resources.search
import org.iot.app.domain.model.Parking
import org.iot.app.screen.map.MapUiState
import org.iot.app.screen.map.MapViewModel
import org.jetbrains.compose.resources.painterResource

@Composable
fun MapScreen(viewModel: MapViewModel) {
    val uiState by viewModel.uiState.collectAsState()
    var searchQuery by remember { mutableStateOf("") }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(horizontal = 16.dp, vertical = 12.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        OutlinedTextField(
            value         = searchQuery,
            onValueChange = { searchQuery = it },
            placeholder   = { Text("Search park / place") },
            leadingIcon   = {
                Icon(
                    painter            = painterResource(Res.drawable.search),
                    contentDescription = "Search"
                )
            },
            modifier  = Modifier.fillMaxWidth(),
            singleLine = true,
            shape      = MaterialTheme.shapes.medium
        )

        Card(
            modifier = Modifier
                .fillMaxWidth()
                .height(240.dp),
            colors = CardDefaults.cardColors(
                containerColor = MaterialTheme.colorScheme.surfaceVariant
            )
        ) {
            Box(
                modifier        = Modifier.fillMaxSize(),
                contentAlignment = Alignment.Center
            ) {
                Column(horizontalAlignment = Alignment.CenterHorizontally) {
                    Icon(
                        painter            = painterResource(Res.drawable.location_on),
                        contentDescription = null,
                        modifier           = Modifier.size(48.dp),
                        tint               = MaterialTheme.colorScheme.primary
                    )
                    Spacer(modifier = Modifier.height(8.dp))
                    Text(
                        text      = "Map of parking\nclose to your location",
                        style     = MaterialTheme.typography.bodyMedium,
                        color     = MaterialTheme.colorScheme.onSurfaceVariant,
                        textAlign = TextAlign.Center
                    )
                }
            }
        }

        Text(
            text  = "Parking list based on position and preferences",
            style = MaterialTheme.typography.titleSmall,
            color = MaterialTheme.colorScheme.onSurface
        )

        MapContent(uiState = uiState, onRetry = { viewModel.loadParkings() })
    }
}

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
        modifier = Modifier.fillMaxWidth(),
        colors   = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface),
        elevation = CardDefaults.cardElevation(defaultElevation = 1.dp)
    ) {
        Row(
            modifier            = Modifier
                .fillMaxWidth()
                .padding(horizontal = 16.dp, vertical = 12.dp),
            verticalAlignment   = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.SpaceBetween
        ) {
            Column {
                Text(text = parking.name,    style = MaterialTheme.typography.bodyMedium)
                Text(text = parking.address, style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant)
            }
            Column(horizontalAlignment = Alignment.End) {
                Text(
                    text  = "${parking.distanceKm} km",
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.primary
                )
                Text(
                    text  = "€ ${parking.pricePerHour}/h",
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }
        }
    }
}
