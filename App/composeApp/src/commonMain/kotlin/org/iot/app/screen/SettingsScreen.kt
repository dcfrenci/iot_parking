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
import app.composeapp.generated.resources.Res
import app.composeapp.generated.resources.credit_card
import app.composeapp.generated.resources.person
import org.iot.app.domain.model.PaymentMethod
import org.iot.app.domain.model.Plate
import org.iot.app.domain.model.User
import org.iot.app.screen.settings.SettingsUiState
import org.iot.app.screen.settings.SettingsViewModel
import org.jetbrains.compose.resources.painterResource

@Composable
fun SettingsScreen(viewModel: SettingsViewModel) {
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
        else -> SettingsContent(
            uiState        = uiState,
            onTogglePlate  = { id, active -> viewModel.togglePlate(id, active) },
            onSavePrefs    = { dist, price -> viewModel.updatePreferences(dist, price) }
        )
    }
}

@Composable
private fun SettingsContent(
    uiState       : SettingsUiState,
    onTogglePlate : (String, Boolean) -> Unit,
    onSavePrefs   : (Double, Double) -> Unit,
) {
    LazyColumn(
        modifier            = Modifier
            .fillMaxSize()
            .padding(horizontal = 16.dp, vertical = 12.dp),
        verticalArrangement = Arrangement.spacedBy(24.dp)
    ) {
        item { SectionHeader("Account") }
        item { uiState.user?.let { AccountCard(user = it) } }

        item { SectionHeader("Registered plate") }
        item {
            Column(verticalArrangement = Arrangement.spacedBy(10.dp)) {
                uiState.plates.forEach { plate ->
                    RegisteredPlateCard(
                        plate         = plate,
                        onToggle      = { isActive -> onTogglePlate(plate.id, isActive) }
                    )
                }
            }
        }

        item { SectionHeader("Payment method") }
        item { uiState.paymentMethod?.let { PaymentMethodCard(payment = it) } }

        item { SectionHeader("Parking preferences") }
        item {
            ParkingPreferencesCard(
                initialDistance = uiState.preferences.maxDistanceKm,
                initialPrice    = uiState.preferences.maxPricePerHour,
                onSave          = onSavePrefs
            )
        }
    }
}

@Composable
private fun SectionHeader(title: String) {
    Text(
        text  = title,
        style = MaterialTheme.typography.titleMedium,
        color = MaterialTheme.colorScheme.onBackground
    )
}

@Composable
private fun AccountCard(user: User) {
    Card(
        modifier  = Modifier.fillMaxWidth(),
        colors    = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface),
        elevation = CardDefaults.cardElevation(defaultElevation = 1.dp)
    ) {
        Row(
            modifier              = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            verticalAlignment     = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            Box(
                modifier         = Modifier
                    .size(48.dp)
                    .clip(CircleShape)
                    .background(MaterialTheme.colorScheme.primaryContainer),
                contentAlignment = Alignment.Center
            ) {
                Icon(
                    painter            = painterResource(Res.drawable.person),
                    contentDescription = null,
                    tint               = MaterialTheme.colorScheme.onPrimaryContainer,
                    modifier           = Modifier.size(24.dp)
                )
            }
            Column {
                Text(text = user.name,  style = MaterialTheme.typography.bodyLarge)
                Text(
                    text  = user.email,
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }
        }
    }
}

