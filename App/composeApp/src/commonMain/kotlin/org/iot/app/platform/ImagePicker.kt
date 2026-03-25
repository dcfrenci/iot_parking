package org.iot.app.platform

/**
 * Expect class: each platform provides its own implementation.
 *
 * Usage in Composable:
 *   val picker = rememberImagePicker { uri -> /* handle uri string */ }
 *   picker.launch()
 */
expect class ImagePicker(
    onResult: (uri: String?) -> Unit
) {
    fun launch()
}

/**
 * Composable helper to remember an ImagePicker instance that survives recomposition.
 * Declared as expect so each platform can wire the Activity/UIViewController lifecycle.
 */
@androidx.compose.runtime.Composable
expect fun rememberImagePicker(onResult: (uri: String?) -> Unit): ImagePicker
