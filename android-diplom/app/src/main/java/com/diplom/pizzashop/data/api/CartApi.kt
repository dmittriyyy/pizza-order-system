package com.diplom.pizzashop.data.api

import com.diplom.pizzashop.data.model.AddToCartRequest
import com.diplom.pizzashop.data.model.CartResponse
import retrofit2.Response
import retrofit2.http.Body
import retrofit2.http.DELETE
import retrofit2.http.GET
import retrofit2.http.POST

interface CartApi {
    @GET("api/cart")
    suspend fun getCart(): Response<CartResponse>

    @POST("api/cart/add")
    suspend fun addToCart(@Body request: AddToCartRequest): Response<CartResponse>

    @DELETE("api/cart/clear")
    suspend fun clearCart(): Response<Unit>
}
