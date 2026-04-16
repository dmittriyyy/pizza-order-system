package com.diplom.pizzashop.ui.screens

import androidx.compose.foundation.*
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.*
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.*
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.lifecycle.viewmodel.compose.viewModel
import com.diplom.pizzashop.ui.theme.*
import com.diplom.pizzashop.ui.viewmodels.AuthViewModel

@Composable
fun MoreScreen(
    authViewModel: AuthViewModel = viewModel(),
    onNavigateToLogin: () -> Unit,
    onNavigateToRegister: () -> Unit,
    onNavigateToProfile: () -> Unit,
    onNavigateToAbout: () -> Unit,
    onNavigateToKitchen: () -> Unit = {},
    onNavigateToDelivery: () -> Unit = {},
    onNavigateToAdminDashboard: () -> Unit = {},
    onNavigateToAdminProducts: () -> Unit = {},
    onNavigateToAdminEmployees: () -> Unit = {}
) {
    LazyColumn(
        modifier = Modifier.fillMaxSize().padding(16.dp), 
        verticalArrangement = Arrangement.spacedBy(12.dp)
    ) {
        item {
            Text("Ещё", style = MaterialTheme.typography.headlineMedium, color = TextWhite, modifier = Modifier.padding(bottom = 8.dp))
        }
        
        if (!authViewModel.isAuthenticated) {
            // Кнопки входа и регистрации
            item {
                Card(
                    shape = RoundedCornerShape(20.dp),
                    colors = CardDefaults.cardColors(containerColor = OrangeAccent)
                ) {
                    Row(
                        modifier = Modifier.padding(16.dp).fillMaxWidth().clickable(onClick = onNavigateToLogin),
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.SpaceBetween
                    ) {
                        Text("Войти", color = TextWhite, fontWeight = FontWeight.Bold, fontSize = 18.sp)
                        Icon(Icons.AutoMirrored.Filled.Login, contentDescription = "Login", tint = TextWhite)
                    }
                }
            }
            
            item {
                Card(
                    shape = RoundedCornerShape(20.dp),
                    colors = CardDefaults.cardColors(containerColor = GlassSurface),
                    border = BorderStroke(1.dp, OrangeAccent.copy(0.3f))
                ) {
                    Row(
                        modifier = Modifier.padding(16.dp).fillMaxWidth().clickable(onClick = onNavigateToRegister),
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.SpaceBetween
                    ) {
                        Text("Зарегистрироваться", color = TextWhite, fontWeight = FontWeight.Bold, fontSize = 18.sp)
                        Icon(Icons.Default.PersonAdd, contentDescription = "Register", tint = OrangeAccent)
                    }
                }
            }
            
            item {
                Text("Доступно после входа:", color = TextSecondary, fontSize = 12.sp, modifier = Modifier.padding(top = 8.dp))
            }
        } else {
            // Профиль
            item {
                MoreCard(icon = Icons.Default.Person, title = "Профиль", subtitle = "Личные данные и заказы", onClick = onNavigateToProfile)
            }
            item {
                MoreCard(icon = Icons.Default.Info, title = "О нас", subtitle = "Информация о Piazza Pizza", onClick = onNavigateToAbout)
            }
            
            // Разделитель
            item {
                HorizontalDivider(color = TextSecondary.copy(0.2f), modifier = Modifier.padding(vertical = 8.dp))
            }
            
            // Кнопки выхода
            item {
                TextButton(onClick = { authViewModel.logout() }, modifier = Modifier.fillMaxWidth()) {
                    Text("Выйти из аккаунта", color = Color.Red)
                }
            }
            
            // Динамические кнопки ролей
            if (authViewModel.userRole == "admin" || authViewModel.userRole == "cook" || authViewModel.userRole == "courier") {
                item {
                    Text("Сотрудникам", color = TextSecondary, modifier = Modifier.padding(top = 8.dp))
                }

                if (authViewModel.userRole == "admin") {
                    item { MoreCard(icon = Icons.Default.AdminPanelSettings, title = "Админ панель", subtitle = "Управление товарами", onClick = onNavigateToAdminDashboard) }
                    // Админ имеет доступ ко всему
                    item { 
                        MoreCard(
                            icon = Icons.Default.Kitchen, 
                            title = "Кухня", 
                            subtitle = "Заказы на приготовление",
                            onClick = onNavigateToKitchen
                        ) 
                    }
                    item { 
                        MoreCard(
                            icon = Icons.Default.LocalShipping, 
                            title = "Доставка", 
                            subtitle = "Активные заказы",
                            onClick = onNavigateToDelivery
                        ) 
                    }
                }
                if (authViewModel.userRole == "cook") {
                    item { MoreCard(icon = Icons.Default.Kitchen, title = "Кухня", subtitle = "Заказы на приготовление", onClick = onNavigateToKitchen) }
                }
                if (authViewModel.userRole == "courier") {
                    item { MoreCard(icon = Icons.Default.LocalShipping, title = "Доставка", subtitle = "Активные заказы", onClick = onNavigateToDelivery) }
                }
            }
        }
    }
}

@Composable
fun MoreCard(
    icon: androidx.compose.ui.graphics.vector.ImageVector,
    title: String,
    subtitle: String,
    onClick: () -> Unit = {}
) {
    Card(
        shape = RoundedCornerShape(20.dp),
        colors = CardDefaults.cardColors(containerColor = GlassSurface),
        modifier = Modifier.clickable(onClick = onClick)
    ) {
        Row(modifier = Modifier.padding(16.dp).fillMaxWidth(), verticalAlignment = Alignment.CenterVertically) {
            Icon(icon, contentDescription = title, tint = OrangeAccent, modifier = Modifier.size(32.dp))
            Spacer(Modifier.width(16.dp))
            Column {
                Text(title, color = TextWhite, fontWeight = FontWeight.Bold, fontSize = 16.sp)
                Text(subtitle, color = TextSecondary, fontSize = 12.sp)
            }
        }
    }
}