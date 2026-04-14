package com.diplom.pizzashop.ui.screens

import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.*
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.diplom.pizzashop.ui.theme.*

@Composable
fun KitchenScreen() {
    Box(modifier = Modifier.fillMaxSize().padding(24.dp), contentAlignment = Alignment.Center) {
        Text("👨‍ Кухня\nЗаказы на приготовление", color = TextWhite, fontSize = 24.sp, fontWeight = FontWeight.Bold)
    }
}

@Composable
fun DeliveryScreen() {
    Box(modifier = Modifier.fillMaxSize().padding(24.dp), contentAlignment = Alignment.Center) {
        Text("🚚 Доставка\nАктивные заказы", color = TextWhite, fontSize = 24.sp, fontWeight = FontWeight.Bold)
    }
}