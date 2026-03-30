package org.iot.app.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.unit.dp
import app.composeapp.generated.resources.*
import org.iot.app.domain.model.PaymentMethod
import org.iot.app.domain.model.Plate
import org.iot.app.domain.model.User
import org.iot.app.platform.rememberImagePicker
import org.iot.app.screen.settings.SettingsUiState
import org.iot.app.screen.settings.SettingsViewModel
import org.jetbrains.compose.resources.painterResource

@Composable
fun SettingsScreen(viewModel: SettingsViewModel) {
    val uiState by viewModel.uiState.collectAsState()

    when {
        uiState.isLoading -> {
            Box(Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                CircularProgressIndicator()
            }
        }
        uiState.error != null -> {
            Box(Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                Column(
                    horizontalAlignment = Alignment.CenterHorizontally,
                    verticalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    Text("Error: ${uiState.error}", color = MaterialTheme.colorScheme.error)
                    Button(onClick = { viewModel.loadSettings() }) { Text("Try again") }
                }
            }
        }
        else -> SettingsContent(
            uiState       = uiState,
            onTogglePlate = { id, active -> viewModel.togglePlate(id, active) },
            onSavePrefs   = { dist, price -> viewModel.updatePrefs(dist, price) },
            onOpenAddPlate = { viewModel.openAddPlateDialog() },
        )
    }

    if (uiState.isAddPlateDialogOpen) {
        AddPlateDialog(
            onConfirm = { name, text, uri -> viewModel.addNewPlate(name, text, uri) },
            onDismiss = { viewModel.closeAddPlateDialog() },
        )
    }
}

// ── Content ───────────────────────────────────────────────────────────────────

