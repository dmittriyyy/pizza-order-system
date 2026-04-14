package com.diplom.pizzashop

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.animation.core.Spring
import androidx.compose.animation.core.animateDpAsState
import androidx.compose.animation.core.spring
import androidx.compose.foundation.*
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material.icons.outlined.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.*
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.navigation.NavHostController
import androidx.navigation.compose.*
import com.diplom.pizzashop.ui.screens.*
import com.diplom.pizzashop.ui.theme.*
import com.diplom.pizzashop.ui.viewmodels.*
import com.diplom.pizzashop.data.TokenManager

sealed class Screen(val route: String, val title: String, val icon: ImageVector, val selectedIcon: ImageVector) {
    object Menu : Screen("menu", "Меню", Icons.Outlined.LocalPizza, Icons.Filled.LocalPizza)
    object AI : Screen("ai", "AI", Icons.Outlined.SmartToy, Icons.Filled.SmartToy)
    object Cart : Screen("cart", "Корзина", Icons.Outlined.ShoppingCart, Icons.Filled.ShoppingCart)
    object More : Screen("more", "Ещё", Icons.Outlined.MoreHoriz, Icons.Filled.MoreHoriz)
    object Login : Screen("login", "Вход", Icons.Outlined.Login, Icons.Filled.Login)
    object Register : Screen("register", "Регистрация", Icons.Outlined.PersonAdd, Icons.Filled.PersonAdd)
    object Checkout : Screen("checkout", "Оформление", Icons.Outlined.ReceiptLong, Icons.Filled.ReceiptLong)
    object Kitchen : Screen("kitchen", "Кухня", Icons.Outlined.Kitchen, Icons.Filled.Kitchen)
    object Delivery : Screen("delivery", "Доставка", Icons.Outlined.LocalShipping, Icons.Filled.LocalShipping)
}

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        TokenManager.init(applicationContext)
        setContent {
            PizzaTheme {
                Surface(modifier = Modifier.fillMaxSize(), color = DarkBackground) {
                    PizzaApp()
                }
            }
        }
    }
}

@Composable
fun PizzaApp() {
    val navController = rememberNavController()
    val authViewModel: AuthViewModel = viewModel()
    val cartViewModel: CartViewModel = viewModel()
    val menuViewModel: MenuViewModel = viewModel()

    // Определяем, показывать ли док
    val showDock = navController.currentBackStackEntryAsState().value?.destination?.route in 
        listOf(Screen.Menu.route, Screen.AI.route, Screen.Cart.route, Screen.More.route)

    Scaffold(
        bottomBar = { 
            if (showDock) GlassBottomBar(navController = navController) 
        },
        containerColor = DarkBackground
    ) { paddingValues ->
        NavHost(
            navController = navController,
            startDestination = Screen.Menu.route,
            modifier = Modifier.padding(paddingValues)
        ) {
            composable(Screen.Menu.route) { 
                MenuScreen(
                    menuViewModel = menuViewModel, 
                    cartViewModel = cartViewModel,
                    onProductClick = { } 
                ) 
            }
            composable(Screen.AI.route) { AIScreen() }
            composable(Screen.Cart.route) { 
                CartScreen(
                    viewModel = cartViewModel,
                    onCheckout = { navController.navigate(Screen.Checkout.route) }
                ) 
            }
            composable(Screen.Checkout.route) { 
                CheckoutScreen(
                    cartViewModel = cartViewModel,
                    onBack = { navController.popBackStack() },
                    onSuccess = { navController.popBackStack() }
                ) 
            }
            composable(Screen.Kitchen.route) { KitchenScreen() }
            composable(Screen.Delivery.route) { DeliveryScreen() }
            composable(Screen.More.route) { 
                MoreScreen(
                    authViewModel = authViewModel,
                    onNavigateToLogin = { navController.navigate(Screen.Login.route) },
                    onNavigateToRegister = { navController.navigate(Screen.Register.route) },
                    onNavigateToKitchen = { navController.navigate(Screen.Kitchen.route) },
                    onNavigateToDelivery = { navController.navigate(Screen.Delivery.route) }
                ) 
            }
            composable(Screen.Login.route) { 
                LoginScreen(
                    authViewModel = authViewModel,
                    onLoginSuccess = { navController.popBackStack() },
                    onNavigateToRegister = { navController.navigate(Screen.Register.route) }
                )
            }
            composable(Screen.Register.route) { 
                RegisterScreen(
                    authViewModel = authViewModel,
                    onRegisterSuccess = { navController.popBackStack() },
                    onNavigateToLogin = { navController.popBackStack() }
                )
            }
        }
    }
}

@Composable
fun GlassBottomBar(
    navController: NavHostController,
    modifier: Modifier = Modifier
) {
    val navBackStackEntry = navController.currentBackStackEntryAsState()
    val currentRoute = navBackStackEntry.value?.destination?.route

    val screens = listOf(Screen.Menu, Screen.AI, Screen.Cart, Screen.More)

    Box(
        modifier = modifier
            .fillMaxWidth()
            .padding(horizontal = 16.dp, vertical = 16.dp)
    ) {
        // Glass background
        Box(
            modifier = Modifier
                .fillMaxWidth()
                .clip(RoundedCornerShape(32.dp))
                .background(Color(0xFF1A1A2E).copy(alpha = 0.95f))
                .padding(horizontal = 8.dp, vertical = 10.dp)
        ) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceEvenly,
                verticalAlignment = Alignment.CenterVertically
            ) {
                screens.forEach { screen ->
                    val isSelected = currentRoute == screen.route
                    
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
                            .padding(horizontal = 4.dp, vertical = 6.dp)
                    ) {
                        // "Таблетка" фона для активного элемента
                        Box(
                            modifier = Modifier
                                .background(
                                    color = if (isSelected) OrangeAccent.copy(alpha = 0.15f) else Color.Transparent,
                                    shape = RoundedCornerShape(20.dp)
                                )
                                .padding(horizontal = 16.dp, vertical = 8.dp)
                        ) {
                            Column(horizontalAlignment = Alignment.CenterHorizontally) {
                                Icon(
                                    imageVector = if (isSelected) screen.selectedIcon else screen.icon,
                                    contentDescription = screen.title,
                                    tint = if (isSelected) OrangeAccent else Color(0xFF8899AA),
                                    modifier = Modifier.size(24.dp)
                                )
                                Spacer(Modifier.height(2.dp))
                                Text(
                                    text = screen.title,
                                    fontSize = 10.sp,
                                    color = if (isSelected) OrangeAccent else Color(0xFF8899AA),
                                    fontWeight = if (isSelected) FontWeight.Bold else FontWeight.Normal
                                )
                            }
                        }
                    }
                }
            }
        }
    }
}