package com.diplom.pizzashop.data.api

import com.diplom.pizzashop.data.model.*
import retrofit2.Response
import retrofit2.http.*

interface PizzaApi {

    @GET("api/products")
    suspend fun getProducts(
        @Query("skip") skip: Int = 0,
        @Query("limit") limit: Int = 50
    ): Response<ProductsResponse>

    @GET("api/categories")
    suspend fun getCategories(): Response<List<Category>>

    @GET("api/cart")
    suspend fun getCart(): Response<CartResponse>

    @POST("api/cart/add")
    suspend fun addToCart(@Body request: AddToCartRequest): Response<CartResponse>

    @DELETE("api/cart/clear")
    suspend fun clearCart(): Response<Unit>

    @POST("api/chat/send")
    suspend fun sendChatMessage(@Body request: ChatRequest): Response<ChatResponse>

    // --- AUTH & PROFILE ---
    data class LoginRequest(val login: String, val password: String)
    data class LoginResponse(val access_token: String, val token_type: String)
    data class ProfileResponse(val id: Int, val role: String?, val login: String?)

    @POST("api/auth/login")
    suspend fun login(@Body request: LoginRequest): LoginResponse

    @GET("api/auth/me")
    suspend fun getProfile(): ProfileResponse
}

data class ChatRequest(val message: String, val session_id: String)
data class ChatResponse(val message: String, val response: String, val timestamp: String)