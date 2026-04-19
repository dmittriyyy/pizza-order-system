package com.diplom.pizzashop.ui.screens

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Add
import androidx.compose.material.icons.filled.Delete
import androidx.compose.material.icons.filled.Edit
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
import com.diplom.pizzashop.data.model.Product
import com.diplom.pizzashop.ui.theme.*
import com.diplom.pizzashop.ui.viewmodels.AdminProductsViewModel

@Composable
fun AdminProductsScreen(
    viewModel: AdminProductsViewModel = viewModel(),
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
                Column {
                    Text("✏️ Изменить меню", color = TextWhite, fontWeight = FontWeight.Bold, fontSize = 20.sp)
                    Text("Добавление, редактирование и удаление товаров", color = TextSecondary, fontSize = 12.sp)
                }
                FloatingActionButton(
                    onClick = { /* TODO: open add modal */ },
                    containerColor = OrangeAccent
                ) {
                    Icon(Icons.Default.Add, contentDescription = "Add product", tint = TextWhite)
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
                    verticalArrangement = Arrangement.spacedBy(12.dp)
                ) {
                    // Stats
                    item {
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.spacedBy(12.dp)
                        ) {
                            StatCard(
                                title = "Всего товаров",
                                value = viewModel.products.size.toString(),
                                subtitle = "",
                                modifier = Modifier.weight(1f)
                            )
                            StatCard(
                                title = "Категорий",
                                value = viewModel.categories.size.toString(),
                                subtitle = "",
                                modifier = Modifier.weight(1f)
                            )
                        }
                    }

                    // Products
                    items(viewModel.products) { product ->
                        ProductAdminCard(product, viewModel)
                    }
                }
            }
        }
    }
}

@Composable
fun ProductAdminCard(product: Product, viewModel: AdminProductsViewModel) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(16.dp),
        colors = CardDefaults.cardColors(containerColor = GlassSurface)
    ) {
        Row(modifier = Modifier.padding(16.dp)) {
            // Image
            AsyncImage(
                model = if (product.image_url?.startsWith("http") == true) product.image_url else "http://10.0.2.2:8000${product.image_url ?: ""}",
                contentDescription = product.name,
                contentScale = ContentScale.Crop,
                modifier = Modifier.size(80.dp).clip(RoundedCornerShape(12.dp))
            )

            Spacer(Modifier.width(16.dp))

            // Info
            Column(modifier = Modifier.weight(1f)) {
                Text(product.name, color = TextWhite, fontWeight = FontWeight.Bold, fontSize = 16.sp)
                Text(product.description, color = TextSecondary, fontSize = 12.sp, maxLines = 2)
                Spacer(Modifier.height(4.dp))
                Text("${product.price.toInt()} ₽", color = OrangeAccent, fontWeight = FontWeight.Bold)
                val totalCalories = product.total_calories
                    ?: if ((product.calories ?: 0) > 0 && (product.weight ?: 0) > 0) {
                        ((product.calories ?: 0) * (product.weight ?: 0) + 50) / 100
                    } else {
                        0
                    }
                if (totalCalories > 0) {
                    Text("$totalCalories ккал за порцию", color = TextSecondary, fontSize = 11.sp)
                }
            }

            // Actions
            Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                IconButton(
                    onClick = { /* TODO: edit */ },
                    modifier = Modifier.size(32.dp)
                ) {
                    Icon(Icons.Default.Edit, contentDescription = "Edit", tint = OrangeAccent, modifier = Modifier.size(20.dp))
                }
                IconButton(
                    onClick = { viewModel.deleteProduct(product.id) },
                    modifier = Modifier.size(32.dp)
                ) {
                    Icon(Icons.Default.Delete, contentDescription = "Delete", tint = Color.Red, modifier = Modifier.size(20.dp))
                }
            }
        }
    }
}
