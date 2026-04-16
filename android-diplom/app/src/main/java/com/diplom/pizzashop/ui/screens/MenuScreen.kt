package com.diplom.pizzashop.ui.screens

import androidx.compose.animation.*
import androidx.compose.animation.core.*
import androidx.compose.foundation.*
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.grid.*
import androidx.compose.foundation.lazy.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material3.*
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.runtime.*
import kotlinx.coroutines.launch
import androidx.compose.ui.*
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.scale
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.hapticfeedback.HapticFeedbackType
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.LocalHapticFeedback
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.lifecycle.viewmodel.compose.viewModel
import coil.compose.AsyncImage
import com.diplom.pizzashop.data.model.Product
import com.diplom.pizzashop.ui.theme.*
import com.diplom.pizzashop.ui.viewmodels.MenuViewModel
import com.diplom.pizzashop.ui.viewmodels.CartViewModel

@Composable
fun MenuScreen(
    menuViewModel: MenuViewModel = viewModel(),
    cartViewModel: CartViewModel = viewModel(),
    onProductClick: (Product) -> Unit
) {
    val haptic = LocalHapticFeedback.current
    val snackbarHostState = remember { SnackbarHostState() }
    val scope = rememberCoroutineScope()
    var addedProductId by remember { mutableStateOf<Int?>(null) }

    Scaffold(
        snackbarHost = { SnackbarHost(snackbarHostState) },
        containerColor = DarkBackground
    ) { padding ->
        Column(modifier = Modifier.fillMaxSize().padding(padding)) {
            // Header
            Text(
                text = "🍕 Наше меню",
                style = MaterialTheme.typography.headlineMedium,
                color = TextWhite,
                modifier = Modifier.padding(20.dp, 20.dp, 20.dp, 10.dp)
            )

            // Categories
            if (menuViewModel.categories.isNotEmpty()) {
                LazyRow(
                    modifier = Modifier.padding(horizontal = 20.dp, vertical = 8.dp),
                    horizontalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    item {
                        FilterChip(
                            selected = menuViewModel.selectedCategory == null,
                            onClick = { menuViewModel.selectCategory(null) },
                            label = { Text("Все") },
                            colors = FilterChipDefaults.filterChipColors(
                                selectedContainerColor = OrangeAccent,
                                containerColor = GlassSurface
                            )
                        )
                    }
                    items(menuViewModel.categories) { cat ->
                        FilterChip(
                            selected = menuViewModel.selectedCategory == cat.id,
                            onClick = { menuViewModel.selectCategory(cat.id) },
                            label = { Text(cat.name) },
                            colors = FilterChipDefaults.filterChipColors(
                                selectedContainerColor = OrangeAccent,
                                containerColor = GlassSurface
                            )
                        )
                    }
                }
            }

            // Products Grid
            if (menuViewModel.isLoading) {
                Box(Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                    CircularProgressIndicator(color = OrangeAccent)
                }
            } else if (menuViewModel.error != null) {
                Box(Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                    Column(horizontalAlignment = Alignment.CenterHorizontally) {
                        Text(menuViewModel.error!!, color = Color.Red)
                        Button(onClick = { menuViewModel.loadData() }, colors = ButtonDefaults.buttonColors(OrangeAccent)) {
                            Text("Повторить")
                        }
                    }
                }
            } else {
                LazyVerticalGrid(
                    columns = GridCells.Fixed(2),
                    contentPadding = PaddingValues(16.dp),
                    horizontalArrangement = Arrangement.spacedBy(12.dp),
                    verticalArrangement = Arrangement.spacedBy(12.dp)
                ) {
                    items(menuViewModel.filteredProducts) { product ->
                        ProductCard(
                            product = product,
                            onClick = { onProductClick(product) },
                            onAddToCart = { 
                                haptic.performHapticFeedback(HapticFeedbackType.LongPress)
                                cartViewModel.addToCart(product.id)
                                addedProductId = product.id
                                // Show snackbar
                                scope.launch {
                                    snackbarHostState.showSnackbar("✅ ${product.name} добавлен в корзину!")
                                    addedProductId = null
                                }
                            }
                        )
                    }
                }
            }
        }
    }
}

