package org.iot.app.screens

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp

// Placeholder dati
private data class CurrentParking(
    val carName: String,
    val price: String,
)

private data class BookedPark(
    val name: String,
    val date: String,
    val carName: String,
    val parkSelected: String,
)

private val fakeCurrentParking = CurrentParking(
    carName = "Audi A3 - AB123CD",
    price = "€ 2.50 / h"
)

private val fakeBookedParks = listOf(
    BookedPark("Parking Centro",  "20 Mar 2025", "Audi A3 - AB123CD", "Slot A4"),
    BookedPark("Parking Stazione","18 Mar 2025", "BMW X1 - EF456GH", "Slot B2"),
)

@Composable
fun HomeScreen() {
    LazyColumn(
        modifier = Modifier
            .fillMaxSize()
            .padding(horizontal = 16.dp, vertical = 12.dp),
        verticalArrangement = Arrangement.spacedBy(20.dp)
    ) {
        // Currently parked section
        item {
            SectionTitle("Currently parked")
        }
        item {
            CurrentlyParkedCard(parking = fakeCurrentParking)
        }

        // Booked car parks section
        item {
            SectionTitle("Booked car park")
        }
        items(fakeBookedParks) { booked ->
            BookedParkCard(booked = booked)
        }
    }
}

@Composable
private fun SectionTitle(title: String) {
    Text(
        text = title,
        style = MaterialTheme.typography.titleMedium,
        color = MaterialTheme.colorScheme.onBackground
    )
}

@Composable
private fun CurrentlyParkedCard(parking: CurrentParking) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.primaryContainer
        ),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(
                    text = parking.carName,
                    style = MaterialTheme.typography.bodyLarge,
                    color = MaterialTheme.colorScheme.onPrimaryContainer
                )
                Text(
                    text = parking.price,
                    style = MaterialTheme.typography.titleSmall,
                    color = MaterialTheme.colorScheme.primary
                )
            }

            HorizontalDivider(color = MaterialTheme.colorScheme.onPrimaryContainer.copy(alpha = 0.2f))

            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                // Alarm button
                OutlinedButton(
                    onClick = { /* TODO: set alarm */ },
                    modifier = Modifier.weight(1f)
                ) {
                    Icon(
                        imageVector = androidx.compose.material.icons.Icons.Default.Notifications,
                        contentDescription = null,
                        modifier = Modifier.size(16.dp)
                    )
                    Spacer(Modifier.width(6.dp))
                    Text("Alarm")
                }
                // Direction button
                Button(
                    onClick = { /* TODO: show directions */ },
                    modifier = Modifier.weight(1f)
                ) {
                    Icon(
                        imageVector = androidx.compose.material.icons.Icons.Default.Navigation,
                        contentDescription = null,
                        modifier = Modifier.size(16.dp)
                    )
                    Spacer(Modifier.width(6.dp))
                    Text("Direction")
                }
            }
        }
    }
}

@Composable
private fun BookedParkCard(booked: BookedPark) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.surface
        ),
        elevation = CardDefaults.cardElevation(defaultElevation = 1.dp)
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(4.dp)
        ) {
            Text(
                text = booked.name,
                style = MaterialTheme.typography.bodyLarge
            )
            Text(
                text = booked.date,
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
            Text(
                text = booked.carName,
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
            Text(
                text = booked.parkSelected,
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.primary
            )
        }
    }
}
