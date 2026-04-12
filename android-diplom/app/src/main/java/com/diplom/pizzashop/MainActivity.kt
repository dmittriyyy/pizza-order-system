package com.diplom.pizzashop

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.LazyRow
import androidx.compose.foundation.lazy.grid.GridCells
import androidx.compose.foundation.lazy.grid.LazyVerticalGrid
import androidx.compose.foundation.lazy.grid.items
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.*
import androidx.compose.material.icons.outlined.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.diplom.pizzashop.ui.viewmodels.MenuViewModel
import com.diplom.pizzashop.ui.screens.ChatScreen
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.navigation.NavHostController
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.currentBackStackEntryAsState
import androidx.navigation.compose.rememberNavController
import coil.compose.AsyncImage
import coil.request.ImageRequest
import com.diplom.pizzashop.data.model.Product
import com.diplom.pizzashop.data.repository.PizzaRepository
import kotlinx.coroutines.launch

// ==================== THEME COLORS ====================
val OrangeAccent = Color(0xFFFF6B00)
val BackgroundDark = Color(0xFF0F0F1A)
val SurfaceDark = Color(0xFF1A1A2E)
val TextWhite = Color(0xFFFFFFFF)
val TextSecondary = Color(0xFF8899AA)

// ==================== SCREENS ====================
sealed class Screen(
    val route: String,
    val title: String,
    val icon: androidx.compose.ui.graphics.vector.ImageVector,
    val selectedIcon: androidx.compose.ui.graphics.vector.ImageVector
) {
    object Menu : Screen("menu", "Меню", Icons.Outlined.LocalPizza, Icons.Filled.LocalPizza)
    object AI : Screen("ai", "AI", Icons.Outlined.SmartToy, Icons.Filled.SmartToy)
    object Cart : Screen("cart", "Корзина", Icons.Outlined.ShoppingCart, Icons.Filled.ShoppingCart)
    object Profile : Screen("profile", "Профиль", Icons.Outlined.Person, Icons.Filled.Person)
    object About : Screen("about", "О нас", Icons.Outlined.Info, Icons.Filled.Info)
}

// ==================== MAIN ACTIVITY ====================
class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            MaterialTheme(
                colorScheme = darkColorScheme(
                    primary = OrangeAccent,
                    background = BackgroundDark,
                    surface = SurfaceDark,
                    onPrimary = TextWhite,
                    onBackground = TextWhite,
                    onSurface = TextWhite
                ),
                typography = androidx.compose.material3.Typography(
                    displayLarge = androidx.compose.ui.text.TextStyle(
                        fontWeight = FontWeight.Bold, fontSize = 32.sp, lineHeight = 40.sp
                    ),
                    headlineMedium = androidx.compose.ui.text.TextStyle(
                        fontWeight = FontWeight.Bold, fontSize = 24.sp, lineHeight = 32.sp
                    ),
                    titleLarge = androidx.compose.ui.text.TextStyle(
                        fontWeight = FontWeight.SemiBold, fontSize = 20.sp, lineHeight = 28.sp
                    ),
                    bodyLarge = androidx.compose.ui.text.TextStyle(
                        fontWeight = FontWeight.Normal, fontSize = 16.sp, lineHeight = 24.sp
                    ),
                    bodyMedium = androidx.compose.ui.text.TextStyle(
                        fontWeight = FontWeight.Normal, fontSize = 14.sp, lineHeight = 20.sp
                    ),
                    labelMedium = androidx.compose.ui.text.TextStyle(
                        fontWeight = FontWeight.Medium, fontSize = 12.sp, lineHeight = 16.sp
                    )
                )
            ) {
                Surface(modifier = Modifier.fillMaxSize(), color = BackgroundDark) {
                    PizzaAppNavGraph()
                }
            }
        }
    }
}

// ==================== NAVIGATION ====================
@Composable
fun PizzaAppNavGraph() {
    val navController = rememberNavController()
    var selectedProduct by remember { mutableStateOf<Product?>(null) }

    Scaffold(
        bottomBar = { GlassBottomBar(navController = navController) },
        containerColor = BackgroundDark
    ) { paddingValues ->
        NavHost(
            navController = navController,
            startDestination = Screen.Menu.route,
            modifier = Modifier.padding(paddingValues)
        ) {
            composable(Screen.Menu.route) {
                MenuScreen(viewModel = viewModel(), onProductClick = { product ->
                    selectedProduct = product
                })
            }
            composable(Screen.AI.route) { AIScreen(navController = navController) }
            composable(Screen.Cart.route) { CartScreen() }
            composable(Screen.Profile.route) { ProfileScreen() }
            composable(Screen.About.route) { AboutScreen() }
        }

        // Product Detail Overlay
        selectedProduct?.let { product ->
            ProductDetailScreen(product = product, onBack = { selectedProduct = null })
        }
    }
}

