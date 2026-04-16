package com.diplom.pizzashop.ui.screens

import androidx.compose.foundation.*
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.*
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.lifecycle.viewmodel.compose.viewModel
import com.diplom.pizzashop.data.model.Order
import com.diplom.pizzashop.ui.theme.*
import com.diplom.pizzashop.ui.viewmodels.KitchenViewModel

@Composable
fun KitchenScreen(viewModel: KitchenViewModel = viewModel()) {
    Column(
        modifier = Modifier.fillMaxSize(),
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        // Header
        Surface(color = GlassSurface, modifier = Modifier.padding(bottom = 1.dp)) {
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(16.dp),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Column {
                    Text("👨‍🍳 Кухня", color = TextWhite, fontWeight = FontWeight.Bold, fontSize = 20.sp)
                    Text("Заказы на приготовление", color = TextSecondary, fontSize = 12.sp)
                }
                if (viewModel.orders.isNotEmpty()) {
                    Surface(
                        color = OrangeAccent.copy(0.2f),
                        shape = RoundedCornerShape(12.dp)
                    ) {
                        Text(
                            "${viewModel.orders.size} в работе",
                            color = OrangeAccent,
                            fontSize = 12.sp,
                            fontWeight = FontWeight.Bold,
                            modifier = Modifier.padding(horizontal = 12.dp, vertical = 6.dp)
                        )
                    }
                }
            }
        }

        // Content
        when {
            viewModel.isLoading -> {
                Box(Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                    CircularProgressIndicator(color = OrangeAccent)
                }
            }
            viewModel.orders.isEmpty() -> {
                Box(Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                    Column(horizontalAlignment = Alignment.CenterHorizontally) {
                        Text("🍳", fontSize = 48.sp)
                        Text("Нет активных заказов", color = TextWhite, fontSize = 18.sp, modifier = Modifier.padding(top = 16.dp))
                        Text("Все заказы приготовлены!", color = TextSecondary, fontSize = 14.sp)
                    }
                }
            }
            else -> {
                LazyColumn(
                    modifier = Modifier.fillMaxSize(),
                    contentPadding = PaddingValues(16.dp),
                    verticalArrangement = Arrangement.spacedBy(12.dp)
                ) {
                    items(viewModel.orders, key = { it.id }) { order ->
                        OrderCard(order, viewModel)
                    }
                }
            }
        }
    }
}

@Composable
fun OrderCard(order: Order, viewModel: KitchenViewModel) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(20.dp),
        colors = CardDefaults.cardColors(containerColor = GlassSurface)
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            // Header: Order ID + Status
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text("Заказ #${order.id}", color = TextWhite, fontWeight = FontWeight.Bold, fontSize = 18.sp)
                StatusBadge(order.status)
            }

            Spacer(Modifier.height(12.dp))

            // Items
            Surface(
                color = DarkCardBackground,
                shape = RoundedCornerShape(12.dp),
                modifier = Modifier.fillMaxWidth()
            ) {
                Column(modifier = Modifier.padding(12.dp)) {
                    Text("Состав заказа:", color = TextSecondary, fontSize = 12.sp, fontWeight = FontWeight.Bold)
                    Spacer(Modifier.height(8.dp))
                    order.items.forEach { item ->
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween
                        ) {
                            Column {
                                Text(item.product?.name ?: "Товар", color = TextWhite, fontSize = 14.sp)
                                if (item.comment != null || item.special_requests != null) {
                                    Text(
                                        "⚠️ ${item.comment ?: item.special_requests}",
                                        color = Color.Yellow.copy(0.8f),
                                        fontSize = 11.sp
                                    )
                                }
                            }
                            Text("× ${item.quantity}", color = TextSecondary, fontSize = 14.sp)
                        }
                        if (item != order.items.last()) {
                            HorizontalDivider(color = TextSecondary.copy(0.1f), modifier = Modifier.padding(vertical = 6.dp))
                        }
                    }
                }
            }

            // Order comment
            if (order.order_comment != null) {
                Spacer(Modifier.height(8.dp))
                Surface(
                    color = Color.Yellow.copy(alpha = 0.1f),
                    shape = RoundedCornerShape(12.dp),
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Row(modifier = Modifier.padding(12.dp)) {
                        Text("📝 ${order.order_comment}", color = Color.Yellow.copy(0.9f), fontSize = 13.sp)
                    }
                }
            }

            Spacer(Modifier.height(12.dp))

            // Total & Actions
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text("Сумма: ${order.total_price.toInt()} ₽", color = TextSecondary, fontSize = 14.sp)
            }

            Spacer(Modifier.height(12.dp))

            // Action buttons
            when (order.status) {
                "created", "paid" -> {
                    Button(
                        onClick = { viewModel.startCooking(order.id) },
                        enabled = !viewModel.isProcessing,
                        colors = ButtonDefaults.buttonColors(containerColor = OrangeAccent),
                        shape = RoundedCornerShape(16.dp),
                        modifier = Modifier.fillMaxWidth().height(48.dp)
                    ) {
                        Text(if (viewModel.isProcessing) "..." else "🔥 Начать приготовление", fontSize = 16.sp)
                    }
                }
                "cooking" -> {
                    Button(
                        onClick = { viewModel.markReady(order.id) },
                        enabled = !viewModel.isProcessing,
                        colors = ButtonDefaults.buttonColors(containerColor = Color.Green.copy(0.7f)),
                        shape = RoundedCornerShape(16.dp),
                        modifier = Modifier.fillMaxWidth().height(48.dp)
                    ) {
                        Text(if (viewModel.isProcessing) "..." else "✅ Готов к выдаче", fontSize = 16.sp)
                    }
                }
                "ready" -> {
                    Surface(
                        color = Color.Green.copy(alpha = 0.15f),
                        shape = RoundedCornerShape(12.dp),
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        Text(
                            "✓ Готов",
                            color = Color.Green.copy(0.8f),
                            fontSize = 16.sp,
                            fontWeight = FontWeight.Bold,
                            modifier = Modifier.padding(vertical = 12.dp).align(Alignment.CenterHorizontally)
                        )
                    }
                }
            }
        }
    }
}

@Composable
fun StatusBadge(status: String) {
    val (color, text) = when (status) {
        "created" -> Color.Blue to "Новый"
        "paid" -> Color.Blue to "Оплачен"
        "cooking" -> Color.Yellow.copy(0.8f) to "Готовится"
        "ready" -> Color.Green.copy(0.7f) to "Готов"
        else -> Color.Gray to status
    }
    Surface(
        color = color.copy(alpha = 0.2f),
        shape = RoundedCornerShape(8.dp)
    ) {
        Text(text, color = color, fontSize = 11.sp, fontWeight = FontWeight.Bold, modifier = Modifier.padding(horizontal = 10.dp, vertical = 4.dp))
    }
}
