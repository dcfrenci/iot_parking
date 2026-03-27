package org.iot.app.screen.register

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch

class RegisterViewModel(
    // Inject your use cases here later TODO
) : ViewModel() {

    private val _uiState = MutableStateFlow(RegisterUiState())
    val uiState: StateFlow<RegisterUiState> = _uiState.asStateFlow()

    fun onNameChange(name: String) {
        _uiState.update { it.copy(name = name, errorMessage = null) }
    }

    fun onEmailChange(email: String) {
        _uiState.update { it.copy(email = email, errorMessage = null) }
    }

    fun onPasswordChange(password: String) {
        _uiState.update { it.copy(password = password, errorMessage = null) }
    }

    fun onConfirmPasswordChange(confirmPassword: String) {
        _uiState.update { it.copy(confirmPassword = confirmPassword, errorMessage = null) }
    }

    fun onRegisterClick(onSuccess: () -> Unit) {
        val currentState = _uiState.value

        // 1. Check for empty fields
        if (currentState.name.isBlank() ||
            currentState.email.isBlank() ||
            currentState.password.isBlank() ||
            currentState.confirmPassword.isBlank()
        ) {
            _uiState.update { it.copy(errorMessage = "All fields must be filled") }
            return
        }

        // 2. Check if passwords match
        if (currentState.password != currentState.confirmPassword) {
            _uiState.update { it.copy(errorMessage = "Passwords do not match") }
            return
        }

        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true) }

            // Simulate network request / Use Case execution TODO
            delay(1500)

            // Assuming success:
            _uiState.update { it.copy(isLoading = false) }
            onSuccess()
        }
    }
}

data class RegisterUiState(
    val name: String = "",
    val email: String = "",
    val password: String = "",
    val confirmPassword: String = "",
    val isLoading: Boolean = false,
    val errorMessage: String? = null
)