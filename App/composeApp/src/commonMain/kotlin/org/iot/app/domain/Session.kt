package org.iot.app.domain

import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow

object SessionManager {
    // Hold the state reactively
    private val _currentAccountId = MutableStateFlow(-1)
    val currentAccountId: StateFlow<Int> = _currentAccountId.asStateFlow()

    fun loginUser(accountId: Int) {
        _currentAccountId.value = accountId
    }

    fun logout() {
        _currentAccountId.value = -1
    }
}