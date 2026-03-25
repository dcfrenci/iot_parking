package org.iot.app.platform

import androidx.compose.runtime.Composable
import androidx.compose.runtime.remember
import kotlinx.cinterop.ExperimentalForeignApi
import platform.Foundation.NSURL
import platform.PhotosUI.PHPickerConfiguration
import platform.PhotosUI.PHPickerFilter
import platform.PhotosUI.PHPickerResult
import platform.PhotosUI.PHPickerViewController
import platform.PhotosUI.PHPickerViewControllerDelegateProtocol
import platform.UIKit.UIApplication
import platform.darwin.NSObject

/**
 * iOS implementation.
 * Place this file in iosMain/kotlin/org/iot/app/platform/ImagePicker.ios.kt
 */
actual class ImagePicker actual constructor(
    private val onResult: (uri: String?) -> Unit
) {
    @OptIn(ExperimentalForeignApi::class)
    actual fun launch() {
        val config = PHPickerConfiguration().apply {
            filter = PHPickerFilter.imagesFilter
            selectionLimit = 1
        }
        val picker = PHPickerViewController(configuration = config)
        val delegate = object : NSObject(), PHPickerViewControllerDelegateProtocol {
            override fun picker(
                picker: PHPickerViewController,
                didFinishPicking: List<*>
            ) {
                picker.dismissViewControllerAnimated(true, null)
                val result = (didFinishPicking.firstOrNull() as? PHPickerResult)
                result?.itemProvider?.loadFileRepresentationForTypeIdentifier(
                    typeIdentifier = "public.image"
                ) { url, _ ->
                    onResult((url as? NSURL)?.absoluteString)
                } ?: onResult(null)
            }
        }
        picker.delegate = delegate
        UIApplication.sharedApplication.keyWindow
            ?.rootViewController
            ?.presentViewController(picker, animated = true, completion = null)
    }
}

@Composable
actual fun rememberImagePicker(onResult: (uri: String?) -> Unit): ImagePicker =
    remember { ImagePicker(onResult) }
