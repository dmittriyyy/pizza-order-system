package com.diplom.pizzashop.data.model

import android.os.Parcelable
import kotlinx.parcelize.Parcelize

// Модель товара
@Parcelize
data class Product(
    val id: Int,
    val name: String,
    val description: String,
    val price: Double,
    val category_id: Int,
    val image_url: String,
    val calories: Double?,
    val protein: Double?,
    val fat: Double?,
    val carbohydrates: Double?,
    val weight: Int?,
    val ingredients: List<String>?,
    val created_at: String?,
    val updated_at: String?
) : Parcelable

// Модель категории
@Parcelize
data class Category(
    val id: Int,
    val name: String,
    val slug: String
) : Parcelable

// Обертка для ответа сервера: { "products": [...], "total": N }
data class ProductsResponse(
    val products: List<Product>,
    val total: Int
)
