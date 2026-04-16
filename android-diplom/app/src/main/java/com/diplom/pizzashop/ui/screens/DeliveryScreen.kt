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
import com.diplom.pizzashop.ui.viewmodels.DeliveryViewModel

@Composable
fun DeliveryScreen(viewModel: DeliveryViewModel = viewModel()) {
    Column(modifier = Modifier.fillMaxSize()) {
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
                    Text("🚚 Доставка", color = TextWhite, fontWeight = FontWeight.Bold, fontSize = 20.sp)
                    Text("Заберите и доставьте клиентам", color = TextSecondary, fontSize = 12.sp)
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
            viewModel.readyOrders.isEmpty() && viewModel.deliveringOrders.isEmpty() -> {
                Box(Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                    Column(horizontalAlignment = Alignment.CenterHorizontally) {
                        Text("🛵", fontSize = 48.sp)
                        Text("Нет доступных заказов", color = TextWhite, fontSize = 18.sp, modifier = Modifier.padding(top = 16.dp))
                        Text("Все заказы доставлены!", color = TextSecondary, fontSize = 14.sp)
                    }
                }
            }
            else -> {
                LazyColumn(
                    modifier = Modifier.fillMaxSize(),
                    contentPadding = PaddingValues(16.dp),
                    verticalArrangement = Arrangement.spacedBy(16.dp)
                ) {
                    // Ready orders
                    if (viewModel.readyOrders.isNotEmpty()) {
                        item {
                            Text("📦 Готовы к доставке", color = TextWhite, fontWeight = FontWeight.Bold, fontSize = 16.sp)
                        }
                        items(viewModel.readyOrders, key = { it.id }) { order ->
                            ReadyOrderCard(order, viewModel)
                        }
                    }

                    // Delivering orders
                    if (viewModel.deliveringOrders.isNotEmpty()) {
                        item {
                            Spacer(Modifier.height(8.dp))
                            Text("🚀 В доставке", color = TextWhite, fontWeight = FontWeight.Bold, fontSize = 16.sp)
                        }
                        items(viewModel.deliveringOrders, key = { it.id }) { order ->
                            DeliveringOrderCard(order, viewModel)
                        }
                    }
                }
            }
        }
    }
}

@Composable
fun ReadyOrderCard(order: Order, viewModel: DeliveryViewModel) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(20.dp),
        colors = CardDefaults.cardColors(containerColor = GlassSurface)
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Text("Заказ #${order.id}", color = TextWhite, fontWeight = FontWeight.Bold, fontSize = 18.sp)
            Spacer(Modifier.height(8.dp))

            // Address
            Surface(color = DarkCardBackground, shape = RoundedCornerShape(12.dp), modifier = Modifier.fillMaxWidth()) {
                Row(modifier = Modifier.padding(12.dp)) {
                    Text("📍 ", fontSize = 16.sp)
                    Column {
                        Text("Адрес:", color = TextSecondary, fontSize = 12.sp, fontWeight = FontWeight.Bold)
                        Text(order.delivery_address, color = TextWhite, fontSize = 14.sp)
                    }
                }
            }

            Spacer(Modifier.height(8.dp))

            // Customer info
            Surface(color = DarkCardBackground, shape = RoundedCornerShape(12.dp), modifier = Modifier.fillMaxWidth()) {
                Row(
                    modifier = Modifier.padding(12.dp).fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Column {
                        Text(order.customer_name ?: "Клиент", color = TextWhite, fontWeight = FontWeight.Bold)
                        if (order.customer_phone != null) {
                            Text(order.customer_phone, color = TextSecondary, fontSize = 13.sp)
                        }
                    }
                    if (order.customer_phone != null) {
                        Surface(
                            color = OrangeAccent.copy(0.2f),
                            shape = RoundedCornerShape(8.dp)
                        ) {
                            Text("📞 ${order.customer_phone}", color = OrangeAccent, fontSize = 12.sp, modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp).clickable { })
                        }
                    }
                }
            }

            Spacer(Modifier.height(8.dp))

            // Items
            Surface(color = DarkCardBackground, shape = RoundedCornerShape(12.dp), modifier = Modifier.fillMaxWidth()) {
                Column(modifier = Modifier.padding(12.dp)) {
                    order.items.forEach { item ->
                        Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                            Text(item.product?.name ?: "Товар", color = TextWhite, fontSize = 14.sp)
                            Text("× ${item.quantity}", color = TextSecondary)
                        }
                        if (item != order.items.last()) HorizontalDivider(color = TextSecondary.copy(0.1f), modifier = Modifier.padding(vertical = 4.dp))
                    }
                }
            }

            Spacer(Modifier.height(12.dp))

            Button(
                onClick = { viewModel.takeOrder(order.id) },
                enabled = !viewModel.isProcessing,
                colors = ButtonDefaults.buttonColors(containerColor = OrangeAccent),
                shape = RoundedCornerShape(16.dp),
                modifier = Modifier.fillMaxWidth().height(48.dp)
            ) {
                Text(if (viewModel.isProcessing) "..." else "🚀 Забрать заказ", fontSize = 16.sp)
            }
        }
    }
}

