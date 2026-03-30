package org.iot.app.data.remote.dto

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

@Serializable
data class LoginRequest(
    val email: String,
    @SerialName("pass") val password: String
)

@Serializable
data class RegisterRequest(
    val name: String,
    val email: String,
    @SerialName("pass") val password: String
)

@Serializable
data class AuthResponse(
    @SerialName("account_id") val accountId: Int,
    val name: String,
    val email: String
)