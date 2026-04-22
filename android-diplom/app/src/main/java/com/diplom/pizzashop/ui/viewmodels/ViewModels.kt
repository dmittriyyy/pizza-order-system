package com.diplom.pizzashop.ui.viewmodels

import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.diplom.pizzashop.data.TokenManager
import com.diplom.pizzashop.data.api.AppNotification
import com.diplom.pizzashop.data.api.CreateOrderRequest
import com.diplom.pizzashop.data.api.Feedback
import com.diplom.pizzashop.data.api.PizzaApi
import com.diplom.pizzashop.data.api.RecommendationResponse
import com.diplom.pizzashop.data.api.RetrofitClient
import com.diplom.pizzashop.data.api.UpdateEmployeeRequest
import com.diplom.pizzashop.data.model.*
import com.diplom.pizzashop.data.repository.PizzaRepository
import kotlinx.coroutines.delay
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

    fun getProductById(id: Int): Product? = products.find { it.id == id }
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

    fun updateQuantity(productId: Int, quantity: Int) {
        viewModelScope.launch {
            try {
                if (quantity > 0) {
                    items = repository.updateCartItem(productId, quantity)
                } else {
                    items = repository.removeCartItem(productId)
                }
            } catch (e: Exception) { error = "Ошибка: ${e.message}" }
        }
    }

    fun removeItem(productId: Int) {
        viewModelScope.launch {
            try {
                items = repository.removeCartItem(productId)
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

    fun createOrder(
        request: CreateOrderRequest,
        onSuccess: () -> Unit = {},
        onError: (String) -> Unit = {}
    ) {
        viewModelScope.launch {
            isLoading = true
            try {
                repository.createOrder(request)
                if (repository.clearCart()) items = emptyList()
                error = null
                onSuccess()
            } catch (e: Exception) {
                error = "Ошибка оформления заказа: ${e.message}"
                onError(error ?: "Ошибка оформления заказа")
            } finally {
                isLoading = false
            }
        }
    }

    val total: Double get() = items.sumOf { it.subtotal }
}

class ChatViewModel : ViewModel() {
    private val repository = PizzaRepository()
    private val sessionId = UUID.randomUUID().toString()
    var messages by mutableStateOf<List<ChatMessage>>(listOf(ChatMessage("assistant", "Привет! Я WOKI 🍕")))
    var isTyping by mutableStateOf(false)
    var errorMessage by mutableStateOf<String?>(null)

    fun sendMessage(text: String, onSuccess: () -> Unit = {}) {
        if (text.isBlank()) return
        errorMessage = null
        messages = messages + ChatMessage("user", text)
        isTyping = true
        viewModelScope.launch {
            val result = repository.sendChatMessage(text, sessionId)
            result.fold(
                onSuccess = { response ->
                    messages = messages + ChatMessage("assistant", response)
                    onSuccess()
                },
                onFailure = { error ->
                    messages = messages + ChatMessage("assistant", "⚠️ ${error.message}")
                }
            )
            isTyping = false
        }
    }
}

class AuthViewModel : ViewModel() {
    private val api = RetrofitClient.api

    var isAuthenticated by mutableStateOf(false)
    var userRole by mutableStateOf<String?>("guest")
    var login by mutableStateOf<String?>(null)
    var email by mutableStateOf<String?>(null)
    var firstName by mutableStateOf<String?>(null)
    var lastName by mutableStateOf<String?>(null)
    var phone by mutableStateOf<String?>(null)
    var telegram by mutableStateOf<String?>(null)
    var defaultAddress by mutableStateOf<String?>(null)
    var isLoading by mutableStateOf(false)
    var error by mutableStateOf<String?>(null)

    init {
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
                login = profile.login
                email = profile.email
                firstName = profile.first_name
                lastName = profile.last_name
                phone = profile.phone
                telegram = profile.telegram
                defaultAddress = profile.default_address
            } catch (e: Exception) {
                logout()
            }
        }
    }

    fun updateProfile(
        email: String? = null,
        firstName: String? = null,
        lastName: String? = null,
        phone: String? = null,
        telegram: String? = null,
        defaultAddress: String? = null,
        onSuccess: () -> Unit = {},
        onError: (String) -> Unit = {}
    ) {
        viewModelScope.launch {
            isLoading = true
            error = null
            try {
                val profile = api.updateProfile(
                    PizzaApi.UpdateProfileRequest(
                        email = email,
                        first_name = firstName,
                        last_name = lastName,
                        phone = phone,
                        telegram = telegram,
                        default_address = defaultAddress
                    )
                )
                login = profile.login
                userRole = profile.role ?: "client"
                this@AuthViewModel.email = profile.email
                this@AuthViewModel.firstName = profile.first_name
                this@AuthViewModel.lastName = profile.last_name
                this@AuthViewModel.phone = profile.phone
                this@AuthViewModel.telegram = profile.telegram
                this@AuthViewModel.defaultAddress = profile.default_address
                onSuccess()
            } catch (e: Exception) {
                val message = "Ошибка обновления профиля: ${e.message}"
                error = message
                onError(message)
            } finally {
                isLoading = false
            }
        }
    }

    fun logout() {
        TokenManager.clearToken()
        isAuthenticated = false
        userRole = "guest"
        login = null
        email = null
        firstName = null
        lastName = null
        phone = null
        telegram = null
        defaultAddress = null
    }
}

