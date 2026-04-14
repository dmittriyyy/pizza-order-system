package com.diplom.pizzashop.ui.screens

import androidx.compose.foundation.*
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.*
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.PasswordVisualTransformation
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.lifecycle.viewmodel.compose.viewModel
import com.diplom.pizzashop.ui.theme.*
import com.diplom.pizzashop.ui.viewmodels.AuthViewModel

@Composable
fun LoginScreen(
    authViewModel: AuthViewModel = viewModel(),
    onLoginSuccess: () -> Unit,
    onNavigateToRegister: () -> Unit
) {
    var login by remember { mutableStateOf("") }
    var password by remember { mutableStateOf("") }
    
    val isLoading = authViewModel.isLoading
    val error = authViewModel.error

    // Если вошли успешно, возвращаемся назад
    LaunchedEffect(authViewModel.isAuthenticated) {
        if (authViewModel.isAuthenticated) onLoginSuccess()
    }

    Column(
        modifier = Modifier.fillMaxSize().padding(24.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        Text("Вход", fontSize = 32.sp, fontWeight = FontWeight.Bold, color = TextWhite)
        Spacer(Modifier.height(40.dp))

        OutlinedTextField(
            value = login, onValueChange = { login = it },
            label = { Text("Логин", color = TextSecondary) },
            modifier = Modifier.fillMaxWidth(),
            colors = OutlinedTextFieldDefaults.colors(focusedBorderColor = OrangeAccent, unfocusedBorderColor = TextSecondary.copy(0.3f))
        )
        Spacer(Modifier.height(16.dp))
        OutlinedTextField(
            value = password, onValueChange = { password = it },
            label = { Text("Пароль", color = TextSecondary) },
            modifier = Modifier.fillMaxWidth(),
            visualTransformation = PasswordVisualTransformation(),
            colors = OutlinedTextFieldDefaults.colors(focusedBorderColor = OrangeAccent, unfocusedBorderColor = TextSecondary.copy(0.3f))
        )

        if (error != null) Text(error, color = Color.Red, modifier = Modifier.padding(top = 12.dp))
        Spacer(Modifier.height(24.dp))

        Button(
            onClick = { if (login.isNotBlank() && password.isNotBlank()) authViewModel.login(login, password) },
            modifier = Modifier.fillMaxWidth().height(50.dp),
            shape = RoundedCornerShape(16.dp),
            colors = ButtonDefaults.buttonColors(containerColor = OrangeAccent)
        ) {
            if (isLoading) CircularProgressIndicator(color = Color.White, modifier = Modifier.size(24.dp))
            else Text("Войти", fontSize = 18.sp, fontWeight = FontWeight.Bold)
        }

        Spacer(Modifier.height(16.dp))
        TextButton(onClick = onNavigateToRegister) {
            Text("Нет аккаунта? Зарегистрироваться", color = OrangeAccent)
        }
    }
}