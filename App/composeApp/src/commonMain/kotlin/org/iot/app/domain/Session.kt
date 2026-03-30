package org.iot.app.domain

/**
 * A simple in-memory session manager to hold the logged-in user's account ID.
 * In a production app, you might back this with Multiplatform Settings or DataStore.
 */
object SessionManager {
    var currentAccountId: Int = -1
        private set

    fun loginUser(accountId: Int) {
        currentAccountId = accountId
    }

    fun logout() {
        currentAccountId = -1
    }
}