package com.diplom.pizzashop.data

import android.content.Context
import android.content.SharedPreferences

object TokenManager {
    private const val PREFS_NAME = "pizza_prefs"
    private const val TOKEN_KEY = "access_token"
    private var prefs: SharedPreferences? = null

    fun init(context: Context) {
        if (prefs == null) {
            prefs = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
        }
    }

    fun saveToken(token: String?) {
        prefs?.edit()?.putString(TOKEN_KEY, token)?.apply()
    }

    fun getToken(): String? {
        return prefs?.getString(TOKEN_KEY, null)
    }
    
    fun clearToken() {
        prefs?.edit()?.remove(TOKEN_KEY)?.apply()
    }
}