class AgentSupportViewModel : ViewModel() {
    private val repository = PizzaRepository()

    var notifications by mutableStateOf<List<AppNotification>>(emptyList())
    var recommendation by mutableStateOf<RecommendationResponse?>(null)
    var isLoading by mutableStateOf(false)
    var error by mutableStateOf<String?>(null)

    fun loadAll() {
        viewModelScope.launch {
            isLoading = true
            try {
                notifications = repository.getNotifications(unreadOnly = false).take(5)
                recommendation = repository.getRecommendations()
                error = null
            } catch (e: Exception) {
                error = e.message
            } finally {
                isLoading = false
            }
        }
    }

    fun markNotificationsRead() {
        viewModelScope.launch {
            try {
                repository.markNotificationsRead()
                notifications = notifications.map { it.copy(is_read = true) }
            } catch (_: Exception) {
            }
        }
    }
}

class ReviewsViewModel : ViewModel() {
    private val repository = PizzaRepository()

    var reviews by mutableStateOf<List<Feedback>>(emptyList())
    var isLoading by mutableStateOf(false)
    var error by mutableStateOf<String?>(null)

    fun loadReviews() {
        viewModelScope.launch {
            isLoading = true
            try {
                reviews = repository.getPublicFeedback()
                error = null
            } catch (e: Exception) {
                error = e.message
            } finally {
                isLoading = false
            }
        }
    }
}

// ==================== Кухня ====================

class KitchenViewModel : ViewModel() {
    private val repository = PizzaRepository()
    var orders by mutableStateOf<List<Order>>(emptyList())
    var isLoading by mutableStateOf(false)
    var isProcessing by mutableStateOf(false)
    var error by mutableStateOf<String?>(null)

    init { loadOrders() }

    fun loadOrders() {
        viewModelScope.launch {
            isLoading = true
            try {
                orders = repository.getCookOrders()
                error = null
            } catch (e: Exception) { error = "Ошибка: ${e.message}" }
            finally { isLoading = false }
        }
    }

    fun startCooking(orderId: Int) {
        viewModelScope.launch {
            isProcessing = true
            try {
                repository.startCooking(orderId)
                loadOrders()
            } catch (e: Exception) { error = "Ошибка: ${e.message}" }
            finally { isProcessing = false }
        }
    }

    fun markReady(orderId: Int) {
        viewModelScope.launch {
            isProcessing = true
            try {
                repository.markReady(orderId)
                loadOrders()
            } catch (e: Exception) { error = "Ошибка: ${e.message}" }
            finally { isProcessing = false }
        }
    }

    fun startPeriodicRefresh() {
        viewModelScope.launch {
            while (true) {
                delay(30000) // 30 seconds
                loadOrders()
            }
        }
    }
}

// ==================== Доставка ====================

class DeliveryViewModel : ViewModel() {
    private val repository = PizzaRepository()
    var readyOrders by mutableStateOf<List<Order>>(emptyList())
    var deliveringOrders by mutableStateOf<List<Order>>(emptyList())
    var isLoading by mutableStateOf(false)
    var isProcessing by mutableStateOf(false)
    var error by mutableStateOf<String?>(null)

    init { loadOrders() }

