package org.iot.app

import androidx.compose.foundation.layout.padding
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.currentBackStackEntryAsState
import androidx.navigation.compose.rememberNavController
import app.composeapp.generated.resources.Res
import app.composeapp.generated.resources.home
import app.composeapp.generated.resources.map
import app.composeapp.generated.resources.settings
import org.iot.app.domain.usecase.*
import org.iot.app.screen.HomeScreen
import org.iot.app.screen.MapScreen
import org.iot.app.screen.RegisterScreen
import org.iot.app.screen.home.HomeViewModel
import org.iot.app.screen.map.MapViewModel
import org.iot.app.screen.settings.SettingsViewModel
import org.iot.app.screens.SettingsScreen

// New imports for Auth
import org.iot.app.screen.login.LoginScreen
import org.iot.app.screen.login.LoginViewModel
import org.iot.app.screen.register.RegisterViewModel

import org.jetbrains.compose.resources.DrawableResource
import org.jetbrains.compose.resources.painterResource

// 1. Updated Screen sealed class to include Auth routes.
// The icon is now nullable (DrawableResource?) because Login and Register don't use bottom bar icons.
sealed class Screen(
    val route: String,
    val title: String,
    val icon: DrawableResource?,
) {
    data object Login    : Screen("login",    "Login",    null)
    data object Register : Screen("register", "Register", null)

    data object Map      : Screen("map",      "Map",     Res.drawable.map)
    data object Home     : Screen("home",     "Home",    Res.drawable.home)
    data object Settings : Screen("settings", "Setting", Res.drawable.settings)
}

@Composable
fun RootNavigation(
    login               : LoginUseCase,
    register            : RegisterUseCase,
    getNearbyParkings   : GetNearbyParkingsUseCase,
    getActiveSessions   : GetActiveSessionsUseCase,
    getBookings         : GetBookingsUseCase,
    createBooking       : CreateBookingUseCase,
    updateBooking       : UpdateBookingUseCase,
    deleteBooking       : DeleteBookingUseCase,
    getUser             : GetUserUseCase,
    getPlates           : GetPlatesUseCase,
    addPlate            : AddPlateUseCase,
    deletePlate         : DeletePlateUseCase,
    getPaymentMethod    : GetPaymentMethodUseCase,
    updatePaymentMethod : UpdatePaymentMethodUseCase,
    getPreferences      : GetPreferencesUseCase,
    savePreferences     : SavePreferencesUseCase,
) {
    val navController = rememberNavController()
    val navBackStackEntry by navController.currentBackStackEntryAsState()
    val currentRoute = navBackStackEntry?.destination?.route

    // 2. Define which screens should actually show the bottom navigation bar.
    val bottomNavScreens = listOf(Screen.Map, Screen.Home, Screen.Settings)
    val showBottomBar = bottomNavScreens.any { it.route == currentRoute }

    val loginViewModel = remember {
        LoginViewModel(login)
    }

    val registerViewModel = remember {
        RegisterViewModel(register)
    }

    val mapViewModel = remember {
        MapViewModel(getNearbyParkings)
    }

    val homeViewModel = remember {
        HomeViewModel(
            getActiveSessions = getActiveSessions,
            getBookings       = getBookings,
            getPlates         = getPlates,
            createBooking     = createBooking,
            updateBooking     = updateBooking,
            deleteBooking     = deleteBooking,
        )
    }

    val settingsViewModel = remember {
        SettingsViewModel(
            getUser             = getUser,
            getPlates           = getPlates,
            addPlate            = addPlate,
            deletePlate         = deletePlate,
            getPaymentMethod    = getPaymentMethod,
            updatePaymentMethod = updatePaymentMethod,
            getPreferences      = getPreferences,
            savePreferences     = savePreferences,
        )
    }

    Scaffold(
        bottomBar = {
            // 4. Conditionally render the NavigationBar only if we are on a main app screen
            if (showBottomBar) {
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
                            icon  = {
                                // Safely unwrap the icon since it is now nullable
                                screen.icon?.let {
                                    Icon(painter = painterResource(it), contentDescription = screen.title)
                                }
                            },
                            label = { Text(screen.title) }
                        )
                    }
                }
            }
        }
    ) { innerPadding ->
        NavHost(
            navController    = navController,
            // 5. Change the start destination so the app boots to the Login screen
            startDestination = Screen.Login.route,
            modifier         = Modifier.padding(innerPadding)
        ) {

            // --- Auth Routes ---
            composable(Screen.Login.route) {
                LoginScreen(
                    viewModel = loginViewModel,
                    onLoginSuccess = {
                        // Navigate to Home and clear the login screen from the back history
                        navController.navigate(Screen.Home.route) {
                            popUpTo(Screen.Login.route) { inclusive = true }
                        }
                    },
                    onNavigateToRegister = {
                        navController.navigate(Screen.Register.route)
                    }
                )
            }

            composable(Screen.Register.route) {
                RegisterScreen(
                    viewModel = registerViewModel,
                    onRegisterSuccess = {
                        // On success, take them to the main app and clear auth screens from history
                        navController.navigate(Screen.Home.route) {
                            popUpTo(Screen.Login.route) { inclusive = true }
                        }
                    },
                    onBackToLogin = {
                        // Pop the backstack to return to the Login screen
                        navController.popBackStack()
                    }
                )
            }

            // --- Main App Routes ---
            composable(Screen.Map.route)      { MapScreen(viewModel = mapViewModel) }
            composable(Screen.Home.route)     { HomeScreen(viewModel = homeViewModel) }
            composable(Screen.Settings.route) { SettingsScreen(viewModel = settingsViewModel) }
        }
    }
}