@Composable
fun ProductCard(product: Product, onClick: () -> Unit, onAddToCart: () -> Unit) {
    var isAnimating by remember { mutableStateOf(false) }
    
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .clickable(onClick = onClick),
        shape = RoundedCornerShape(24.dp),
        colors = CardDefaults.cardColors(containerColor = GlassSurface)
    ) {
        Column {
            AsyncImage(
                model = if (product.image_url?.startsWith("http") == true) product.image_url else "http://10.0.2.2:8000${product.image_url ?: ""}",
                contentDescription = product.name,
                contentScale = ContentScale.Crop,
                modifier = Modifier
                    .fillMaxWidth()
                    .height(140.dp)
            )
            Column(modifier = Modifier.padding(12.dp)) {
                Text(product.name, style = MaterialTheme.typography.titleLarge, color = TextWhite, maxLines = 1)
                Spacer(Modifier.height(8.dp))
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Text("${product.price.toInt()} ₽", style = MaterialTheme.typography.titleLarge, color = OrangeAccent, fontWeight = FontWeight.Bold)
                    Spacer(Modifier.weight(1f))
                    Button(
                        onClick = {
                            isAnimating = true
                            onAddToCart()
                            androidx.compose.animation.core.Animatable(0f).also { anim ->
                                // Reset animation state after delay
                            }
                        },
                        colors = ButtonDefaults.buttonColors(containerColor = OrangeAccent),
                        shape = RoundedCornerShape(16.dp),
                        modifier = Modifier
                            .height(32.dp)
                            .scale(if (isAnimating) 1.2f else 1f)
                            .then(
                                Modifier.animateContentSize(
                                    animationSpec = spring(dampingRatio = Spring.DampingRatioMediumBouncy)
                                )
                            )
                    ) {
                        Text("В корзину", fontSize = 11.sp)
                    }
                }
            }
        }
    }
    
    LaunchedEffect(isAnimating) {
        if (isAnimating) {
            kotlinx.coroutines.delay(300)
            isAnimating = false
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ProductDetailScreen(
    product: Product?,
    cartViewModel: CartViewModel,
    onBack: () -> Unit
) {
    Scaffold(
        topBar = {
            SmallTopAppBar(
                title = { Text(product?.name ?: "Товар", color = TextWhite) },
                navigationIcon = {
                    IconButton(onClick = onBack) {
                        Icon(Icons.Filled.ArrowBack, contentDescription = "Назад", tint = TextWhite)
                    }
                },
                colors = TopAppBarDefaults.smallTopAppBarColors(containerColor = DarkBackground)
            )
        },
        containerColor = DarkBackground
    ) { padding ->
        if (product == null) {
            Box(Modifier.fillMaxSize().padding(padding), contentAlignment = Alignment.Center) {
                Text("Товар не найден", color = TextWhite)
            }
            return@Scaffold
        }

        Column(
            modifier = Modifier
                .fillMaxSize()
                .verticalScroll(rememberScrollState())
                .padding(padding)
                .padding(16.dp)
        ) {
            AsyncImage(
                model = if (product.image_url?.startsWith("http") == true) product.image_url else "http://10.0.2.2:8000${product.image_url ?: ""}",
                contentDescription = product.name,
                contentScale = ContentScale.Crop,
                modifier = Modifier
                    .fillMaxWidth()
                    .height(260.dp)
                    .clip(RoundedCornerShape(24.dp))
            )

            Spacer(Modifier.height(20.dp))
            Text(product.name, style = MaterialTheme.typography.headlineSmall, color = TextWhite)
            Spacer(Modifier.height(8.dp))
            Text("${product.price.toInt()} ₽", style = MaterialTheme.typography.headlineSmall, color = OrangeAccent, fontWeight = FontWeight.Bold)
            Spacer(Modifier.height(16.dp))
            Text(product.description, style = MaterialTheme.typography.bodyMedium, color = TextSecondary)

            Spacer(Modifier.height(20.dp))
            Column(verticalArrangement = Arrangement.spacedBy(10.dp)) {
                product.calories?.let {
                    DetailRow(label = "Калории", value = "$it ккал")
                }
                product.weight?.let {
                    DetailRow(label = "Вес", value = "$it г")
                }
                product.protein?.let {
                    DetailRow(label = "Белки", value = "${it} г")
                }
                product.fat?.let {
                    DetailRow(label = "Жиры", value = "${it} г")
                }
                product.carbohydrates?.let {
                    DetailRow(label = "Углеводы", value = "${it} г")
                }
                product.ingredients?.takeIf { it.isNotEmpty() }?.let {
                    DetailRow(label = "Ингредиенты", value = it.joinToString(", "))
                }
            }

            Spacer(Modifier.height(24.dp))
            Button(
                onClick = { cartViewModel.addToCart(product.id) },
                colors = ButtonDefaults.buttonColors(containerColor = OrangeAccent),
                shape = RoundedCornerShape(16.dp),
                modifier = Modifier.fillMaxWidth().height(50.dp)
            ) {
                Text("Добавить в корзину", fontSize = 16.sp)
            }
        }
    }
}

@Composable
fun DetailRow(label: String, value: String) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .background(GlassSurface, shape = RoundedCornerShape(16.dp))
            .padding(14.dp),
        horizontalArrangement = Arrangement.SpaceBetween,
        verticalAlignment = Alignment.CenterVertically
    ) {
        Text(label, color = TextSecondary)
        Text(value, color = TextWhite, fontWeight = FontWeight.Bold)
    }
}
