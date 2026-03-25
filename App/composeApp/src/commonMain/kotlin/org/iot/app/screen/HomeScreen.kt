package org.iot.app.screen

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalUriHandler
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.unit.dp
import app.composeapp.generated.resources.*
import kotlin.time.Clock
import kotlin.time.Instant
import kotlinx.datetime.TimeZone
import kotlinx.datetime.number
import kotlinx.datetime.toLocalDateTime
import org.iot.app.domain.model.Booking
import org.iot.app.domain.model.CurrentParking
import org.iot.app.domain.model.Parking
import org.iot.app.domain.model.Plate
import org.iot.app.screen.home.HomeUiState
import org.iot.app.screen.home.HomeViewModel
import org.iot.app.screen.home.SecurityAlerts
import org.jetbrains.compose.resources.DrawableResource
import org.jetbrains.compose.resources.painterResource

// ── Root ──────────────────────────────────────────────────────────────────────

@Composable
fun HomeScreen(viewModel: HomeViewModel) {
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
                    Button(onClick = { viewModel.loadData() }) { Text("Try again") }
                }
            }
        }
        else -> HomeContent(
            uiState               = uiState,
            onToggleParkingDetail = { viewModel.toggleParkingDetail() },
            onSecurityChange      = { viewModel.updateSecurityAlerts(it) },
            onToggleBooking       = { viewModel.toggleBookingExpanded(it) },
            onOpenEditPlate       = { viewModel.openEditPlateDialog(it) },
            onOpenNewBooking      = { viewModel.openNewBookingDialog() },
        )
    }

    if (uiState.isNewBookingDialogOpen) {
        NewBookingDialog(
            availableParkings = emptyList(),
            availablePlates   = uiState.plates,
            onConfirm         = { name, parkingId, plate, days ->
                viewModel.submitNewBooking(
                    name      = name,
                    parkingId = parkingId,
                    carPlate  = plate,
                    days      = days,
                    onSuccess = {},
                    onError   = {},
                )
            },
            onDismiss = { viewModel.closeNewBookingDialog() },
        )
    }

    uiState.editingBookingId?.let { bookingId ->
        val booking = uiState.bookings.firstOrNull { it.id == bookingId }
        if (booking != null) {
            EditPlateDialog(
                currentPlate    = booking.carPlate,
                availablePlates = uiState.plates,
                onConfirm       = { newPlate -> viewModel.changeBookingPlate(bookingId, newPlate) },
                onDismiss       = { viewModel.closeEditPlateDialog() },
            )
        }
    }
}

// ── Content ───────────────────────────────────────────────────────────────────

