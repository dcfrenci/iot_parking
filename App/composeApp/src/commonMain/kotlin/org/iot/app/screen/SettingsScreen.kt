package org.iot.app.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.unit.dp

// Placeholder dati
private data class RegisteredPlate(
    val name: String,
    val plateText: String,
    val isActive: Boolean,
)

private val fakePlates = listOf(
    RegisteredPlate("Audi A3",  "AB123CD", isActive = true),
    RegisteredPlate("BMW X1",   "EF456GH", isActive = false),
)

@Composable
fun SettingsScreen() {
    LazyColumn(
        modifier = Modifier
            .fillMaxSize()
            .padding(horizontal = 16.dp, vertical = 12.dp),
        verticalArrangement = Arrangement.spacedBy(24.dp)
    ) {
        // Account section
        item { SectionHeader("Account") }
        item { AccountCard() }

        // Registered plates section
        item { SectionHeader("Registered plate") }
        item {
            Column(verticalArrangement = Arrangement.spacedBy(10.dp)) {
                fakePlates.forEach { plate ->
                    RegisteredPlateCard(plate = plate)
                }
            }
        }

        // Payment method section
        item { SectionHeader("Payment method") }
        item { PaymentMethodCard() }

        // Parking preferences section
        item { SectionHeader("Parking preferences") }
        item { ParkingPreferencesCard() }
    }
}

@Composable
private fun SectionHeader(title: String) {
    Text(
        text = title,
        style = MaterialTheme.typography.titleMedium,
        color = MaterialTheme.colorScheme.onBackground
    )
}

@Composable
private fun AccountCard() {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.surface
        ),
        elevation = CardDefaults.cardElevation(defaultElevation = 1.dp)
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            // Avatar placeholder
            Box(
                modifier = Modifier
                    .size(48.dp)
                    .clip(CircleShape)
                    .background(MaterialTheme.colorScheme.primaryContainer),
                contentAlignment = Alignment.Center
            ) {
                Icon(
                    imageVector = androidx.compose.material.icons.Icons.Default.Person,
                    contentDescription = null,
                    tint = MaterialTheme.colorScheme.onPrimaryContainer
                )
            }
            Column {
                Text(
                    text = "Mario Rossi",
                    style = MaterialTheme.typography.bodyLarge
                )
                Text(
                    text = "mario.rossi@email.com",
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }
        }
    }
}

@Composable
private fun RegisteredPlateCard(plate: RegisteredPlate) {
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
            verticalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(
                    text = plate.name,
                    style = MaterialTheme.typography.bodyLarge
                )
                // Active / Inactive indicator
                Row(
                    verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.spacedBy(4.dp)
                ) {
                    Box(
                        modifier = Modifier
                            .size(10.dp)
                            .clip(CircleShape)
                            .background(
                                if (plate.isActive) MaterialTheme.colorScheme.tertiary
                                else MaterialTheme.colorScheme.error
                            )
                    )
                    Text(
                        text = if (plate.isActive) "Active" else "Inactive",
                        style = MaterialTheme.typography.labelSmall,
                        color = if (plate.isActive) MaterialTheme.colorScheme.tertiary
                                else MaterialTheme.colorScheme.error
                    )
                }
            }

            // Plate text
            Surface(
                shape = MaterialTheme.shapes.small,
                color = MaterialTheme.colorScheme.secondaryContainer,
                modifier = Modifier.wrapContentWidth()
            ) {
                Text(
                    text = plate.plateText,
                    style = MaterialTheme.typography.labelLarge,
                    color = MaterialTheme.colorScheme.onSecondaryContainer,
                    modifier = Modifier.padding(horizontal = 12.dp, vertical = 4.dp)
                )
            }

            // State toggle row
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(
                    text = "State",
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
                var checked by remember { mutableStateOf(plate.isActive) }
                Switch(
                    checked = checked,
                    onCheckedChange = { checked = it }
                )
            }
        }
    }
}

@Composable
private fun PaymentMethodCard() {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.surface
        ),
        elevation = CardDefaults.cardElevation(defaultElevation = 1.dp)
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Row(
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                Icon(
                    imageVector = androidx.compose.material.icons.Icons.Default.CreditCard,
                    contentDescription = null,
                    tint = MaterialTheme.colorScheme.primary
                )
                Text(
                    text = "**** **** **** 4242",
                    style = MaterialTheme.typography.bodyMedium
                )
            }
            TextButton(onClick = { /* TODO: change payment */ }) {
                Text("Change")
            }
        }
    }
}

@Composable
private fun ParkingPreferencesCard() {
    var maxDistance by remember { mutableStateOf(0.5f) } // 0..1 → 0..5 km
    var maxPrice    by remember { mutableStateOf(0.4f) } // 0..1 → 0..10 €/h

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
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            // Distance preference
            Column(verticalArrangement = Arrangement.spacedBy(4.dp)) {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween
                ) {
                    Text("Distance", style = MaterialTheme.typography.bodyMedium)
                    Text(
                        text = "${"%.1f".format(maxDistance * 5)} km",
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.primary
                    )
                }
                Slider(
                    value = maxDistance,
                    onValueChange = { maxDistance = it },
                    modifier = Modifier.fillMaxWidth()
                )
            }

            // Price preference
            Column(verticalArrangement = Arrangement.spacedBy(4.dp)) {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween
                ) {
                    Text("Price", style = MaterialTheme.typography.bodyMedium)
                    Text(
                        text = "€ ${"%.1f".format(maxPrice * 10)} / h",
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.primary
                    )
                }
                Slider(
                    value = maxPrice,
                    onValueChange = { maxPrice = it },
                    modifier = Modifier.fillMaxWidth()
                )
            }
        }
    }
}
