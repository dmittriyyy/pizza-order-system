package com.diplom.pizzashop.ui.screens

import androidx.compose.animation.*
import androidx.compose.foundation.*
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.*
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.lifecycle.viewmodel.compose.viewModel
import coil.compose.AsyncImage
import com.diplom.pizzashop.data.model.CartItem
import com.diplom.pizzashop.ui.theme.*
import com.diplom.pizzashop.ui.viewmodels.CartViewModel

@Composable
fun CartScreen(
    viewModel: CartViewModel = viewModel(),
    onCheckout: () -> Unit
) {
    LaunchedEffect(Unit) { viewModel.loadCart() }

    // Snackbar for add confirmation
    val snackbarHostState = remember { SnackbarHostState() }

    Scaffold(
        snackbarHost = { SnackbarHost(snackbarHostState) },
        containerColor = DarkBackground
    ) { padding ->
        Column(modifier = Modifier.fillMaxSize().padding(padding)) {
            // Header
            Surface(color = GlassSurface, modifier = Modifier.padding(bottom = 1.dp)) {
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(16.dp),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Text("🛒 Корзина", color = TextWhite, fontWeight = FontWeight.Bold, fontSize = 20.sp)
                    if (viewModel.items.isNotEmpty()) {
                        TextButton(onClick = { viewModel.clearCart() }) {
                            Text("Очистить", color = Color.Red)
                        }
                    }
                }
            }

            // Cart Items
            if (viewModel.items.isEmpty()) {
                Box(Modifier.weight(1f), contentAlignment = Alignment.Center) {
                    Column(horizontalAlignment = Alignment.CenterHorizontally) {
                        Icon(Icons.Default.ShoppingCart, contentDescription = null, tint = TextSecondary, modifier = Modifier.size(80.dp))
                        Text("Корзина пуста", color = TextSecondary, fontSize = 18.sp, modifier = Modifier.padding(top = 16.dp))
                    }
                }
            } else {
                LazyColumn(
                    modifier = Modifier.weight(1f).padding(16.dp),
                    verticalArrangement = Arrangement.spacedBy(12.dp)
                ) {
                    items(viewModel.items, key = { it.product_id }) { item ->
                        CartItemCard(
                            item = item,
                            onQuantityChange = { newQty ->
                                if (newQty > 0) {
                                    // TODO: Call API to update quantity
                                } else {
                                    // TODO: Call API to remove item
                                }
                            },
                            onRemove = {
                                // TODO: Call API to remove item
                            }
                        )
                    }
                }
            }

            // Total & Checkout
            if (viewModel.items.isNotEmpty()) {
                Surface(color = GlassSurface, modifier = Modifier.padding(16.dp), shape = RoundedCornerShape(24.dp)) {
                    Column(modifier = Modifier.padding(16.dp)) {
                        Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                            Text("Итого:", color = TextSecondary, fontSize = 16.sp)
                            Text("${viewModel.total.toInt()} ₽", color = OrangeAccent, fontWeight = FontWeight.Bold, fontSize = 24.sp)
                        }
                        Spacer(Modifier.height(12.dp))
                        Button(
                            onClick = onCheckout,
                            colors = ButtonDefaults.buttonColors(containerColor = OrangeAccent),
                            shape = RoundedCornerShape(16.dp),
                            modifier = Modifier.fillMaxWidth().height(50.dp)
                        ) {
                            Text("Оформить заказ", fontSize = 16.sp, fontWeight = FontWeight.Bold)
                        }
                    }
                }
            }
        }
    }
}

@Composable
fun CartItemCard(
    item: CartItem,
    onQuantityChange: (Int) -> Unit,
    onRemove: () -> Unit
) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .background(GlassSurface, RoundedCornerShape(20.dp))
            .padding(12.dp),
        verticalAlignment = Alignment.CenterVertically
    ) {
        AsyncImage(
            model = "http://10.0.2.2:8000${item.image_url}",
            contentDescription = item.name,
            contentScale = ContentScale.Crop,
            modifier = Modifier.size(60.dp).clip(RoundedCornerShape(12.dp))
        )
        Spacer(Modifier.width(12.dp))
        Column(modifier = Modifier.weight(1f)) {
            Text(item.name, color = TextWhite, fontWeight = FontWeight.Bold, fontSize = 16.sp)
            Text("${item.price.toInt()} ₽", color = TextSecondary, fontSize = 14.sp)
        }
        
        // Quantity Controls
        Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            IconButton(onClick = { onQuantityChange(item.quantity - 1) }) {
                Icon(Icons.Default.Remove, contentDescription = "Уменьшить", tint = TextSecondary)
            }
            Text("${item.quantity}", color = TextWhite, fontWeight = FontWeight.Bold, fontSize = 16.sp)
            IconButton(onClick = { onQuantityChange(item.quantity + 1) }) {
                Icon(Icons.Default.Add, contentDescription = "Увеличить", tint = OrangeAccent)
            }
        }
        
        Spacer(Modifier.width(8.dp))
        IconButton(onClick = onRemove) {
            Icon(Icons.Default.Delete, contentDescription = "Удалить", tint = Color.Red)
        }
    }
}