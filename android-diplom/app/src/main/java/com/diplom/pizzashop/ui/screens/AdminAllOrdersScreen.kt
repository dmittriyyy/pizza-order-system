package com.diplom.pizzashop.ui.screens

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
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
fun AdminAllOrdersScreen(
    viewModel: AdminDashboardViewModel = viewModel(),
    onNavigateBack: () -> Unit
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
                IconButton(onClick = onNavigateBack) {
                    Icon(Icons.Default.ArrowBack, contentDescription = "Назад", tint = TextWhite)
                }
                Text("📋 Все заказы", color = TextWhite, fontWeight = FontWeight.Bold, fontSize = 20.sp)
                Spacer(Modifier.width(48.dp))
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
                    // Active orders
                    if (viewModel.activeOrders.isNotEmpty()) {
                        item {
                            Text("🔔 Активные заказы (${viewModel.activeOrders.size})", color = TextWhite, fontWeight = FontWeight.Bold, fontSize = 16.sp)
                        }
                        items(viewModel.activeOrders) { order ->
                            OrderSummaryCard(order)
                        }
                    }

                    // Completed orders
                    if (viewModel.completedOrders.isNotEmpty()) {
                        item {
                            Text("✅ Выполненные заказы (${viewModel.completedOrders.size})", color = TextWhite, fontWeight = FontWeight.Bold, fontSize = 16.sp)
                        }
                        items(viewModel.completedOrders) { order ->
                            OrderSummaryCard(order)
                        }
                    }

                    if (viewModel.activeOrders.isEmpty() && viewModel.completedOrders.isEmpty()) {
                        item {
                            Box(Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                                Text("Нет заказов", color = TextSecondary, fontSize = 16.sp)
                            }
                        }
                    }
                }
            }
        }
    }
}
