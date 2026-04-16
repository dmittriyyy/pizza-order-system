package com.diplom.pizzashop.data.model

import android.os.Parcelable
import kotlinx.parcelize.Parcelize
import kotlinx.parcelize.RawValue

@Parcelize
data class Product(
    val id: Int,
    val name: String,
    val description: String,
    val price: Double,
    val category_id: Int,
    val image_url: String?,
    val calories: Int?,
    val protein: Double?,
    val fat: Double?,
    val carbohydrates: Double?,
    val weight: Int?,
    val ingredients: @RawValue List<String>?,
    val created_at: String?,
    val updated_at: String?,
    val is_available: Boolean = true,
    val discount: Double = 0.0,
    val category: @RawValue CategoryResponse? = null
) : Parcelable

@Parcelize
data class Category(
    val id: Int,
    val name: String,
    val slug: String
) : Parcelable

data class CategoryResponse(
    val id: Int,
    val name: String,
    val slug: String
)

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
    val comment: String? = null,
    val subtotal: Double = price * quantity
) : Parcelable

data class CartResponse(
    val items: List<CartItem>,
    val total: Double,
    val items_count: Int = 0
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

// ==================== ЗАКАЗЫ ====================

@Parcelize
data class OrderItem(
    val id: Int = 0,
    val order_id: Int = 0,
    val product_id: Int = 0,
    val quantity: Int = 1,
    val price_at_time_of_order: Double = 0.0,
    val comment: String? = null,
    val special_requests: String? = null,
    val product: OrderProduct? = null
) : Parcelable

@Parcelize
data class OrderProduct(
    val id: Int,
    val name: String,
    val price: Double,
    val image_url: String? = null
) : Parcelable

@Parcelize
data class Order(
    val id: Int,
    val user_id: Int,
    val status: String,
    val total_price: Double,
    val delivery_address: String,
    val delivery_comment: String? = null,
    val delivery_time: String? = null,
    val delivery_lat: Double? = null,
    val delivery_lng: Double? = null,
    val picked_up_at: String? = null,
    val customer_phone: String? = null,
    val customer_name: String? = null,
    val payment_method: String,
    val order_comment: String? = null,
    val created_at: String,
    val updated_at: String? = null,
    val items: List<OrderItem> = emptyList()
) : Parcelable

// ==================== СОТРУДНИКИ ====================

@Parcelize
data class Employee(
    val id: Int,
    val first_name: String?,
    val last_name: String?,
    val login: String,
    val email: String?,
    val phone: String?,
    val telegram: String?,
    val role: String,
    val status: String = "active",
    val registered_at: String? = null
) : Parcelable

data class CreateEmployeeRequest(
    val login: String,
    val email: String? = null,
    val first_name: String? = null,
    val last_name: String? = null,
    val role: String = "client",
    val phone: String? = null,
    val telegram: String? = null
)
