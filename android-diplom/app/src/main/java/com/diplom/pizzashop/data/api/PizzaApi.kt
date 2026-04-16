package com.diplom.pizzashop.data.api

import com.diplom.pizzashop.data.model.*
import retrofit2.Response
import retrofit2.http.*

interface PizzaApi {

    // ==================== ТОВАРЫ И КАТЕГОРИИ ====================

    @GET("api/products")
    suspend fun getProducts(
        @Query("skip") skip: Int = 0,
        @Query("limit") limit: Int = 50
    ): Response<ProductsResponse>

    @GET("api/categories")
    suspend fun getCategories(): Response<List<Category>>

    // ==================== КОРЗИНА ====================

    @GET("api/cart")
    suspend fun getCart(): Response<CartResponse>

    @POST("api/cart/add")
    suspend fun addToCart(@Body request: AddToCartRequest): Response<CartResponse>

    @PUT("api/cart/update/{product_id}")
    suspend fun updateCartItem(
        @Path("product_id") productId: Int,
        @Body request: AddToCartRequest
    ): Response<CartResponse>

    @DELETE("api/cart/remove/{product_id}")
    suspend fun removeCartItem(@Path("product_id") productId: Int): Response<CartResponse>

    @DELETE("api/cart/clear")
    suspend fun clearCart(): Response<Unit>

    // ==================== ЗАКАЗЫ ====================

    @POST("api/orders")
    suspend fun createOrder(@Body request: CreateOrderRequest): Response<Order>

    @GET("api/orders")
    suspend fun getUserOrders(
        @Query("skip") skip: Int = 0,
        @Query("limit") limit: Int = 50
    ): Response<List<Order>>

    @GET("api/orders/cook/pending")
    suspend fun getCookOrders(): Response<List<Order>>

    @PATCH("api/orders/{orderId}/status/start-cooking")
    suspend fun startCooking(@Path("orderId") orderId: Int): Response<Order>

    @PATCH("api/orders/{orderId}/status/ready")
    suspend fun markReady(@Path("orderId") orderId: Int): Response<Order>

    @GET("api/orders/courier/ready")
    suspend fun getCourierReadyOrders(): Response<List<Order>>

    @GET("api/orders/admin/all")
    suspend fun getAllOrders(
        @Query("skip") skip: Int = 0,
        @Query("limit") limit: Int = 200
    ): Response<List<Order>>

    @PATCH("api/orders/{orderId}/status/delivering")
    suspend fun startDelivery(@Path("orderId") orderId: Int): Response<Order>

    @PATCH("api/orders/{orderId}/status/completed")
    suspend fun completeDelivery(@Path("orderId") orderId: Int): Response<Order>

    // ==================== ЧАТ ====================

    @POST("api/chat/send")
    suspend fun sendChatMessage(@Body request: ChatRequest): Response<ChatResponse>

    // ==================== AUTH & PROFILE ====================

    data class LoginRequest(val login: String, val password: String)
    data class LoginResponse(val access_token: String, val token_type: String)
    data class ProfileResponse(
        val id: Int,
        val role: String?,
        val login: String?,
        val email: String? = null,
        val first_name: String? = null,
        val last_name: String? = null,
        val phone: String? = null,
        val telegram: String? = null,
        val default_address: String? = null
    )

    data class UpdateProfileRequest(
        val email: String? = null,
        val first_name: String? = null,
        val last_name: String? = null,
        val phone: String? = null,
        val telegram: String? = null,
        val default_address: String? = null
    )

    @POST("api/auth/login")
    suspend fun login(@Body request: LoginRequest): LoginResponse

    @GET("api/auth/me")
    suspend fun getProfile(): ProfileResponse

    @PATCH("api/profile/me")
    suspend fun updateProfile(@Body request: UpdateProfileRequest): ProfileResponse

    // ==================== АДМИН: ТОВАРЫ ====================

    @POST("api/products")
    suspend fun createProduct(@Body request: CreateProductRequest): Response<Product>

    @PATCH("api/products/{productId}")
    suspend fun updateProduct(
        @Path("productId") productId: Int,
        @Body request: UpdateProductRequest
    ): Response<Product>

    @DELETE("api/products/{productId}")
    suspend fun deleteProduct(@Path("productId") productId: Int): Response<Unit>

    // ==================== АДМИН: СОТРУДНИКИ ====================

    @GET("api/admin/employees")
    suspend fun getEmployees(): Response<List<Employee>>

    @POST("api/admin/employees")
    suspend fun createEmployee(@Body request: CreateEmployeeRequest): Response<Employee>

    @PATCH("api/admin/employees/{employeeId}")
    suspend fun updateEmployee(
        @Path("employeeId") employeeId: Int,
        @Body request: UpdateEmployeeRequest
    ): Response<Employee>

    @DELETE("api/admin/employees/{employeeId}")
    suspend fun deleteEmployee(@Path("employeeId") employeeId: Int): Response<Unit>
}

// ==================== DTO ====================

data class ChatRequest(val message: String, val session_id: String)
data class ChatResponse(val message: String, val response: String, val timestamp: String)

data class CreateOrderRequest(
    val delivery_address: String,
    val delivery_comment: String? = null,
    val delivery_time: String? = null,
    val customer_phone: String? = null,
    val customer_name: String? = null,
    val payment_method: String = "cash_on_delivery",
    val order_comment: String? = null
)

data class CreateProductRequest(
    val name: String,
    val description: String,
    val slug: String,
    val price: Double,
    val category_id: Int,
    val image_url: String? = null,
    val calories: Int = 0,
    val protein: Double = 0.0,
    val fat: Double = 0.0,
    val carbohydrates: Double = 0.0,
    val weight: Int = 0,
    val ingredients: List<String> = emptyList()
)

data class UpdateProductRequest(
    val name: String? = null,
    val description: String? = null,
    val price: Double? = null,
    val category_id: Int? = null,
    val image_url: String? = null,
    val calories: Int? = null,
    val protein: Double? = null,
    val fat: Double? = null,
    val carbohydrates: Double? = null,
    val weight: Int? = null,
    val ingredients: List<String>? = null,
    val is_available: Boolean? = null,
    val discount: Double? = null
)

data class UpdateEmployeeRequest(
    val role: String? = null,
    val status: String? = null,
    val first_name: String? = null,
    val last_name: String? = null,
    val email: String? = null,
    val phone: String? = null,
    val telegram: String? = null
)