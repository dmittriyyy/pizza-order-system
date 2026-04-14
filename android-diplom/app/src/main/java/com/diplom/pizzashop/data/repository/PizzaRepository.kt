package com.diplom.pizzashop.data.repository

import com.diplom.pizzashop.data.api.*
import com.diplom.pizzashop.data.model.*

class PizzaRepository {
    private val api = RetrofitClient.api

    suspend fun getProducts(): List<Product> {
        val response = api.getProducts()
        return if (response.isSuccessful) response.body()?.products ?: emptyList() else emptyList()
    }

    suspend fun getCategories(): List<Category> {
        // Исправлено: парсим список напрямую
        val response = api.getCategories()
        return if (response.isSuccessful) response.body() ?: emptyList() else emptyList()
    }

    suspend fun getCart(): List<CartItem> {
        val response = api.getCart()
        return if (response.isSuccessful) response.body()?.items ?: emptyList() else emptyList()
    }

    suspend fun addToCart(productId: Int): List<CartItem> {
        val response = api.addToCart(AddToCartRequest(productId))
        return if (response.isSuccessful) response.body()?.items ?: emptyList() else emptyList()
    }

    suspend fun clearCart(): Boolean {
        val response = api.clearCart()
        return response.isSuccessful
    }

    suspend fun sendChatMessage(message: String, sessionId: String): String? {
        val response = api.sendChatMessage(ChatRequest(message, sessionId))
        return if (response.isSuccessful) response.body()?.response else null
    }
}