package com.diplom.pizzashop.data.repository

import com.diplom.pizzashop.data.api.*
import com.diplom.pizzashop.data.model.*

class PizzaRepository {
    private val api = RetrofitClient.api

    // ==================== ТОВАРЫ И КАТЕГОРИИ ====================

    suspend fun getProducts(): List<Product> {
        val response = api.getProducts()
        return if (response.isSuccessful) response.body()?.products ?: emptyList() else emptyList()
    }

    suspend fun getCategories(): List<Category> {
        val response = api.getCategories()
        return if (response.isSuccessful) response.body() ?: emptyList() else emptyList()
    }

    suspend fun createProduct(request: CreateProductRequest): Product {
        val response = api.createProduct(request)
        if (response.isSuccessful && response.body() != null) return response.body()!!
        throw Exception("Ошибка создания товара: ${response.errorBody()?.string()}")
    }

    suspend fun updateProduct(id: Int, request: UpdateProductRequest): Product {
        val response = api.updateProduct(id, request)
        if (response.isSuccessful && response.body() != null) return response.body()!!
        throw Exception("Ошибка обновления: ${response.errorBody()?.string()}")
    }

    suspend fun deleteProduct(id: Int) {
        val response = api.deleteProduct(id)
        if (!response.isSuccessful) throw Exception("Ошибка удаления: ${response.errorBody()?.string()}")
    }

    // ==================== КОРЗИНА ====================

    suspend fun getCart(): List<CartItem> {
        val response = api.getCart()
        return if (response.isSuccessful) response.body()?.items ?: emptyList() else emptyList()
    }

    suspend fun addToCart(productId: Int, quantity: Int = 1): List<CartItem> {
        val response = api.addToCart(AddToCartRequest(productId, quantity))
        return if (response.isSuccessful) response.body()?.items ?: emptyList() else emptyList()
    }

    suspend fun updateCartItem(productId: Int, quantity: Int): List<CartItem> {
        val response = api.updateCartItem(productId, AddToCartRequest(productId, quantity))
        return if (response.isSuccessful) response.body()?.items ?: emptyList() else emptyList()
    }

    suspend fun removeCartItem(productId: Int): List<CartItem> {
        val response = api.removeCartItem(productId)
        return if (response.isSuccessful) response.body()?.items ?: emptyList() else emptyList()
    }

    suspend fun clearCart(): Boolean {
        val response = api.clearCart()
        return response.isSuccessful
    }

    // ==================== ЗАКАЗЫ ====================

    suspend fun createOrder(request: CreateOrderRequest): Order {
        val response = api.createOrder(request)
        if (response.isSuccessful && response.body() != null) return response.body()!!
        throw Exception("Ошибка создания заказа: ${response.errorBody()?.string()}")
    }

    suspend fun getUserOrders(): List<Order> {
        val response = api.getUserOrders()
        return if (response.isSuccessful) response.body() ?: emptyList() else emptyList()
    }

    suspend fun getCookOrders(): List<Order> {
        val response = api.getCookOrders()
        return if (response.isSuccessful) response.body() ?: emptyList() else emptyList()
    }

    suspend fun startCooking(orderId: Int): Order {
        val response = api.startCooking(orderId)
        if (response.isSuccessful && response.body() != null) return response.body()!!
        throw Exception("Ошибка: ${response.errorBody()?.string()}")
    }

    suspend fun markReady(orderId: Int): Order {
        val response = api.markReady(orderId)
        if (response.isSuccessful && response.body() != null) return response.body()!!
        throw Exception("Ошибка: ${response.errorBody()?.string()}")
    }

    suspend fun getCourierReadyOrders(): List<Order> {
        val response = api.getCourierReadyOrders()
        return if (response.isSuccessful) response.body() ?: emptyList() else emptyList()
    }

    suspend fun getAllOrders(): List<Order> {
        val response = api.getAllOrders()
        return if (response.isSuccessful) response.body() ?: emptyList() else emptyList()
    }

    suspend fun startDelivery(orderId: Int): Order {
        val response = api.startDelivery(orderId)
        if (response.isSuccessful && response.body() != null) return response.body()!!
        throw Exception("Ошибка: ${response.errorBody()?.string()}")
    }

    suspend fun completeDelivery(orderId: Int): Order {
        val response = api.completeDelivery(orderId)
        if (response.isSuccessful && response.body() != null) return response.body()!!
        throw Exception("Ошибка: ${response.errorBody()?.string()}")
    }

    // ==================== ЧАТ ====================

    suspend fun sendChatMessage(message: String, sessionId: String): Result<String> {
        return try {
            val response = api.sendChatMessage(ChatRequest(message, sessionId))
            if (response.isSuccessful) {
                val body = response.body()
                if (body != null) {
                    Result.success(body.response)
                } else {
                    Result.failure(Exception("Пустой ответ от сервера"))
                }
            } else {
                val errorBody = response.errorBody()?.string()
                Result.failure(Exception("Ошибка ${response.code()}: $errorBody"))
            }
        } catch (e: java.net.SocketTimeoutException) {
            Result.failure(Exception("WOKI думает слишком долго... Попробуй ещё раз"))
        } catch (e: java.net.ConnectException) {
            Result.failure(Exception("Нет соединения с сервером"))
        } catch (e: Exception) {
            Result.failure(Exception("Ошибка: ${e.message}"))
        }
    }

    // ==================== СОТРУДНИКИ ====================

    suspend fun getEmployees(): List<Employee> {
        val response = api.getEmployees()
        return if (response.isSuccessful) response.body() ?: emptyList() else emptyList()
    }

    suspend fun createEmployee(request: CreateEmployeeRequest): Employee {
        val response = api.createEmployee(request)
        if (response.isSuccessful && response.body() != null) return response.body()!!
        throw Exception("Ошибка создания сотрудника: ${response.errorBody()?.string()}")
    }

    suspend fun updateEmployee(id: Int, request: UpdateEmployeeRequest): Employee {
        val response = api.updateEmployee(id, request)
        if (response.isSuccessful && response.body() != null) return response.body()!!
        throw Exception("Ошибка обновления: ${response.errorBody()?.string()}")
    }

    suspend fun deleteEmployee(id: Int) {
        val response = api.deleteEmployee(id)
        if (!response.isSuccessful) throw Exception("Ошибка удаления: ${response.errorBody()?.string()}")
    }
}