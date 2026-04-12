package com.diplom.pizzashop.data.repository

import com.diplom.pizzashop.data.api.NetworkModule
import com.diplom.pizzashop.data.model.Category
import com.diplom.pizzashop.data.model.Product

class PizzaRepository {
    private val api = NetworkModule.pizzaApi

    suspend fun getProducts(): List<Product> {
        val response = api.getProducts()
        // Сервер возвращает { "products": [...] }, достаем список из поля products
        return if (response.isSuccessful) response.body()?.products ?: emptyList() else emptyList()
    }

    suspend fun getCategories(): List<Category> {
        val response = api.getCategories()
        // Сервер возвращает просто список [...], берем его напрямую
        return if (response.isSuccessful) response.body() ?: emptyList() else emptyList()
    }

    suspend fun getProduct(id: Int): Product? {
        val response = api.getProduct(id)
        return if (response.isSuccessful) response.body() else null
    }
}