// ==================== GLASS BOTTOM BAR ====================
@Composable
fun GlassBottomBar(
    navController: NavHostController,
    modifier: Modifier = Modifier
) {
    val navBackStackEntry = navController.currentBackStackEntryAsState()
    val currentRoute = navBackStackEntry.value?.destination?.route

    val screens = listOf(Screen.Menu, Screen.AI, Screen.Cart, Screen.Profile, Screen.About)

    Box(
        modifier = modifier
            .fillMaxWidth()
            .padding(horizontal = 16.dp, vertical = 12.dp)
    ) {
        // Glass background
        Box(
            modifier = Modifier
                .fillMaxWidth()
                .clip(RoundedCornerShape(32.dp))
                .background(Color(0xCC0F0F1A).copy(alpha = 0.85f))
                .padding(horizontal = 8.dp, vertical = 10.dp)
        ) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceEvenly,
                verticalAlignment = Alignment.CenterVertically
            ) {
                screens.forEach { screen ->
                    val isSelected = currentRoute == screen.route
                    val iconTint = if (isSelected) OrangeAccent else TextSecondary
                    val iconSize = if (isSelected) 28.dp else 24.dp

                    Column(
                        horizontalAlignment = Alignment.CenterHorizontally,
                        modifier = Modifier
                            .clickable {
                                if (currentRoute != screen.route) {
                                    navController.navigate(screen.route) {
                                        popUpTo(navController.graph.startDestinationId) { saveState = true }
                                        launchSingleTop = true
                                        restoreState = true
                                    }
                                }
                            }
                            .padding(horizontal = 8.dp, vertical = 4.dp)
                    ) {
                        Icon(
                            imageVector = if (isSelected) screen.selectedIcon else screen.icon,
                            contentDescription = screen.title,
                            tint = iconTint,
                            modifier = Modifier.size(iconSize)
                        )
                        Text(
                            text = screen.title,
                            fontSize = 10.sp,
                            color = if (isSelected) OrangeAccent else TextSecondary,
                            fontWeight = if (isSelected) FontWeight.SemiBold else FontWeight.Normal,
                            modifier = Modifier.padding(top = 2.dp)
                        )
                    }
                }
            }
        }
    }
}

// ==================== MENU SCREEN ====================
@Composable
fun MenuScreen(
    viewModel: MenuViewModel = viewModel(),
    onProductClick: (Product) -> Unit
) {
    Column(modifier = Modifier.fillMaxSize()) {
        // Header
        Text(
            text = "🍕 Наше меню",
            style = MaterialTheme.typography.headlineMedium,
            color = TextWhite,
            modifier = Modifier.padding(20.dp, 20.dp, 20.dp, 10.dp)
        )

        // Categories
        LazyRow(
            modifier = Modifier.padding(horizontal = 20.dp, vertical = 8.dp),
            horizontalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            item {
                FilterChip(
                    selected = viewModel.selectedCategory == null,
                    onClick = { viewModel.selectCategory(null) },
                    label = { Text("Все", color = if (viewModel.selectedCategory == null) TextWhite else TextSecondary) },
                    colors = FilterChipDefaults.filterChipColors(
                        selectedContainerColor = OrangeAccent,
                        containerColor = SurfaceDark
                    )
                )
            }
            items(viewModel.categories) { cat ->
                FilterChip(
                    selected = viewModel.selectedCategory == cat.id,
                    onClick = { viewModel.selectCategory(cat.id) },
                    label = { Text(cat.name, color = if (viewModel.selectedCategory == cat.id) TextWhite else TextSecondary) },
                    colors = FilterChipDefaults.filterChipColors(
                        selectedContainerColor = OrangeAccent,
                        containerColor = SurfaceDark
                    )
                )
            }
        }

        // Loading state
        if (viewModel.isLoading) {
            Box(Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                CircularProgressIndicator(color = OrangeAccent)
            }
        } else if (viewModel.error != null) {
            Box(Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                Column(horizontalAlignment = Alignment.CenterHorizontally) {
                    Text("⚠️", fontSize = 48.sp)
                    Text(viewModel.error!!, color = TextSecondary, modifier = Modifier.padding(top = 12.dp))
                    Button(
                        onClick = { viewModel.loadData() },
                        colors = ButtonDefaults.buttonColors(containerColor = OrangeAccent),
                        shape = RoundedCornerShape(16.dp),
                        modifier = Modifier.padding(top = 16.dp)
                    ) { Text("Повторить") }
                }
            }
        } else {
            // Products Grid
            LazyVerticalGrid(
                columns = GridCells.Fixed(2),
                contentPadding = PaddingValues(16.dp),
                horizontalArrangement = Arrangement.spacedBy(12.dp),
                verticalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                items(viewModel.filteredProducts) { product ->
                    ProductCard(product = product, onClick = { onProductClick(product) })
                }
            }
        }
    }
}

