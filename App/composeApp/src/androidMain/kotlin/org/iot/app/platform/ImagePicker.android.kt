package org.iot.app.platform

import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.runtime.Composable
import androidx.compose.runtime.remember

/**
 * Android implementation.
 * Place this file in androidMain/kotlin/org/iot/app/platform/ImagePicker.android.kt
 */
actual class ImagePicker actual constructor(
    private val onResult: (uri: String?) -> Unit
) {
    internal var launcher: (() -> Unit)? = null

    actual fun launch() {
        launcher?.invoke()
    }
}

@Composable
actual fun rememberImagePicker(onResult: (uri: String?) -> Unit): ImagePicker {
    val picker = remember { ImagePicker(onResult) }
    val launcher = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.GetContent()
    ) { uri ->
        onResult(uri?.toString())
    }
    picker.launcher = { launcher.launch("image/*") }
    return picker
}
