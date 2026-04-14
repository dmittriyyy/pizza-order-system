package com.diplom.pizzashop.data.model

import android.os.Parcelable
import kotlinx.parcelize.Parcelize

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

@Parcelize
data class Category(
    val id: Int,
    val name: String,
    val slug: String
) : Parcelable

data class ProductsResponse(
    val products: List<Product>,
    val total: Int
)

data class CategoriesResponse(
    val categories: List<Category>,
    val total: Int
)

@Parcelize
data class CartItem(
    val product_id: Int,
    val name: String,
    val price: Double,
    val quantity: Int,
    val image_url: String?,
    val subtotal: Double = price * quantity
) : Parcelable

data class CartResponse(
    val items: List<CartItem>,
    val total: Double
)

data class AddToCartRequest(
    val product_id: Int,
    val quantity: Int = 1
)

@Parcelize
data class ChatMessage(
    val role: String,
    val content: String
) : Parcelable