@Composable
fun ProductCard(product: Product, onClick: () -> Unit) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .clickable(onClick = onClick),
        shape = RoundedCornerShape(24.dp),
        colors = CardDefaults.cardColors(containerColor = SurfaceDark)
    ) {
        Column {
            AsyncImage(
                model = ImageRequest.Builder(LocalContext.current)
                    // Добавляем адрес сервера к относительному пути из БД
                    .data("http://10.0.2.2:8000${product.image_url}")
                    .crossfade(true)
                    .build(),
                contentDescription = product.name,
                contentScale = ContentScale.Crop,
                modifier = Modifier
                    .fillMaxWidth()
                    .height(140.dp)
            )
            Column(modifier = Modifier.padding(12.dp)) {
                Text(product.name, style = MaterialTheme.typography.titleLarge, color = TextWhite, maxLines = 1)
                Text(product.description, style = MaterialTheme.typography.bodyMedium, color = TextSecondary, maxLines = 2)
                Spacer(Modifier.height(8.dp))
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Text("${product.price.toInt()} ₽", style = MaterialTheme.typography.titleLarge, color = OrangeAccent, fontWeight = FontWeight.Bold)
                    Spacer(Modifier.weight(1f))
                    Button(
                        onClick = { /* TODO: add to cart */ },
                        colors = ButtonDefaults.buttonColors(containerColor = OrangeAccent),
                        shape = RoundedCornerShape(16.dp),
                        modifier = Modifier.height(32.dp)
                    ) {
                        Text("В корзину", fontSize = 11.sp)
                    }
                }
            }
        }
    }
}

// ==================== PRODUCT DETAIL ====================
@Composable
fun ProductDetailScreen(product: Product, onBack: () -> Unit) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(BackgroundDark)
            .verticalScroll(rememberScrollState())
    ) {
        // Image
        Box {
            AsyncImage(
                model = ImageRequest.Builder(LocalContext.current)
                    // Добавляем адрес сервера к относительному пути из БД
                    .data("http://10.0.2.2:8000${product.image_url}")
                    .crossfade(true)
                    .build(),
                contentDescription = product.name,
                contentScale = ContentScale.Crop,
                modifier = Modifier
                    .fillMaxWidth()
                    .height(300.dp)
            )
            IconButton(
                onClick = onBack,
                modifier = Modifier
                    .padding(16.dp)
                    .background(Color.Black.copy(0.5f), CircleShape)
            ) {
                Icon(Icons.AutoMirrored.Filled.ArrowBack, contentDescription = "Назад", tint = TextWhite)
            }
        }

        Column(modifier = Modifier.padding(20.dp)) {
            Text(product.name, style = MaterialTheme.typography.displayLarge, color = TextWhite)
            Text(product.description, style = MaterialTheme.typography.bodyLarge, color = TextSecondary, modifier = Modifier.padding(top = 12.dp))

            // Nutrition
            if (product.calories != null || product.protein != null) {
                Card(
                    modifier = Modifier.fillMaxWidth().padding(top = 20.dp),
                    colors = CardDefaults.cardColors(containerColor = SurfaceDark),
                    shape = RoundedCornerShape(20.dp)
                ) {
                    Column(modifier = Modifier.padding(16.dp)) {
                        Text("Пищевая ценность", style = MaterialTheme.typography.titleLarge, color = TextWhite)
                        Spacer(Modifier.height(12.dp))
                        Row(horizontalArrangement = Arrangement.SpaceEvenly, modifier = Modifier.fillMaxWidth()) {
                            NutritionItem("ккал", product.calories?.toInt()?.toString() ?: "-")
                            NutritionItem("белки", "${product.protein ?: "-"}г")
                            NutritionItem("жиры", "${product.fat ?: "-"}г")
                            NutritionItem("углеводы", "${product.carbohydrates ?: "-"}г")
                        }
                    }
                }
            }

            // Ingredients
            if (!product.ingredients.isNullOrEmpty()) {
                Text("Состав", style = MaterialTheme.typography.titleLarge, color = TextWhite, modifier = Modifier.padding(top = 20.dp))
                Spacer(Modifier.height(8.dp))
                FlowRow(horizontalArrangement = Arrangement.spacedBy(8.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                    product.ingredients.forEach { ing ->
                        SuggestionChip(
                            onClick = { },
                            label = { Text(ing, color = TextSecondary) },
                            colors = SuggestionChipDefaults.suggestionChipColors(containerColor = SurfaceDark),
                            shape = RoundedCornerShape(16.dp)
                        )
                    }
                }
            }

            // Price & Button
            Spacer(Modifier.height(24.dp))
            Row(verticalAlignment = Alignment.CenterVertically) {
                Text("${product.price.toInt()} ₽", style = MaterialTheme.typography.displayLarge, color = OrangeAccent)
                Spacer(Modifier.weight(1f))
                Button(
                    onClick = { /* TODO: add to cart */ },
                    colors = ButtonDefaults.buttonColors(containerColor = OrangeAccent),
                    shape = RoundedCornerShape(24.dp),
                    modifier = Modifier.height(48.dp).width(160.dp)
                ) {
                    Text("В корзину", fontSize = 16.sp)
                }
            }
        }
    }
}

