package com.diplom.pizzashop.ui.screens

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.*
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.diplom.pizzashop.data.model.Order
import com.diplom.pizzashop.ui.theme.*

@Composable
fun OrderSummaryCard(order: Order) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(16.dp),
        colors = CardDefaults.cardColors(containerColor = DarkCardBackground)
    ) {
        Row(
            modifier = Modifier.padding(12.dp).fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Column {
                Text("Заказ #${order.id}", color = TextWhite, fontWeight = FontWeight.Bold)
                Text("${order.total_price.toInt()} ₽", color = OrangeAccent, fontSize = 14.sp)
            }
            AdminStatusBadge(order.status)
        }
    }
}

@Composable
fun AdminStatusBadge(status: String) {
    val (text, color) = when (status) {
        "created" -> "Новый" to Color.Blue.copy(0.7f)
        "paid" -> "Оплачен" to Color.Blue.copy(0.7f)
        "cooking" -> "Готовится" to Color.Yellow.copy(0.7f)
        "ready" -> "Готов" to Color.Green.copy(0.7f)
        "delivering" -> "В доставке" to Purple.copy(0.7f)
        "completed" -> "Выполнен" to Color.Gray
        else -> status to Color.Gray
    }
    Surface(
        color = color.copy(alpha = 0.2f),
        shape = RoundedCornerShape(8.dp)
    ) {
        Text(text, color = color, fontSize = 11.sp, fontWeight = FontWeight.Bold, modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp))
    }
}