    fun loadOrders() {
        viewModelScope.launch {
            isLoading = true
            try {
                val ready = repository.getCourierReadyOrders()
                val all = repository.getAllOrders()
                deliveringOrders = all.filter { it.status == "delivering" }
                readyOrders = ready
                error = null
            } catch (e: Exception) { error = "Ошибка: ${e.message}" }
            finally { isLoading = false }
        }
    }

    fun takeOrder(orderId: Int) {
        viewModelScope.launch {
            isProcessing = true
            try {
                repository.startDelivery(orderId)
                loadOrders()
            } catch (e: Exception) { error = "Ошибка: ${e.message}" }
            finally { isProcessing = false }
        }
    }

    fun completeDelivery(orderId: Int) {
        viewModelScope.launch {
            isProcessing = true
            try {
                repository.completeDelivery(orderId)
                loadOrders()
            } catch (e: Exception) { error = "Ошибка: ${e.message}" }
            finally { isProcessing = false }
        }
    }
}

// ==================== Админ панель ====================

class AdminDashboardViewModel : ViewModel() {
    private val repository = PizzaRepository()
    var allOrders by mutableStateOf<List<Order>>(emptyList())
    var isLoading by mutableStateOf(false)
    var error by mutableStateOf<String?>(null)

    val activeOrders: List<Order> get() = allOrders.filter { it.status !in listOf("completed", "cancelled") }
        .sortedByDescending { it.created_at }
    val completedOrders: List<Order> get() = allOrders.filter { it.status in listOf("completed", "cancelled") }
        .sortedByDescending { it.created_at }
    val limitedActiveOrders: List<Order> get() = activeOrders.take(3)
    val limitedCompletedOrders: List<Order> get() = completedOrders.take(3)

    val todayRevenue: Double
        get() {
            val todayStart = java.time.LocalDate.now().atStartOfDay().toString()
            return allOrders.filter { it.created_at >= todayStart && it.status == "completed" }
                .sumOf { it.total_price }
        }

    val monthlyRevenue: Double
        get() {
            val monthStart = java.time.LocalDate.now().withDayOfMonth(1).atStartOfDay().toString()
            return allOrders.filter { it.created_at >= monthStart && it.status == "completed" }
                .sumOf { it.total_price }
        }

    val todayCount: Int
        get() {
            val todayStart = java.time.LocalDate.now().atStartOfDay().toString()
            return allOrders.count { it.created_at >= todayStart }
        }

    val statusCounts: Map<String, Int>
        get() = allOrders.groupingBy { it.status }.eachCount()

    init { loadOrders() }

    fun loadOrders() {
        viewModelScope.launch {
            isLoading = true
            try {
                allOrders = repository.getAllOrders()
                error = null
            } catch (e: Exception) { error = "Ошибка: ${e.message}" }
            finally { isLoading = false }
        }
    }
}

// ==================== АДМИН: ПРОДУКТЫ ====================

class AdminProductsViewModel : ViewModel() {
    private val repository = PizzaRepository()
    var products by mutableStateOf<List<Product>>(emptyList())
    var categories by mutableStateOf<List<Category>>(emptyList())
    var isLoading by mutableStateOf(false)
    var error by mutableStateOf<String?>(null)

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

    fun deleteProduct(productId: Int) {
        viewModelScope.launch {
            try {
                repository.deleteProduct(productId)
                loadData()
            } catch (e: Exception) { error = "Ошибка удаления: ${e.message}" }
        }
    }
}

class AdminEmployeesViewModel : ViewModel() {
    private val repository = PizzaRepository()
    var employees by mutableStateOf<List<Employee>>(emptyList())
    var isLoading by mutableStateOf(false)
    var error by mutableStateOf<String?>(null)

    init { loadEmployees() }

    fun loadEmployees() {
        viewModelScope.launch {
            isLoading = true
            try {
                employees = repository.getEmployees()
                error = null
            } catch (e: Exception) { error = "Ошибка: ${e.message}" }
            finally { isLoading = false }
        }
    }

    fun updateEmployeeRole(userId: Int, newRole: String) {
        viewModelScope.launch {
            try {
                repository.updateEmployee(userId, UpdateEmployeeRequest(role = newRole))
                loadEmployees()
            } catch (e: Exception) { error = "Ошибка: ${e.message}" }
        }
    }

    fun deleteEmployee(userId: Int) {
        viewModelScope.launch {
            try {
                repository.deleteEmployee(userId)
                loadEmployees()
            } catch (e: Exception) { error = "Ошибка удаления: ${e.message}" }
        }
    }
}
