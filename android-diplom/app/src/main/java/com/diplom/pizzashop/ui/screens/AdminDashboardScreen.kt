package com.diplom.pizzashop.ui.screens

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.LazyRow
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.*
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.lifecycle.viewmodel.compose.viewModel
import com.diplom.pizzashop.ui.theme.*
import com.diplom.pizzashop.ui.viewmodels.AdminDashboardViewModel
import com.diplom.pizzashop.data.model.Order

@Composable
fun AdminDashboardScreen(
    viewModel: AdminDashboardViewModel = viewModel(),
    onNavigateToProducts: () -> Unit,
    onNavigateToEmployees: () -> Unit,
    onNavigateToAllOrders: () -> Unit
) {
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
                    Text("⚙️ Админ панель", color = TextWhite, fontWeight = FontWeight.Bold, fontSize = 20.sp)
                    Text("Полная статистика и управление", color = TextSecondary, fontSize = 12.sp)
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
            else -> {
                LazyColumn(
                    modifier = Modifier.fillMaxSize(),
                    contentPadding = PaddingValues(16.dp),
                    verticalArrangement = Arrangement.spacedBy(16.dp)
                ) {
                    // Buttons
                    item {
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.spacedBy(12.dp)
                        ) {
                            Button(
                                onClick = onNavigateToProducts,
                                colors = ButtonDefaults.buttonColors(containerColor = OrangeAccent),
                                shape = RoundedCornerShape(16.dp),
                                modifier = Modifier.weight(1f).height(48.dp)
                            ) {
                                Text("✏️ Изменить меню", fontSize = 14.sp)
                            }
                            Button(
                                onClick = onNavigateToEmployees,
                                colors = ButtonDefaults.buttonColors(containerColor = GlassSurface),
                                shape = RoundedCornerShape(16.dp),
                                modifier = Modifier.weight(1f).height(48.dp)
                            ) {
                                Text("👥 Сотрудники", fontSize = 14.sp, color = TextWhite)
                            }
                        }
                    }

                    // Financial stats
                    item {
                        Column(
                            modifier = Modifier.fillMaxWidth(),
                            verticalArrangement = Arrangement.spacedBy(12.dp)
                        ) {
                            Row(
                                modifier = Modifier.fillMaxWidth(),
                                horizontalArrangement = Arrangement.spacedBy(12.dp)
                            ) {
                                StatCard(
                                    title = "Прибыль за сегодня",
                                    value = "${viewModel.todayRevenue.toInt()} ₽",
                                    subtitle = "${viewModel.todayCount} заказов",
                                    modifier = Modifier.weight(1f)
                                )
                                StatCard(
                                    title = "Прибыль за месяц",
                                    value = "${viewModel.monthlyRevenue.toInt()} ₽",
                                    subtitle = "текущий месяц",
                                    modifier = Modifier.weight(1f)
                                )
                            }
                            StatCard(
                                title = "Активных заказов",
                                value = "${viewModel.activeOrders.size}",
                                subtitle = "в работе",
                                modifier = Modifier.fillMaxWidth()
                            )
                        }
                    }

                    // Status counts
                    item {
                        Text("📊 Статусы заказов", color = TextWhite, fontWeight = FontWeight.Bold, fontSize = 16.sp)
                    }
                    item {
                        LazyRow(
                            modifier = Modifier.fillMaxWidth(),
                            contentPadding = PaddingValues(horizontal = 8.dp),
                            horizontalArrangement = Arrangement.spacedBy(8.dp)
                        ) {
                            item {
                                StatusCountCard(
                                    "Новые",
                                    viewModel.statusCounts["created"] ?: 0,
                                    Color.Blue.copy(0.7f),
                                    modifier = Modifier.width(85.dp).height(100.dp)
                                )
                            }
                            item {
                                StatusCountCard(
                                    "Готовятся",
                                    viewModel.statusCounts["cooking"] ?: 0,
                                    Color.Yellow.copy(0.7f),
                                    modifier = Modifier.width(85.dp).height(100.dp)
                                )
                            }
                            item {
                                StatusCountCard(
                                    "Готовы",
                                    viewModel.statusCounts["ready"] ?: 0,
                                    Color.Green.copy(0.7f),
                                    modifier = Modifier.width(85.dp).height(100.dp)
                                )
                            }
                            item {
                                StatusCountCard(
                                    "В доставке",
                                    viewModel.statusCounts["delivering"] ?: 0,
                                    Color.Magenta.copy(0.7f),
                                    modifier = Modifier.width(85.dp).height(100.dp)
                                )
                            }
                            item {
                                StatusCountCard(
                                    "Выполнены",
                                    viewModel.statusCounts["completed"] ?: 0,
                                    TextSecondary,
                                    modifier = Modifier.width(85.dp).height(100.dp)
                                )
                            }
                        }
                    }

                    // Active orders
                    if (viewModel.limitedActiveOrders.isNotEmpty()) {
                        item {
                            Text("🔔 Активные заказы", color = TextWhite, fontWeight = FontWeight.Bold, fontSize = 16.sp)
                        }
                        items(viewModel.limitedActiveOrders) { order ->
                            OrderSummaryCard(order)
                        }
                    }

                    // Completed orders
                    if (viewModel.limitedCompletedOrders.isNotEmpty()) {
                        item {
                            Text("✅ Выполненные заказы", color = TextWhite, fontWeight = FontWeight.Bold, fontSize = 16.sp)
                        }
                        items(viewModel.limitedCompletedOrders) { order ->
                            OrderSummaryCard(order)
                        }
                        item {
                            Button(
                                onClick = onNavigateToAllOrders,
                                colors = ButtonDefaults.buttonColors(containerColor = GlassSurface),
                                shape = RoundedCornerShape(16.dp),
                                modifier = Modifier.fillMaxWidth().height(48.dp)
                            ) {
                                Text("Показать все заказы", fontSize = 14.sp, color = TextWhite)
                            }
                        }
                    }
                }
            }
        }
    }
}

@Composable
fun StatCard(title: String, value: String, subtitle: String, modifier: Modifier = Modifier) {
    Card(
        modifier = modifier,
        shape = RoundedCornerShape(20.dp),
        colors = CardDefaults.cardColors(containerColor = GlassSurface)
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Text(title, color = TextSecondary, fontSize = 12.sp, fontWeight = FontWeight.Bold)
            Text(value, color = TextWhite, fontSize = 24.sp, fontWeight = FontWeight.Bold)
            Text(subtitle, color = TextSecondary, fontSize = 12.sp)
        }
    }
}

@Composable
fun StatusCountCard(label: String, count: Int, color: Color, modifier: Modifier = Modifier) {
    Card(
        modifier = modifier.width(96.dp),
        shape = RoundedCornerShape(12.dp),
        colors = CardDefaults.cardColors(containerColor = color.copy(alpha = 0.1f))
    ) {
        Column(
            modifier = Modifier.padding(12.dp),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Text(count.toString(), color = color, fontSize = 20.sp, fontWeight = FontWeight.Bold)
            Text(
                label,
                color = color.copy(alpha = 0.8f),
                fontSize = 10.sp,
                maxLines = 2
            )
        }
    }
}