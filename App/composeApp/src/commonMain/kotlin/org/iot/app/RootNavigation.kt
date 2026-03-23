package org.iot.app

import androidx.compose.foundation.layout.padding
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.currentBackStackEntryAsState
import androidx.navigation.compose.rememberNavController
import app.composeapp.generated.resources.Res
import app.composeapp.generated.resources.home
import app.composeapp.generated.resources.settings
import app.composeapp.generated.resources.map
import org.iot.app.screens.HomeScreen
import org.iot.app.screens.MapScreen
import org.iot.app.screens.SettingsScreen
import org.jetbrains.compose.resources.DrawableResource
import org.jetbrains.compose.resources.painterResource

// ── Sealed class Screen ──────────────────────────────────────────────────────

sealed class Screen(
    val route: String,
    val title: String,
    val icon: DrawableResource
) {
    data object Map : Screen(
        route = "map",
        title = "Map",
        icon = Res.drawable.map
    )
    data object Home : Screen(
        route = "home",
        title = "Home",
        icon = Res.drawable.home
    )
    data object Settings : Screen(
        route = "settings",
        title = "Setting",
        icon = Res.drawable.settings
    )
}

// ── Root Navigation ──────────────────────────────────────────────────────────

@Composable
fun RootNavigation() {
    val navController = rememberNavController()

    val bottomNavScreens = listOf(
        Screen.Map,
        Screen.Home,
        Screen.Settings
    )

    val navBackStackEntry by navController.currentBackStackEntryAsState()
    val currentRoute = navBackStackEntry?.destination?.route

    Scaffold(
        bottomBar = {
            NavigationBar {
                bottomNavScreens.forEach { screen ->
                    NavigationBarItem(
                        selected = currentRoute == screen.route,
                        onClick = {
                            navController.navigate(screen.route) {
                                popUpTo(navController.graph.startDestinationId) {
                                    saveState = true
                                }
                                launchSingleTop = true
                                restoreState = true
                            }
                        },
                        icon = {
                            Icon(
                                painter = painterResource(screen.icon),
                                contentDescription = screen.title
                            )
                        },
                        label = { Text(screen.title) }
                    )
                }
            }
        }
    ) { innerPadding ->
        NavHost(
            navController = navController,
            startDestination = Screen.Home.route,
            modifier = Modifier.padding(innerPadding)
        ) {
            composable(Screen.Map.route)      { MapScreen() }
            composable(Screen.Home.route)     { HomeScreen() }
            composable(Screen.Settings.route) { SettingsScreen() }
        }
    }
}