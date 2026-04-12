package com.diplom.pizzashop.data.api

import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import retrofit2.http.Body
import retrofit2.http.POST

data class ChatRequest(val message: String, val session_id: String)
data class ChatResponse(val message: String, val response: String, val timestamp: String)

interface ChatApi {
    @POST("api/chat/send")
    suspend fun sendMessage(@Body request: ChatRequest): ChatResponse
}

object ChatApiService {
    private val retrofit = Retrofit.Builder()
        .baseUrl("http://10.0.2.2:8000/")
        .addConverterFactory(GsonConverterFactory.create())
        .build()

    private val api = retrofit.create(ChatApi::class.java)

    suspend fun sendMessage(message: String, sessionId: String): String {
        val response = api.sendMessage(ChatRequest(message, sessionId))
        return response.response
    }
}