@Composable
fun DeliveringOrderCard(order: Order, viewModel: DeliveryViewModel) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(20.dp),
        colors = CardDefaults.cardColors(containerColor = GlassSurface),
        border = BorderStroke(1.dp, Purple.copy(alpha = 0.3f))
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text("Заказ #${order.id}", color = TextWhite, fontWeight = FontWeight.Bold, fontSize = 18.sp)
                Surface(color = Purple.copy(alpha = 0.2f), shape = RoundedCornerShape(8.dp)) {
                    Text("В доставке", color = Purple.copy(0.8f), fontSize = 11.sp, fontWeight = FontWeight.Bold, modifier = Modifier.padding(horizontal = 10.dp, vertical = 4.dp))
                }
            }

            Spacer(Modifier.height(8.dp))

            // Address
            Surface(color = DarkCardBackground, shape = RoundedCornerShape(12.dp), modifier = Modifier.fillMaxWidth()) {
                Column(modifier = Modifier.padding(12.dp)) {
                    Text("📍 ${order.delivery_address}", color = TextWhite, fontSize = 14.sp)
                    if (order.delivery_comment != null) {
                        Text("💬 ${order.delivery_comment}", color = TextSecondary, fontSize = 12.sp)
                    }
                }
            }

            Spacer(Modifier.height(8.dp))

            // Customer
            Surface(color = DarkCardBackground, shape = RoundedCornerShape(12.dp), modifier = Modifier.fillMaxWidth()) {
                Row(
                    modifier = Modifier.padding(12.dp).fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Column {
                        Text(order.customer_name ?: "Клиент", color = TextWhite, fontWeight = FontWeight.Bold)
                        if (order.customer_phone != null) Text(order.customer_phone, color = TextSecondary, fontSize = 13.sp)
                    }
                    if (order.customer_phone != null) {
                        Text("📞", fontSize = 20.sp, modifier = Modifier.clickable { })
                    }
                }
            }

            Spacer(Modifier.height(8.dp))

            // Pickup time
            if (order.picked_up_at != null) {
                Text("⏰ Забран в: ${formatPickupTime(order.picked_up_at)}", color = TextSecondary, fontSize = 13.sp)
                Spacer(Modifier.height(8.dp))
            }

            Button(
                onClick = { viewModel.completeDelivery(order.id) },
                enabled = !viewModel.isProcessing,
                colors = ButtonDefaults.buttonColors(containerColor = Color.Green.copy(0.7f)),
                shape = RoundedCornerShape(16.dp),
                modifier = Modifier.fillMaxWidth().height(48.dp)
            ) {
                Text(if (viewModel.isProcessing) "..." else "✅ Доставлен", fontSize = 16.sp)
            }
        }
    }
}

fun formatPickupTime(time: String): String {
    return try {
        val parts = time.split("T")
        if (parts.size > 1) parts[1].substring(0, 5) else time
    } catch (e: Exception) {
        time
    }
}
