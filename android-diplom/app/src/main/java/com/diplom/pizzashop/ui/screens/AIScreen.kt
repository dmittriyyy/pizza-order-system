package com.diplom.pizzashop.ui.screens

import androidx.compose.foundation.*
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.*
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.lifecycle.viewmodel.compose.viewModel
import com.diplom.pizzashop.data.model.ChatMessage
import com.diplom.pizzashop.ui.theme.*
import com.diplom.pizzashop.ui.viewmodels.CartViewModel
import com.diplom.pizzashop.ui.viewmodels.ChatViewModel

@Composable
fun AIScreen(
    viewModel: ChatViewModel = viewModel(),
    cartViewModel: CartViewModel
) {
    var inputText by remember { mutableStateOf("") }
    val listState = rememberLazyListState()

    Column(modifier = Modifier.fillMaxSize()) {
        // Header
        Surface(color = OrangeAccent, modifier = Modifier.padding(bottom = 1.dp)) {
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(16.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                Icon(Icons.Default.SmartToy, contentDescription = null, tint = Color.White, modifier = Modifier.size(32.dp))
                Spacer(Modifier.width(12.dp))
                Column {
                    Text("WOKI AI", color = Color.White, fontWeight = FontWeight.Bold, fontSize = 18.sp)
                    Text("Онлайн • Отвечает быстро", color = Color.White.copy(0.8f), fontSize = 12.sp)
                }
            }
        }

        // Messages List
        LazyColumn(
            state = listState,
            modifier = Modifier
                .weight(1f)
                .padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            items(viewModel.messages) { msg ->
                MessageBubble(msg)
            }
            if (viewModel.isTyping) {
                item {
                    Surface(
                        color = GlassSurface,
                        shape = RoundedCornerShape(20.dp, 20.dp, 20.dp, 4.dp)
                    ) {
                        Row(modifier = Modifier.padding(12.dp), horizontalArrangement = Arrangement.spacedBy(4.dp)) {
                            repeat(3) { Box(Modifier.size(8.dp).background(OrangeAccent.copy(0.5f), CircleShape)) }
                        }
                    }
                }
            }
        }

        // Input Field
        Surface(color = GlassSurface, modifier = Modifier.padding(16.dp), shape = RoundedCornerShape(30.dp)) {
            Row(modifier = Modifier.padding(8.dp), verticalAlignment = Alignment.CenterVertically) {
                TextField(
                    value = inputText,
                    onValueChange = { inputText = it },
                    placeholder = { Text("Спросите о пицце...", color = TextSecondary) },
                    colors = TextFieldDefaults.colors(
                        focusedContainerColor = Color.Transparent,
                        unfocusedContainerColor = Color.Transparent,
                        focusedIndicatorColor = Color.Transparent,
                        unfocusedIndicatorColor = Color.Transparent
                    ),
                    modifier = Modifier.weight(1f)
                )
                IconButton(onClick = {
                    if (inputText.isNotBlank()) {
                        viewModel.sendMessage(inputText) {
                            cartViewModel.loadCart()
                        }
                        inputText = ""
                    }
                }) {
                    Icon(Icons.Default.Send, contentDescription = "Send", tint = OrangeAccent)
                }
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
        Surface(
            color = if (isUser) OrangeAccent else GlassSurface,
            shape = RoundedCornerShape(
                topStart = 20.dp, topEnd = 20.dp,
                bottomStart = if (isUser) 20.dp else 4.dp,
                bottomEnd = if (isUser) 4.dp else 20.dp
            ),
            modifier = Modifier.widthIn(max = 260.dp)
        ) {
            Text(
                text = msg.content,
                color = Color.White,
                fontSize = 14.sp,
                modifier = Modifier.padding(12.dp)
            )
        }
    }
}
