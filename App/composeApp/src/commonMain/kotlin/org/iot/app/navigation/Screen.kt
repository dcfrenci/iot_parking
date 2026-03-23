package org.iot.app.navigation

import app.composeapp.generated.resources.Res
import app.composeapp.generated.resources.home
import app.composeapp.generated.resources.map
import app.composeapp.generated.resources.settings
import org.jetbrains.compose.resources.DrawableResource

sealed class Screen(
    val route: String,
    val title: String,
    val icon: DrawableResource
) {
    data object Home : Screen(
        route = "home",
        title = "Home",
        icon = Res.drawable.home
    )
    data object Map : Screen(
        route = "map",
        title = "Map",
        icon = Res.drawable.map
    )
    data object Settings : Screen(
        route = "settings",
        title = "Settings",
        icon = Res.drawable.settings
    )
}