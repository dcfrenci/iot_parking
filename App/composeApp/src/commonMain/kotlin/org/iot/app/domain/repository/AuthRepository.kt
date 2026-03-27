package org.iot.app.domain.repository

import org.iot.app.data.remote.dto.AuthResponse
import org.iot.app.data.remote.dto.LoginRequest
import org.iot.app.data.remote.dto.RegisterRequest

interface AuthRepository {
    suspend fun login(request: LoginRequest): Result<AuthResponse>
    suspend fun register(request: RegisterRequest): Result<AuthResponse>
}