@Composable
private fun HomeContent(
    uiState: HomeUiState,
    onToggleParkingDetail: () -> Unit,
    onSecurityChange: (SecurityAlerts) -> Unit,
    onToggleBooking: (String) -> Unit,
    onOpenEditPlate: (String) -> Unit,
    onOpenNewBooking: () -> Unit,
) {
    Box(modifier = Modifier.fillMaxSize()) {
        LazyColumn(
            modifier            = Modifier
                .fillMaxSize()
                .padding(horizontal = 16.dp, vertical = 12.dp),
            verticalArrangement = Arrangement.spacedBy(20.dp),
            contentPadding      = PaddingValues(bottom = 80.dp),
        ) {
            item { SectionTitle("Currently parked") }
            item {
                if (uiState.currentParking != null) {
                    CurrentlyParkedCard(
                        parking          = uiState.currentParking,
                        isExpanded       = uiState.isParkingDetailExpanded,
                        securityAlerts   = uiState.securityAlerts,
                        onToggleExpand   = onToggleParkingDetail,
                        onSecurityChange = onSecurityChange,
                    )
                } else {
                    Text(
                        text  = "No active parking session",
                        style = MaterialTheme.typography.bodyMedium,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
            }

            item { SectionTitle("Booked car park") }

            if (uiState.bookings.isEmpty()) {
                item {
                    Text(
                        text  = "No bookings yet",
                        style = MaterialTheme.typography.bodyMedium,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
            } else {
                items(uiState.bookings) { booking ->
                    BookedParkCard(
                        booking     = booking,
                        isExpanded  = uiState.expandedBookingId == booking.id,
                        onToggle    = { onToggleBooking(booking.id) },
                        onEditPlate = { onOpenEditPlate(booking.id) },
                    )
                }
            }
        }

        FloatingActionButton(
            onClick  = onOpenNewBooking,
            modifier = Modifier.align(Alignment.BottomEnd).padding(16.dp),
        ) {
            Icon(painterResource(Res.drawable.add), contentDescription = "New booking")
        }
    }
}

@Composable
private fun SectionTitle(title: String) {
    Text(text = title, style = MaterialTheme.typography.titleMedium)
}

// ── Currently Parked Card ─────────────────────────────────────────────────────

@Composable
private fun CurrentlyParkedCard(
    parking: CurrentParking,
    isExpanded: Boolean,
    securityAlerts: SecurityAlerts,
    onToggleExpand: () -> Unit,
    onSecurityChange: (SecurityAlerts) -> Unit,
) {
    val uriHandler   = LocalUriHandler.current
    val elapsedHours = remember(parking.startedAt) { computeElapsedHours(parking.startedAt) }
    val currentCost  = kotlin.math.round(elapsedHours * parking.pricePerHour * 100) / 100.0

    Card(
        modifier  = Modifier.fillMaxWidth(),
        colors    = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.primaryContainer),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
    ) {
        Column(
            modifier            = Modifier.fillMaxWidth().padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            // Header — always visible
            Row(
                modifier              = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment     = Alignment.CenterVertically
            ) {
                Column {
                    Text(parking.carPlate,   style = MaterialTheme.typography.bodyLarge,
                        color = MaterialTheme.colorScheme.onPrimaryContainer)
                    Text(parking.parkingName, style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onPrimaryContainer)
                }
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Text("€ ${parking.pricePerHour}/h", style = MaterialTheme.typography.titleSmall,
                        color = MaterialTheme.colorScheme.primary)
                    Spacer(Modifier.width(8.dp))
                    IconButton(onClick = onToggleExpand) {
                        Icon(
                            painter = painterResource(
                                if (isExpanded) Res.drawable.expand_less else Res.drawable.expand_more
                            ),
                            contentDescription = if (isExpanded) "Collapse" else "Expand",
                            tint = MaterialTheme.colorScheme.onPrimaryContainer
                        )
                    }
                }
            }

            // Expanded body — plain `if`, no AnimatedVisibility
            if (isExpanded) {
                HorizontalDivider(color = MaterialTheme.colorScheme.onPrimaryContainer.copy(alpha = 0.2f))

                Row(horizontalArrangement = Arrangement.spacedBy(24.dp)) {
                    InfoChip(Res.drawable.timer, "Entered",      formatStartedAt(parking.startedAt))
                    InfoChip(Res.drawable.euro,  "Current cost", "€ $currentCost")
                }

                HorizontalDivider(color = MaterialTheme.colorScheme.onPrimaryContainer.copy(alpha = 0.2f))

                Text("Security alerts", style = MaterialTheme.typography.labelMedium,
                    color = MaterialTheme.colorScheme.onPrimaryContainer)
                SecurityToggle("Notify if car leaves parking", securityAlerts.notifyOnCarExit)
                { onSecurityChange(securityAlerts.copy(notifyOnCarExit = it)) }
                SecurityToggle("Notify after 12 hours", securityAlerts.notifyAfter12h)
                { onSecurityChange(securityAlerts.copy(notifyAfter12h = it)) }
                SecurityToggle("Notify after 24 hours", securityAlerts.notifyAfter24h)
                { onSecurityChange(securityAlerts.copy(notifyAfter24h = it)) }

                HorizontalDivider(color = MaterialTheme.colorScheme.onPrimaryContainer.copy(alpha = 0.2f))

                Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(12.dp)) {
                    OutlinedButton(onClick = {}, modifier = Modifier.weight(1f)) {
                        Icon(painterResource(Res.drawable.security), null, Modifier.size(16.dp))
                        Spacer(Modifier.width(6.dp))
                        Text("Alerts")
                    }
                    Button(
                        onClick  = {
                            uriHandler.openUri(
                                "https://www.google.com/maps/dir/?api=1" +
                                        "&destination=${parking.latitude},${parking.longitude}" +
                                        "&travelmode=driving"
                            )
                        },
                        modifier = Modifier.weight(1f)
                    ) {
                        Icon(painterResource(Res.drawable.directions_car), null, Modifier.size(16.dp))
                        Spacer(Modifier.width(6.dp))
                        Text("Direction")
                    }
                }
            }
        }
    }
}

@Composable
private fun InfoChip(icon: DrawableResource, label: String, value: String) {
    Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(6.dp)) {
        Icon(painterResource(icon), null, Modifier.size(18.dp),
            tint = MaterialTheme.colorScheme.onPrimaryContainer)
        Column {
            Text(label, style = MaterialTheme.typography.labelSmall,
                color = MaterialTheme.colorScheme.onPrimaryContainer)
            Text(value, style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onPrimaryContainer)
        }
    }
}

