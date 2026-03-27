package org.iot.app.data.remote

import io.ktor.client.HttpClient
import io.ktor.client.call.body
import io.ktor.client.request.post
import io.ktor.client.request.setBody
import org.iot.app.data.remote.dto.AuthResponse
import org.iot.app.data.remote.dto.LoginRequest
import org.iot.app.data.remote.dto.RegisterRequest

class AuthApi(private val client: HttpClient) {

    suspend fun login(request: LoginRequest): AuthResponse {
        return client.post("auth/login") { // Sostituisci con il tuo endpoint OpenAPI corretto
            setBody(request)
        }.body()
    }

    suspend fun register(request: RegisterRequest): AuthResponse {
        return client.post("auth/register") { // Sostituisci con il tuo endpoint OpenAPI corretto
            setBody(request)
        }.body()
    }
}