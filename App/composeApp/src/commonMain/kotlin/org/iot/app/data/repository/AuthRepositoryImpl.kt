package org.iot.app.data.repository

import org.iot.app.data.remote.AuthApi
import org.iot.app.data.remote.dto.LoginRequest
import org.iot.app.data.remote.dto.RegisterRequest
import org.iot.app.domain.model.User
import org.iot.app.domain.repository.AuthRepository

class AuthRepositoryImpl(private val api: AuthApi) : AuthRepository {
    override suspend fun login(request: LoginRequest): Result<User> = runCatching {
        api.login(request).let { User(it.accountId, it.name, it.email) }
    }

    override suspend fun register(request: RegisterRequest): Result<User> = runCatching {
        api.register(request).let { User(it.accountId, it.name, it.email) }
    }
}