@Composable
private fun SecurityToggle(label: String, checked: Boolean, onCheck: (Boolean) -> Unit) {
    Row(
        modifier              = Modifier.fillMaxWidth(),
        horizontalArrangement = Arrangement.SpaceBetween,
        verticalAlignment     = Alignment.CenterVertically
    ) {
        Text(label, style = MaterialTheme.typography.bodySmall,
            color = MaterialTheme.colorScheme.onPrimaryContainer, modifier = Modifier.weight(1f))
        Switch(checked = checked, onCheckedChange = onCheck)
    }
}

// ── Booked Park Card ──────────────────────────────────────────────────────────

@Composable
private fun BookedParkCard(
    booking: Booking,
    isExpanded: Boolean,
    onToggle: () -> Unit,
    onEditPlate: () -> Unit,
) {
    val totalCost = booking.days * 24 * booking.pricePerHour

    Card(
        modifier  = Modifier.fillMaxWidth(),
        colors    = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface),
        elevation = CardDefaults.cardElevation(defaultElevation = 1.dp)
    ) {
        Column(
            modifier            = Modifier.fillMaxWidth().padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(4.dp)
        ) {
            Row(
                modifier              = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment     = Alignment.CenterVertically
            ) {
                Column(modifier = Modifier.weight(1f)) {
                    Text(booking.name,        style = MaterialTheme.typography.bodyLarge)
                    Text(booking.carPlate,    style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant)
                    Text(booking.parkingName, style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant)
                }
                IconButton(onClick = onToggle) {
                    Icon(
                        painter = painterResource(
                            if (isExpanded) Res.drawable.expand_less else Res.drawable.expand_more
                        ),
                        contentDescription = if (isExpanded) "Collapse" else "Expand"
                    )
                }
            }

            if (isExpanded) {
                HorizontalDivider()
                Row(horizontalArrangement = Arrangement.spacedBy(24.dp)) {
                    LabelValue("Duration",   "${booking.days} day(s)")
                    LabelValue("Rate",       "€ ${booking.pricePerHour}/h")
                    LabelValue("Total cost", "€ ${formatPrice(totalCost)}")
                }
                Text("Slot: ${booking.slotCode}", style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant)
                OutlinedButton(onClick = onEditPlate, modifier = Modifier.align(Alignment.End)) {
                    Text("Edit plate")
                }
            }
        }
    }
}

@Composable
private fun LabelValue(label: String, value: String) {
    Column {
        Text(label, style = MaterialTheme.typography.labelSmall,
            color = MaterialTheme.colorScheme.onSurfaceVariant)
        Text(value, style = MaterialTheme.typography.bodySmall)
    }
}

// ── New Booking Dialog ────────────────────────────────────────────────────────