@Composable
private fun SettingsContent(
    uiState: SettingsUiState,
    onTogglePlate: (Int, Boolean) -> Unit,
    onSavePrefs: (Double, Double) -> Unit,
    onOpenAddPlate: () -> Unit,
) {
    LazyColumn(
        modifier            = Modifier
            .fillMaxSize()
            .padding(horizontal = 16.dp, vertical = 12.dp),
        verticalArrangement = Arrangement.spacedBy(24.dp)
    ) {
        item { SectionHeader("Account") }
        item { uiState.user?.let { AccountCard(user = it) } }

        item { SectionHeader("Registered plates") }
        item {
            Column(verticalArrangement = Arrangement.spacedBy(10.dp)) {
                uiState.plates.forEach { plate ->
                    RegisteredPlateCard(
                        plate    = plate,
                        onToggle = { isActive -> onTogglePlate(plate.plateId, isActive) }
                    )
                }
                OutlinedButton(
                    onClick  = onOpenAddPlate,
                    modifier = Modifier.fillMaxWidth(),
                ) {
                    Icon(
                        painter            = painterResource(Res.drawable.add),
                        contentDescription = null,
                        modifier           = Modifier.size(18.dp)
                    )
                    Spacer(Modifier.width(8.dp))
                    Text("Add plate")
                }
            }
        }

        item { SectionHeader("Payment method") }
        item { uiState.paymentMethod?.let { PaymentMethodCard(payment = it) } }

        item { SectionHeader("Parking preferences") }
        item {
            uiState.preferences?.let { prefs ->
                ParkingPreferencesCard(
                    initialDistance = prefs.distanceValue,
                    initialPrice    = prefs.priceValue,
                    onSave          = onSavePrefs,
                )
            }
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

// ── Account Card ──────────────────────────────────────────────────────────────

@Composable
private fun AccountCard(user: User) {
    Card(
        modifier  = Modifier.fillMaxWidth(),
        colors    = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface),
        elevation = CardDefaults.cardElevation(defaultElevation = 1.dp)
    ) {
        Row(
            modifier              = Modifier.fillMaxWidth().padding(16.dp),
            verticalAlignment     = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            Box(
                modifier         = Modifier.size(48.dp).clip(CircleShape)
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

// ── Registered Plate Card ─────────────────────────────────────────────────────

@Composable
private fun RegisteredPlateCard(
    plate: Plate,
    onToggle: (Boolean) -> Unit,
) {
    var checked by remember(plate.plateId) { mutableStateOf(plate.isActive) }

    Card(
        modifier  = Modifier.fillMaxWidth(),
        colors    = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface),
        elevation = CardDefaults.cardElevation(defaultElevation = 1.dp)
    ) {
        Column(
            modifier            = Modifier.fillMaxWidth().padding(16.dp),
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
                        modifier = Modifier.size(10.dp).clip(CircleShape).background(
                            if (checked) MaterialTheme.colorScheme.tertiary
                            else         MaterialTheme.colorScheme.error
                        )
                    )
                    Text(
                        text  = if (checked) "Active" else "Inactive",
                        style = MaterialTheme.typography.labelSmall,
                        color = if (checked) MaterialTheme.colorScheme.tertiary
                        else         MaterialTheme.colorScheme.error
                    )
                }
            }

            Row(
                verticalAlignment     = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                if (plate.imageUri != null) {
                    coil3.compose.AsyncImage(
                        model             = plate.imageUri,
                        contentDescription = "Plate image",
                        modifier          = Modifier
                            .size(width = 100.dp, height = 52.dp)
                            .clip(RoundedCornerShape(4.dp)),
                        contentScale      = ContentScale.Crop,
                        error             = painterResource(Res.drawable.image),
                    )
                } else {
                    Box(
                        modifier         = Modifier
                            .size(width = 100.dp, height = 52.dp)
                            .clip(RoundedCornerShape(4.dp))
                            .background(MaterialTheme.colorScheme.surfaceVariant),
                        contentAlignment = Alignment.Center
                    ) {
                        Icon(
                            painter            = painterResource(Res.drawable.image),
                            contentDescription = "No image",
                            tint               = MaterialTheme.colorScheme.onSurfaceVariant,
                            modifier           = Modifier.size(24.dp)
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
            }

            Row(
                modifier              = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment     = Alignment.CenterVertically
            ) {
                Text(
                    text  = "Active",
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

// ── Payment Method Card ───────────────────────────────────────────────────────

@Composable
private fun PaymentMethodCard(payment: PaymentMethod) {
    Card(
        modifier  = Modifier.fillMaxWidth(),
        colors    = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface),
        elevation = CardDefaults.cardElevation(defaultElevation = 1.dp)
    ) {
        Row(
            modifier              = Modifier.fillMaxWidth().padding(16.dp),
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
                val lastFour = payment.cardNumber.takeLast(4).padStart(4, '*')
                Text(
                    text  = "${payment.circuit} $lastFour",
                    style = MaterialTheme.typography.bodyMedium
                )
            }
            TextButton(onClick = { /* TODO: change payment */ }) { Text("Change") }
        }
    }
}

// ── Parking Preferences Card ──────────────────────────────────────────────────

@Composable
private fun ParkingPreferencesCard(
    initialDistance: Double,
    initialPrice: Double,
    onSave: (Double, Double) -> Unit,
) {
    var distance by remember(initialDistance) { mutableStateOf((initialDistance / 5f).toFloat().coerceIn(0f, 1f)) }
    var price    by remember(initialPrice)    { mutableStateOf((initialPrice / 10f).toFloat().coerceIn(0f, 1f)) }

    Card(
        modifier  = Modifier.fillMaxWidth(),
        colors    = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface),
        elevation = CardDefaults.cardElevation(defaultElevation = 1.dp)
    ) {
        Column(
            modifier            = Modifier.fillMaxWidth().padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            Column(verticalArrangement = Arrangement.spacedBy(4.dp)) {
                Row(
                    modifier              = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween
                ) {
                    Text("Distance", style = MaterialTheme.typography.bodyMedium)
                    Text(
                        text  = "${kotlin.math.round(distance * 5 * 10) / 10.0} km",
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.primary
                    )
                }
                Slider(value = distance, onValueChange = { distance = it }, modifier = Modifier.fillMaxWidth())
            }
            Column(verticalArrangement = Arrangement.spacedBy(4.dp)) {
                Row(
                    modifier              = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween
                ) {
                    Text("Max price", style = MaterialTheme.typography.bodyMedium)
                    Text(
                        text  = "€ ${kotlin.math.round(price * 10 * 10) / 10.0}/h",
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.primary
                    )
                }
                Slider(value = price, onValueChange = { price = it }, modifier = Modifier.fillMaxWidth())
            }
            Button(
                onClick  = {
                    onSave(
                        kotlin.math.round(distance * 5 * 10) / 10.0,
                        kotlin.math.round(price * 10 * 10) / 10.0,
                    )
                },
                modifier = Modifier.align(Alignment.End)
            ) { Text("Save") }
        }
    }
}

// ── Add Plate Dialog ──────────────────────────────────────────────────────────

@Composable
private fun AddPlateDialog(
    onConfirm: (name: String, plateText: String, imageUri: String?) -> Unit,
    onDismiss: () -> Unit,
) {
    var name      by remember { mutableStateOf("") }
    var plateText by remember { mutableStateOf("") }
    var imageUri  by remember { mutableStateOf<String?>(null) }

    val imagePicker = rememberImagePicker { uri -> imageUri = uri }

    AlertDialog(
        onDismissRequest = onDismiss,
        title   = { Text("Add new plate") },
        text    = {
            Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
                OutlinedTextField(
                    value         = name,
                    onValueChange = { name = it },
                    label         = { Text("Plate name (e.g. My Car)") },
                    modifier      = Modifier.fillMaxWidth(),
                    singleLine    = true,
                )
                OutlinedTextField(
                    value         = plateText,
                    onValueChange = { plateText = it.uppercase() },
                    label         = { Text("Plate number") },
                    modifier      = Modifier.fillMaxWidth(),
                    singleLine    = true,
                )

                if (imageUri != null) {
                    coil3.compose.AsyncImage(
                        model             = imageUri,
                        contentDescription = "Plate image preview",
                        modifier          = Modifier
                            .fillMaxWidth()
                            .height(80.dp)
                            .clip(RoundedCornerShape(8.dp)),
                        contentScale      = ContentScale.Crop,
                    )
                }

                Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    OutlinedButton(
                        onClick  = { imagePicker.launch() },
                        modifier = Modifier.weight(1f)
                    ) {
                        Icon(
                            painter            = painterResource(Res.drawable.photo_library),
                            contentDescription = null,
                            modifier           = Modifier.size(16.dp)
                        )
                        Spacer(Modifier.width(4.dp))
                        Text("Gallery")
                    }
                    OutlinedButton(
                        onClick  = { imagePicker.launch() },
                        modifier = Modifier.weight(1f)
                    ) {
                        Icon(
                            painter            = painterResource(Res.drawable.photo_camera),
                            contentDescription = null,
                            modifier           = Modifier.size(16.dp)
                        )
                        Spacer(Modifier.width(4.dp))
                        Text("Camera")
                    }
                }
            }
        },
        confirmButton = {
            Button(
                onClick  = { onConfirm(name, plateText, imageUri) },
                enabled  = name.isNotBlank() && plateText.isNotBlank()
            ) { Text("Add") }
        },
        dismissButton = {
            TextButton(onClick = onDismiss) { Text("Cancel") }
        }
    )
}