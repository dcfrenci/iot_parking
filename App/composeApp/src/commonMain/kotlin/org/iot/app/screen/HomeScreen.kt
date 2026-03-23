package org.iot.app.screen

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import app.composeapp.generated.resources.Res
import app.composeapp.generated.resources.navigation
import app.composeapp.generated.resources.notifications
import org.iot.app.domain.model.Booking
import org.iot.app.domain.model.CurrentParking
import org.iot.app.screen.home.HomeUiState
import org.iot.app.screen.home.HomeViewModel
import org.jetbrains.compose.resources.painterResource

@Composable
fun HomeScreen(viewModel: HomeViewModel) {
    val uiState by viewModel.uiState.collectAsState()

    when {
        uiState.isLoading -> {
            Box(modifier = Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                CircularProgressIndicator()
            }
        }
        uiState.error != null -> {
            Box(modifier = Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                Column(
                    horizontalAlignment = Alignment.CenterHorizontally,
                    verticalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    Text(
                        text  = "Error: ${uiState.error}",
                        color = MaterialTheme.colorScheme.error
                    )
                    Button(onClick = { viewModel.loadData() }) { Text("Try again") }
                }
            }
        }
        else -> HomeContent(uiState = uiState)
    }
}

@Composable
private fun HomeContent(uiState: HomeUiState) {
    LazyColumn(
        modifier            = Modifier
            .fillMaxSize()
            .padding(horizontal = 16.dp, vertical = 12.dp),
        verticalArrangement = Arrangement.spacedBy(20.dp)
    ) {
        item { SectionTitle("Currently parked") }
        item {
            if (uiState.currentParking != null) {
                CurrentlyParkedCard(parking = uiState.currentParking)
            } else {
                Text(
                    text  = "No parking available",
                    style = MaterialTheme.typography.bodyMedium,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }
        }

        item { SectionTitle("Booked car park") }
        items(uiState.bookings) { booking ->
            BookedParkCard(booked = booking)
        }
    }
}

@Composable
private fun SectionTitle(title: String) {
    Text(
        text  = title,
        style = MaterialTheme.typography.titleMedium,
        color = MaterialTheme.colorScheme.onBackground
    )
}

@Composable
private fun CurrentlyParkedCard(parking: CurrentParking) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors   = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.primaryContainer
        ),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
    ) {
        Column(
            modifier            = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            Row(
                modifier              = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment     = Alignment.CenterVertically
            ) {
                Text(
                    text  = parking.carPlate,
                    style = MaterialTheme.typography.bodyLarge,
                    color = MaterialTheme.colorScheme.onPrimaryContainer
                )
                Text(
                    text  = "€ ${parking.pricePerHour} / h",
                    style = MaterialTheme.typography.titleSmall,
                    color = MaterialTheme.colorScheme.primary
                )
            }

            Text(
                text  = parking.parkingName,
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onPrimaryContainer
            )

            HorizontalDivider(
                color = MaterialTheme.colorScheme.onPrimaryContainer.copy(alpha = 0.2f)
            )

            Row(
                modifier              = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                OutlinedButton(
                    onClick  = { /* TODO: set alarm */ },
                    modifier = Modifier.weight(1f)
                ) {
                    Icon(
                        painter            = painterResource(Res.drawable.notifications),
                        contentDescription = null,
                        modifier           = Modifier.size(16.dp)
                    )
                    Spacer(Modifier.width(6.dp))
                    Text("Alarm")
                }
                Button(
                    onClick  = { /* TODO: show directions */ },
                    modifier = Modifier.weight(1f)
                ) {
                    Icon(
                        painter            = painterResource(Res.drawable.navigation),
                        contentDescription = null,
                        modifier           = Modifier.size(16.dp)
                    )
                    Spacer(Modifier.width(6.dp))
                    Text("Direction")
                }
            }
        }
    }
}

@Composable
private fun BookedParkCard(booked: Booking) {
    Card(
        modifier  = Modifier.fillMaxWidth(),
        colors    = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface),
        elevation = CardDefaults.cardElevation(defaultElevation = 1.dp)
    ) {
        Column(
            modifier            = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(4.dp)
        ) {
            Text(text = booked.parkingName, style = MaterialTheme.typography.bodyLarge)
            Text(
                text  = booked.date,
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
            Text(
                text  = booked.carPlate,
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
            Text(
                text  = booked.slotCode,
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.primary
            )
        }
    }
}