@Composable
private fun NewBookingDialog(
    availableParkings: List<Parking>,
    availablePlates: List<Plate>,
    onConfirm: (name: String, parkingId: String, plate: String, days: Int) -> Unit,
    onDismiss: () -> Unit,
) {
    var step            by remember { mutableStateOf(0) }
    var bookingName     by remember { mutableStateOf("") }
    var parkingQuery    by remember { mutableStateOf("") }
    var selectedParking by remember { mutableStateOf<Parking?>(null) }
    var selectedPlate   by remember { mutableStateOf(availablePlates.firstOrNull()?.plateText ?: "") }
    var daysText        by remember { mutableStateOf("1") }

    val days  = daysText.toIntOrNull()?.coerceAtLeast(1) ?: 1
    val price = selectedParking?.pricePerHour ?: 0.0
    val total = days * 24 * price

    val filtered = remember(parkingQuery, availableParkings) {
        if (parkingQuery.isBlank()) availableParkings
        else availableParkings.filter {
            it.name.contains(parkingQuery, ignoreCase = true) ||
                    it.address.contains(parkingQuery, ignoreCase = true)
        }
    }

    AlertDialog(
        onDismissRequest = onDismiss,
        title = { Text(if (step == 0) "New booking" else "Confirm booking") },
        text  = {
            if (step == 0) {
                Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
                    OutlinedTextField(
                        value = bookingName, onValueChange = { bookingName = it },
                        label = { Text("Booking name") }, modifier = Modifier.fillMaxWidth(), singleLine = true,
                    )
                    OutlinedTextField(
                        value = parkingQuery, onValueChange = { parkingQuery = it },
                        label = { Text("Search parking") },
                        leadingIcon = { Icon(painterResource(Res.drawable.local_parking), null) },
                        modifier = Modifier.fillMaxWidth(), singleLine = true,
                    )
                    Column(verticalArrangement = Arrangement.spacedBy(4.dp)) {
                        filtered.take(4).forEach { parking ->
                            Surface(
                                modifier = Modifier.fillMaxWidth(),
                                shape    = MaterialTheme.shapes.small,
                                color    = if (selectedParking?.id == parking.id)
                                    MaterialTheme.colorScheme.primaryContainer
                                else MaterialTheme.colorScheme.surfaceVariant,
                                onClick  = { selectedParking = parking; parkingQuery = parking.name }
                            ) {
                                Row(
                                    modifier = Modifier.padding(horizontal = 12.dp, vertical = 8.dp),
                                    horizontalArrangement = Arrangement.SpaceBetween
                                ) {
                                    Text(parking.name, style = MaterialTheme.typography.bodySmall)
                                    Text("€${parking.pricePerHour}/h", style = MaterialTheme.typography.labelSmall)
                                }
                            }
                        }
                    }
                    OutlinedTextField(
                        value = daysText, onValueChange = { daysText = it.filter { c -> c.isDigit() } },
                        label = { Text("Days") },
                        keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),
                        modifier = Modifier.fillMaxWidth(), singleLine = true,
                    )
                    if (availablePlates.isNotEmpty()) {
                        Text("Select plate", style = MaterialTheme.typography.labelMedium)
                        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                            availablePlates.forEach { plate ->
                                FilterChip(
                                    selected = selectedPlate == plate.plateText,
                                    onClick  = { selectedPlate = plate.plateText },
                                    label    = { Text(plate.plateText) },
                                )
                            }
                        }
                    }
                }
            } else {
                Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                    ConfirmRow("Booking name", bookingName)
                    ConfirmRow("Parking",      selectedParking?.name ?: "-")
                    ConfirmRow("Plate",        selectedPlate)
                    ConfirmRow("Duration",     "$days day(s)")
                    ConfirmRow("Rate",         "€ $price/h")
                    HorizontalDivider()
                    ConfirmRow("Total cost", "€ ${formatPrice(total)}", highlight = true)
                }
            }
        },
        confirmButton = {
            Button(
                onClick = {
                    if (step == 0) step = 1
                    else {
                        val pId = selectedParking?.id ?: return@Button
                        onConfirm(bookingName, pId, selectedPlate, days)
                    }
                },
                enabled = if (step == 0)
                    bookingName.isNotBlank() && selectedParking != null && selectedPlate.isNotBlank()
                else true
            ) { Text(if (step == 0) "Next" else "Confirm") }
        },
        dismissButton = {
            TextButton(onClick = { if (step == 1) step = 0 else onDismiss() }) {
                Text(if (step == 1) "Back" else "Cancel")
            }
        }
    )
}

