package com.diplom.pizzashop.ui.viewmodels

import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.diplom.pizzashop.data.TokenManager
import com.diplom.pizzashop.data.api.PizzaApi
import com.diplom.pizzashop.data.api.RetrofitClient
import com.diplom.pizzashop.data.model.*
import com.diplom.pizzashop.data.repository.PizzaRepository
import kotlinx.coroutines.launch
import java.util.UUID

class MenuViewModel : ViewModel() {
    private val repository = PizzaRepository()
    var products by mutableStateOf<List<Product>>(emptyList())
    var categories by mutableStateOf<List<Category>>(emptyList())
    var isLoading by mutableStateOf(false)
    var error by mutableStateOf<String?>(null)
    var selectedCategory by mutableStateOf<Int?>(null)

    init { loadData() }

    fun loadData() {
        viewModelScope.launch {
            isLoading = true
            try {
                products = repository.getProducts()
                categories = repository.getCategories()
                error = null
            } catch (e: Exception) { error = "Ошибка: ${e.message}" } 
            finally { isLoading = false }
        }
    }
    fun selectCategory(id: Int?) { selectedCategory = id }
    val filteredProducts: List<Product> get() = if (selectedCategory == null) products else products.filter { it.category_id == selectedCategory }
}

class CartViewModel : ViewModel() {
    private val repository = PizzaRepository()
    var items by mutableStateOf<List<CartItem>>(emptyList())
    var isLoading by mutableStateOf(false)
    var error by mutableStateOf<String?>(null)

    init { loadCart() }

    fun loadCart() {
        viewModelScope.launch {
            isLoading = true
            try {
                items = repository.getCart()
                error = null
            } catch (e: Exception) { error = "Ошибка корзины: ${e.message}" } 
            finally { isLoading = false }
        }
    }

    fun addToCart(productId: Int) {
        viewModelScope.launch {
            try {
                items = repository.addToCart(productId)
            } catch (e: Exception) { error = "Ошибка: ${e.message}" }
        }
    }
    fun clearCart() {
        viewModelScope.launch {
            try {
                if (repository.clearCart()) items = emptyList()
            } catch (e: Exception) { error = "Ошибка: ${e.message}" }
        }
    }
    val total: Double get() = items.sumOf { it.subtotal }
}

class ChatViewModel : ViewModel() {
    private val repository = PizzaRepository()
    private val sessionId = UUID.randomUUID().toString()
    var messages by mutableStateOf<List<ChatMessage>>(listOf(ChatMessage("assistant", "Привет! Я WOKI 🍕")))
    var isTyping by mutableStateOf(false)

    fun sendMessage(text: String) {
        if (text.isBlank()) return
        messages = messages + ChatMessage("user", text)
        isTyping = true
        viewModelScope.launch {
            try {
                val response = repository.sendChatMessage(text, sessionId)
                if (response != null) messages = messages + ChatMessage("assistant", response)
            } finally { isTyping = false }
        }
    }
}

class AuthViewModel : ViewModel() {
    private val api = RetrofitClient.api
    
    var isAuthenticated by mutableStateOf(false)
    var userRole by mutableStateOf<String?>("guest")
    var isLoading by mutableStateOf(false)
    var error by mutableStateOf<String?>(null)

    init {
        // Проверяем, есть ли сохраненный токен при запуске
        if (TokenManager.getToken() != null) {
            isAuthenticated = true
            loadProfile()
        }
    }

    fun login(login: String, password: String) {
        viewModelScope.launch {
            isLoading = true
            error = null
            try {
                val response = api.login(PizzaApi.LoginRequest(login, password))
                TokenManager.saveToken(response.access_token)
                isAuthenticated = true
                loadProfile()
            } catch (e: Exception) {
                error = "Ошибка входа: ${e.message}"
            } finally {
                isLoading = false
            }
        }
    }

    private fun loadProfile() {
        viewModelScope.launch {
            try {
                val profile = api.getProfile()
                userRole = profile.role ?: "client"
            } catch (e: Exception) {
                // Если профиль не грузится, сбрасываем авторизацию
                logout()
            }
        }
    }

    fun logout() {
        TokenManager.clearToken()
        isAuthenticated = false
        userRole = "guest"
    }
}