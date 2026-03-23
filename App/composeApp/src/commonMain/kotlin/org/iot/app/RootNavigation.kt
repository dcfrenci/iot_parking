package org.iot.app

import androidx.compose.foundation.layout.padding
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.runtime.remember
import androidx.compose.ui.Modifier
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.currentBackStackEntryAsState
import androidx.navigation.compose.rememberNavController
import androidx.compose.runtime.getValue
import app.composeapp.generated.resources.Res
import app.composeapp.generated.resources.home
import app.composeapp.generated.resources.settings
import app.composeapp.generated.resources.map
import org.iot.app.domain.usecase.*
import org.iot.app.screen.home.HomeViewModel
import org.iot.app.screen.map.MapViewModel
import org.iot.app.screen.settings.SettingsViewModel
import org.iot.app.screen.HomeScreen
import org.iot.app.screen.MapScreen
import org.iot.app.screens.SettingsScreen
import org.jetbrains.compose.resources.DrawableResource
import org.jetbrains.compose.resources.painterResource


// ── Screen sealed class ───────────────────────────────────────────────────────

sealed class Screen(
    val route: String,
    val title: String,
    val icon: DrawableResource,
) {
    data object Map      : Screen("map",      "Map",     Res.drawable.map)
    data object Home     : Screen("home",     "Home",    Res.drawable.home)
    data object Settings : Screen("settings", "Setting", Res.drawable.settings)
}

// ── Root Navigation ───────────────────────────────────────────────────────────

@Composable
fun RootNavigation(
    getNearbyParkings : GetNearbyParkingsUseCase,
    getCurrentParking : GetCurrentParkingUseCase,
    getBookings       : GetBookingsUseCase,
    getUser           : GetUserUseCase,
    getPlates         : GetPlatesUseCase,
    setPlateActive    : SetPlateActiveUseCase,
    getPaymentMethod  : GetPaymentMethodUseCase,
    getPreferences    : GetPreferencesUseCase,
    savePreferences   : SavePreferencesUseCase,
) {
    val navController = rememberNavController()
    val navBackStackEntry by navController.currentBackStackEntryAsState()
    val currentRoute = navBackStackEntry?.destination?.route

    val bottomNavScreens = listOf(Screen.Map, Screen.Home, Screen.Settings)

    // ── ViewModels (creati una volta sola per tutta la sessione) ──────────────
    val mapViewModel = remember {
        MapViewModel(getNearbyParkings)
    }
    val homeViewModel = remember {
        HomeViewModel(getCurrentParking, getBookings)
    }
    val settingsViewModel = remember {
        SettingsViewModel(getUser, getPlates, setPlateActive, getPaymentMethod, getPreferences, savePreferences)
    }

    Scaffold(
        bottomBar = {
            NavigationBar {
                bottomNavScreens.forEach { screen ->
                    NavigationBarItem(
                        selected = currentRoute == screen.route,
                        onClick  = {
                            navController.navigate(screen.route) {
                                popUpTo(navController.graph.startDestinationId) { saveState = true }
                                launchSingleTop = true
                                restoreState    = true
                            }
                        },
                        icon  = { Icon(painter = painterResource(screen.icon), contentDescription = screen.title) },
                        label = { Text(screen.title) }
                    )
                }
            }
        }
    ) { innerPadding ->
        NavHost(
            navController    = navController,
            startDestination = Screen.Home.route,
            modifier         = Modifier.padding(innerPadding)
        ) {
            composable(Screen.Map.route)      { MapScreen(viewModel = mapViewModel) }
            composable(Screen.Home.route)     { HomeScreen(viewModel = homeViewModel) }
            composable(Screen.Settings.route) { SettingsScreen(viewModel = settingsViewModel) }
        }
    }
}