@Composable
private fun ConfirmRow(label: String, value: String, highlight: Boolean = false) {
    Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
        Text(label, style = MaterialTheme.typography.bodySmall,
            color = MaterialTheme.colorScheme.onSurfaceVariant)
        Text(
            text  = value,
            style = if (highlight) MaterialTheme.typography.titleSmall else MaterialTheme.typography.bodySmall,
            color = if (highlight) MaterialTheme.colorScheme.primary   else MaterialTheme.colorScheme.onSurface
        )
    }
}

// ── Edit Plate Dialog ─────────────────────────────────────────────────────────

@Composable
private fun EditPlateDialog(
    currentPlate: String,
    availablePlates: List<Plate>,
    onConfirm: (String) -> Unit,
    onDismiss: () -> Unit,
) {
    var selectedPlate by remember { mutableStateOf(currentPlate) }

    AlertDialog(
        onDismissRequest = onDismiss,
        title = { Text("Change plate") },
        text  = {
            Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                Text("Select the plate to associate with this booking:",
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant)
                availablePlates.forEach { plate ->
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.spacedBy(8.dp)
                    ) {
                        RadioButton(selected = selectedPlate == plate.plateText,
                            onClick = { selectedPlate = plate.plateText })
                        Column {
                            Text(plate.name,      style = MaterialTheme.typography.bodyMedium)
                            Text(plate.plateText, style = MaterialTheme.typography.bodySmall,
                                color = MaterialTheme.colorScheme.onSurfaceVariant)
                        }
                    }
                }
            }
        },
        confirmButton = {
            Button(onClick = { onConfirm(selectedPlate) }, enabled = selectedPlate != currentPlate) {
                Text("Save")
            }
        },
        dismissButton = { TextButton(onClick = onDismiss) { Text("Cancel") } }
    )
}

// ── Helpers ───────────────────────────────────────────────────────────────────

/**
 * Computes elapsed hours from an ISO-8601 UTC string using kotlinx-datetime 0.6.0.
 * API: Instant.parse(), Clock.System.now(), minus operator returns Duration,
 * Duration.inWholeSeconds (not inWholeMinutes in 0.6.0 — use inWholeSeconds / 3600.0).
 */
private fun computeElapsedHours(startedAt: String): Double {
    return try {
        val start    = Instant.parse(startedAt)
        val now      = Clock.System.now()
        val duration = now - start
        duration.inWholeSeconds / 3600.0
    } catch (_: Exception) {
        0.0
    }
}

/**
 * Formats ISO-8601 UTC string to "HH:mm DD/MM/YYYY" in the device local timezone.
 * Uses kotlinx-datetime 0.6.0: toLocalDateTime(TimeZone) returns LocalDateTime,
 * whose properties are .hour, .minute, .dayOfMonth, .monthNumber, .year.
 */
private fun formatStartedAt(startedAt: String): String {
    return try {
        val instant = Instant.parse(startedAt)
        val local   = instant.toLocalDateTime(TimeZone.currentSystemDefault())
        // Pad manually — no String.format in commonMain
        val h  = local.hour.toString().padStart(2, '0')
        val m  = local.minute.toString().padStart(2, '0')
        val d  = local.day.toString().padStart(2, '0')
        val mo = local.month.number.toString().padStart(2, '0')
        "$h:$m $d/$mo/${local.year}"
    } catch (_: Exception) {
        startedAt
    }
}

/**
 * KMP-safe price formatting — no String.format("%.2f") which is JVM-only.
 * Rounds to 2 decimal places and builds the string manually.
 */
private fun formatPrice(value: Double): String {
    val rounded  = kotlin.math.round(value * 100) / 100.0
    val intPart  = rounded.toLong()
    val fracPart = kotlin.math.round((rounded - intPart) * 100).toString().padStart(2, '0')
    return "$intPart.$fracPart"
}