@Composable
private fun RegisteredPlateCard(
    plate    : Plate,
    onToggle : (Boolean) -> Unit,
) {
    var checked by remember(plate.id) { mutableStateOf(plate.isActive) }

    Card(
        modifier  = Modifier.fillMaxWidth(),
        colors    = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface),
        elevation = CardDefaults.cardElevation(defaultElevation = 1.dp)
    ) {
        Column(
            modifier            = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            Row(
                modifier              = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment     = Alignment.CenterVertically
            ) {
                Text(text = plate.name, style = MaterialTheme.typography.bodyLarge)
                Row(
                    verticalAlignment     = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.spacedBy(4.dp)
                ) {
                    Box(
                        modifier = Modifier
                            .size(10.dp)
                            .clip(CircleShape)
                            .background(
                                if (checked) MaterialTheme.colorScheme.tertiary
                                else MaterialTheme.colorScheme.error
                            )
                    )
                    Text(
                        text  = if (checked) "Active" else "Inactive",
                        style = MaterialTheme.typography.labelSmall,
                        color = if (checked) MaterialTheme.colorScheme.tertiary
                                else MaterialTheme.colorScheme.error
                    )
                }
            }

            Surface(
                shape    = MaterialTheme.shapes.small,
                color    = MaterialTheme.colorScheme.secondaryContainer,
                modifier = Modifier.wrapContentWidth()
            ) {
                Text(
                    text     = plate.plateText,
                    style    = MaterialTheme.typography.labelLarge,
                    color    = MaterialTheme.colorScheme.onSecondaryContainer,
                    modifier = Modifier.padding(horizontal = 12.dp, vertical = 4.dp)
                )
            }

            Row(
                modifier              = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment     = Alignment.CenterVertically
            ) {
                Text(
                    text  = "State",
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
                Switch(
                    checked         = checked,
                    onCheckedChange = {
                        checked = it
                        onToggle(it)
                    }
                )
            }
        }
    }
}

@Composable
private fun PaymentMethodCard(payment: PaymentMethod) {
    Card(
        modifier  = Modifier.fillMaxWidth(),
        colors    = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface),
        elevation = CardDefaults.cardElevation(defaultElevation = 1.dp)
    ) {
        Row(
            modifier              = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment     = Alignment.CenterVertically
        ) {
            Row(
                verticalAlignment     = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                Icon(
                    painter            = painterResource(Res.drawable.credit_card),
                    contentDescription = null,
                    tint               = MaterialTheme.colorScheme.primary,
                    modifier           = Modifier.size(24.dp)
                )
                Text(
                    text  = "${payment.brand} **** ${payment.lastFour}",
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
private fun ParkingPreferencesCard(
    initialDistance : Double,
    initialPrice    : Double,
    onSave          : (Double, Double) -> Unit,
) {
    var distance by remember(initialDistance) { mutableStateOf((initialDistance / 5f).toFloat()) }
    var price    by remember(initialPrice)    { mutableStateOf((initialPrice / 10f).toFloat()) }

    Card(
        modifier  = Modifier.fillMaxWidth(),
        colors    = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface),
        elevation = CardDefaults.cardElevation(defaultElevation = 1.dp)
    ) {
        Column(
            modifier            = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            Column(verticalArrangement = Arrangement.spacedBy(4.dp)) {
                Row(
                    modifier              = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween
                ) {
                    Text("Distance", style = MaterialTheme.typography.bodyMedium)
                    Text(
                        text  = "${(kotlin.math.round(distance * 5 * 10) / 10.0)} km",
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.primary
                    )
                }
                Slider(
                    value         = distance,
                    onValueChange = { distance = it },
                    modifier      = Modifier.fillMaxWidth()
                )
            }

            Column(verticalArrangement = Arrangement.spacedBy(4.dp)) {
                Row(
                    modifier              = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween
                ) {
                    Text("Price", style = MaterialTheme.typography.bodyMedium)
                    Text(
                        text  = "€ ${(kotlin.math.round(price * 10 * 10) / 10.0)} / h",
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.primary
                    )
                }
                Slider(
                    value         = price,
                    onValueChange = { price = it },
                    modifier      = Modifier.fillMaxWidth()
                )
            }

            Button(
                onClick  = {
                    onSave(
                        kotlin.math.round(distance * 5 * 10) / 10.0,
                        kotlin.math.round(price * 10 * 10) / 10.0
                    )
                },
                modifier = Modifier.align(Alignment.End)
            ) {
                Text("Save")
            }
        }
    }
}