@Composable
fun NutritionItem(label: String, value: String) {
    Column(horizontalAlignment = Alignment.CenterHorizontally) {
        Text(value, style = MaterialTheme.typography.titleLarge, color = OrangeAccent, fontWeight = FontWeight.Bold)
        Text(label, style = MaterialTheme.typography.labelMedium, color = TextSecondary)
    }
}

@Composable
fun FlowRow(
    modifier: Modifier = Modifier,
    horizontalArrangement: Arrangement.Horizontal = Arrangement.Start,
    verticalArrangement: Arrangement.Vertical = Arrangement.Top,
    content: @Composable () -> Unit
) {
    Row(
        modifier = modifier,
        horizontalArrangement = horizontalArrangement
    ) {
        content()
    }
}

// ==================== OTHER SCREENS ====================
@Composable
fun AIScreen(navController: NavHostController) {
    ChatScreen(onBack = { navController.popBackStack() })
}

@Composable
fun CartScreen() {
    Box(Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
        Column(horizontalAlignment = Alignment.CenterHorizontally) {
            Icon(Icons.Default.ShoppingCart, contentDescription = null, tint = OrangeAccent, modifier = Modifier.size(80.dp))
            Text("Корзина пуста", style = MaterialTheme.typography.headlineMedium, color = TextWhite, modifier = Modifier.padding(top = 16.dp))
            Text("Добавьте что-нибудь вкусное!", color = TextSecondary, modifier = Modifier.padding(top = 8.dp))
        }
    }
}

@Composable
fun ProfileScreen() {
    Box(Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
        Column(horizontalAlignment = Alignment.CenterHorizontally) {
            Icon(Icons.Default.Person, contentDescription = null, tint = OrangeAccent, modifier = Modifier.size(80.dp))
            Text("Профиль", style = MaterialTheme.typography.headlineMedium, color = TextWhite, modifier = Modifier.padding(top = 16.dp))
        }
    }
}

@Composable
fun AboutScreen() {
    Box(Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
        Column(horizontalAlignment = Alignment.CenterHorizontally, modifier = Modifier.padding(20.dp)) {
            Icon(Icons.Default.Info, contentDescription = null, tint = OrangeAccent, modifier = Modifier.size(80.dp))
            Text("Piazza Pizza", style = MaterialTheme.typography.displayLarge, color = TextWhite, modifier = Modifier.padding(top = 16.dp))
            Text("Калуга, улица Кирова, 1\n\nДоставка: 30 минут или пицца бесплатно!\n\nРаботаем: 10:00 - 23:00",
                style = MaterialTheme.typography.bodyLarge, color = TextSecondary, modifier = Modifier.padding(top = 16.dp))
        }
    }
}
