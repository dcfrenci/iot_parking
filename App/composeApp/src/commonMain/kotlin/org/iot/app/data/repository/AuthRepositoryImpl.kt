package org.iot.app.data.repository

import org.iot.app.data.remote.AuthApi
import org.iot.app.data.remote.dto.AuthResponse
import org.iot.app.data.remote.dto.LoginRequest
import org.iot.app.data.remote.dto.RegisterRequest
import org.iot.app.domain.repository.AuthRepository

class AuthRepositoryImpl(private val api: AuthApi) : AuthRepository {
    override suspend fun login(request: LoginRequest): Result<AuthResponse> {
        return try {
            Result.success(api.login(request))
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    override suspend fun register(request: RegisterRequest): Result<AuthResponse> {
        return try {
            Result.success(api.register(request))
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}