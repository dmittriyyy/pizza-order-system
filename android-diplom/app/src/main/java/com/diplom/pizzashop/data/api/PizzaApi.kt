package com.diplom.pizzashop.data.api

import com.diplom.pizzashop.data.model.Category
import com.diplom.pizzashop.data.model.Product
import com.diplom.pizzashop.data.model.ProductsResponse
import retrofit2.Response
import retrofit2.http.GET
import retrofit2.http.Path
import retrofit2.http.Query

interface PizzaApi {

    // Products: Сервер возвращает объект { "products": [...], "total": N }
    @GET("api/products")
    suspend fun getProducts(
        @Query("skip") skip: Int = 0,
        @Query("limit") limit: Int = 50
    ): Response<ProductsResponse>

    // Categories: Сервер возвращает простой список [ {...}, {...} ]
    @GET("api/categories")
    suspend fun getCategories(): Response<List<Category>>

    @GET("api/products/{id}")
    suspend fun getProduct(@Path("id") id: Int): Response<Product>
}
