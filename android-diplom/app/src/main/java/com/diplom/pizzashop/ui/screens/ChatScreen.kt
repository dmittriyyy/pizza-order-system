package com.diplom.pizzashop.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.lazy.rememberLazyListState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.BasicTextField
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Close
import androidx.compose.material.icons.filled.Send
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.diplom.pizzashop.data.api.ChatApiService
import java.util.UUID
import kotlinx.coroutines.launch

data class ChatMessage(
    val role: String, // "user" or "assistant"
    val content: String
)

@Composable
fun ChatScreen(
    onBack: () -> Unit,
    orangeAccent: Color = Color(0xFFFF6B00),
    surfaceDark: Color = Color(0xFF1A1A2E),
    textWhite: Color = Color(0xFFFFFFFF),
    textSecondary: Color = Color(0xFF8899AA)
) {
    val scope = rememberCoroutineScope()
    val listState = rememberLazyListState()
    val apiService = ChatApiService

    var messages by remember {
        mutableStateOf(
            listOf(
                ChatMessage("assistant", "Привет! Я WOKI 🍕 Спрашивай о меню!")
            )
        )
    }
    var inputText by remember { mutableStateOf("") }
    var isTyping by remember { mutableStateOf(false) }
    val sessionId = remember { "android_${UUID.randomUUID()}" }

    // Автоскролл вниз
    LaunchedEffect(messages.size) {
        if (messages.isNotEmpty()) {
            listState.animateScrollToItem(messages.size - 1)
        }
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(Color(0xFF0F0F1A))
    ) {
        // Header
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .background(
                    Brush.horizontalGradient(
                        colors = listOf(orangeAccent, Color(0xFFD14D07))
                    )
                )
                .padding(16.dp),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Box(
                    modifier = Modifier
                        .size(40.dp)
                        .background(Color.White.copy(0.2f), CircleShape),
                    contentAlignment = Alignment.Center
                ) {
                    Text("🤖", fontSize = 20.sp)
                }
                Spacer(Modifier.width(12.dp))
                Column {
                    Text("WOKI", color = textWhite, fontWeight = FontWeight.Bold, fontSize = 16.sp)
                    Text("Онлайн", color = textWhite.copy(0.7f), fontSize = 11.sp)
                }
            }
            IconButton(onClick = onBack) {
                Icon(Icons.Default.Close, contentDescription = "Закрыть", tint = textWhite)
            }
        }

        // Сообщения
        LazyColumn(
            state = listState,
            modifier = Modifier
                .weight(1f)
                .padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            items(messages) { msg ->
                MessageBubble(msg = msg)
            }
            if (isTyping) {
                item {
                    Box(
                        modifier = Modifier
                            .background(surfaceDark, RoundedCornerShape(20.dp, 20.dp, 20.dp, 4.dp))
                            .padding(12.dp)
                    ) {
                        Row(horizontalArrangement = Arrangement.spacedBy(4.dp)) {
                            repeat(3) { i ->
                                Box(
                                    modifier = Modifier
                                        .size(8.dp)
                                        .background(orangeAccent.copy(0.5f), CircleShape)
                                )
                            }
                        }
                    }
                }
            }
        }

        // Поле ввода
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            horizontalArrangement = Arrangement.spacedBy(12.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            BasicTextField(
                value = inputText,
                onValueChange = { inputText = it },
                modifier = Modifier
                    .weight(1f)
                    .background(surfaceDark, RoundedCornerShape(24.dp))
                    .padding(16.dp),
                textStyle = LocalTextStyle.current.copy(color = textWhite),
                decorationBox = { innerTextField ->
                    if (inputText.isEmpty()) {
                        Text("Спросите о пицце...", color = textSecondary.copy(0.5f))
                    }
                    innerTextField()
                }
            )
            Button(
                onClick = {
                    if (inputText.isBlank()) return@Button
                    val userMsg = inputText
                    inputText = ""
                    messages = messages + ChatMessage("user", userMsg)
                    isTyping = true

                    scope.launch {
                        try {
                            val response = apiService.sendMessage(userMsg, sessionId)
                            messages = messages + ChatMessage("assistant", response)
                        } catch (e: Exception) {
                            messages = messages + ChatMessage(
                                "assistant",
                                "Извините, сейчас я немного занят 🍕 Попробуй через минуту!"
                            )
                        } finally {
                            isTyping = false
                        }
                    }
                },
                colors = ButtonDefaults.buttonColors(containerColor = orangeAccent),
                shape = RoundedCornerShape(24.dp),
                enabled = !isTyping
            ) {
                Icon(Icons.Default.Send, contentDescription = "Отправить", tint = Color.White)
            }
        }
    }
}

@Composable
fun MessageBubble(msg: ChatMessage) {
    val isUser = msg.role == "user"
    Row(
        modifier = Modifier.fillMaxWidth(),
        horizontalArrangement = if (isUser) Arrangement.End else Arrangement.Start
    ) {
        val shape = RoundedCornerShape(
            topStart = 20.dp,
            topEnd = 20.dp,
            bottomStart = if (isUser) 20.dp else 4.dp,
            bottomEnd = if (isUser) 4.dp else 20.dp
        )
        Box(
            modifier = Modifier
                .background(
                    if (isUser) Color(0xFFFF6B00) else Color(0xFF1A1A2E),
                    shape
                )
                .padding(12.dp)
                .widthIn(max = 260.dp)
        ) {
            Text(
                text = msg.content,
                color = Color.White,
                fontSize = 14.sp,
                lineHeight = 20.sp
            )
        }
    }
}
