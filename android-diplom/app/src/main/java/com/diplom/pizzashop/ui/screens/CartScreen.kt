package com.diplom.pizzashop.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.runtime.remember
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
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
    val snackbarHostState = remember { SnackbarHostState() }

    Scaffold(
        snackbarHost = { SnackbarHost(snackbarHostState) },
        containerColor = DarkBackground
    ) { padding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
        ) {
            Surface(
                color = GlassSurface,
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(bottom = 1.dp)
            ) {
                Column {
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
                    if (viewModel.error != null) {
                        Text(
                            text = viewModel.error!!,
                            color = Color.Red,
                            modifier = Modifier.padding(horizontal = 16.dp, vertical = 8.dp)
                        )
                    }
                    if (viewModel.isLoading) {
                        LinearProgressIndicator(
                            modifier = Modifier
                                .fillMaxWidth()
                                .padding(horizontal = 16.dp)
                        )
                    }
                }
            }

            Spacer(modifier = Modifier.height(12.dp))

            if (viewModel.items.isEmpty()) {
                Box(
                    modifier = Modifier
                        .fillMaxSize()
                        .padding(horizontal = 24.dp),
                    contentAlignment = Alignment.Center
                ) {
                    Column(horizontalAlignment = Alignment.CenterHorizontally) {
                        Icon(
                            Icons.Default.ShoppingCart,
                            contentDescription = null,
                            tint = TextSecondary,
                            modifier = Modifier.size(90.dp)
                        )
                        Spacer(modifier = Modifier.height(12.dp))
                        Text("Корзина пуста", color = TextSecondary, fontSize = 18.sp)
                        Text("Добавь что-нибудь из меню", color = TextSecondary, fontSize = 14.sp)
                    }
                }
            } else {
                LazyColumn(
                    modifier = Modifier
                        .weight(1f)
                        .fillMaxWidth()
                        .padding(horizontal = 16.dp),
                    verticalArrangement = Arrangement.spacedBy(12.dp)
                ) {
                    items(viewModel.items, key = { it.product_id }) { item ->
                        CartItemCard(
                            item = item,
                            onQuantityChange = { newQty -> viewModel.updateQuantity(item.product_id, newQty) },
                            onRemove = { viewModel.removeItem(item.product_id) }
                        )
                    }
                }

                Surface(
                    color = GlassSurface,
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(16.dp),
                    shape = RoundedCornerShape(24.dp)
                ) {
                    Column(modifier = Modifier.padding(16.dp)) {
                        Row(
                            Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween,
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Column {
                                Text("Итого:", color = TextSecondary, fontSize = 16.sp)
                                Text("${viewModel.items.size} товара", color = TextSecondary, fontSize = 12.sp)
                            }
                            Text(
                                "${viewModel.total.toInt()} ₽",
                                color = OrangeAccent,
                                fontWeight = FontWeight.Bold,
                                fontSize = 24.sp
                            )
                        }
                        Spacer(Modifier.height(16.dp))
                        Button(
                            onClick = onCheckout,
                            colors = ButtonDefaults.buttonColors(containerColor = OrangeAccent),
                            shape = RoundedCornerShape(16.dp),
                            modifier = Modifier.fillMaxWidth().height(50.dp),
                            enabled = !viewModel.isLoading
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
            .clip(RoundedCornerShape(20.dp))
            .background(GlassSurface)
            .padding(14.dp),
        verticalAlignment = Alignment.CenterVertically
    ) {
        AsyncImage(
            model = if (item.image_url?.startsWith("http") == true) item.image_url else "http://10.0.2.2:8000${item.image_url ?: ""}",
            contentDescription = item.name,
            contentScale = ContentScale.Crop,
            modifier = Modifier
                .size(70.dp)
                .clip(RoundedCornerShape(16.dp))
        )

        Spacer(Modifier.width(12.dp))

        Column(modifier = Modifier.weight(1f)) {
            Text(
                text = item.name,
                color = TextWhite,
                fontWeight = FontWeight.Bold,
                fontSize = 16.sp,
                maxLines = 1
            )
            Spacer(Modifier.height(4.dp))
            Text(
                text = "${item.price.toInt()} ₽",
                color = TextSecondary,
                fontSize = 14.sp
            )
            Spacer(Modifier.height(10.dp))
            Row(
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.spacedBy(4.dp)
            ) {
                IconButton(
                    onClick = { onQuantityChange(item.quantity - 1) },
                    modifier = Modifier.size(36.dp)
                ) {
                    Icon(Icons.Default.Remove, contentDescription = "Уменьшить", tint = TextSecondary)
                }
                Text(
                    text = "${item.quantity}",
                    color = TextWhite,
                    fontWeight = FontWeight.Bold,
                    fontSize = 16.sp,
                    modifier = Modifier.widthIn(min = 24.dp)
                )
                IconButton(
                    onClick = { onQuantityChange(item.quantity + 1) },
                    modifier = Modifier.size(36.dp)
                ) {
                    Icon(Icons.Default.Add, contentDescription = "Увеличить", tint = OrangeAccent)
                }
            }
        }

        Spacer(Modifier.width(8.dp))

        IconButton(onClick = onRemove) {
            Icon(Icons.Default.Delete, contentDescription = "Удалить", tint = Color.Red)
        }
    }
}
