package com.diplom.pizzashop.ui.screens

import androidx.compose.foundation.*
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material.icons.filled.Person
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.lifecycle.viewmodel.compose.viewModel
import com.diplom.pizzashop.ui.theme.*
import com.diplom.pizzashop.ui.viewmodels.AuthViewModel

@Composable
fun ProfileScreen(
    authViewModel: AuthViewModel = viewModel(),
    onBack: () -> Unit
) {
    var email by rememberSaveable { mutableStateOf("") }
    var firstName by rememberSaveable { mutableStateOf("") }
    var lastName by rememberSaveable { mutableStateOf("") }
    var phone by rememberSaveable { mutableStateOf("") }
    var telegram by rememberSaveable { mutableStateOf("") }
    var defaultAddress by rememberSaveable { mutableStateOf("") }
    var successMessage by rememberSaveable { mutableStateOf<String?>(null) }

    val isLoading = authViewModel.isLoading
    val error = authViewModel.error

    LaunchedEffect(authViewModel.isAuthenticated, authViewModel.email, authViewModel.firstName, authViewModel.lastName, authViewModel.phone, authViewModel.telegram, authViewModel.defaultAddress) {
        if (email.isBlank()) email = authViewModel.email.orEmpty()
        if (firstName.isBlank()) firstName = authViewModel.firstName.orEmpty()
        if (lastName.isBlank()) lastName = authViewModel.lastName.orEmpty()
        if (phone.isBlank()) phone = authViewModel.phone.orEmpty()
        if (telegram.isBlank()) telegram = authViewModel.telegram.orEmpty()
        if (defaultAddress.isBlank()) defaultAddress = authViewModel.defaultAddress.orEmpty()
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(DarkBackground)
            .padding(16.dp)
            .verticalScroll(rememberScrollState()),
        verticalArrangement = Arrangement.spacedBy(18.dp)
    ) {
        Row(
            modifier = Modifier.fillMaxWidth(),
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.SpaceBetween
        ) {
            IconButton(onClick = onBack) {
                Icon(Icons.Default.ArrowBack, contentDescription = "Назад", tint = TextWhite)
            }
            Text("Профиль", color = TextWhite, fontSize = 24.sp, fontWeight = FontWeight.Bold)
            Spacer(modifier = Modifier.width(48.dp))
        }

        Card(
            modifier = Modifier.fillMaxWidth(),
            shape = RoundedCornerShape(20.dp),
            colors = CardDefaults.cardColors(containerColor = GlassSurface)
        ) {
            Column(modifier = Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(12.dp)) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Icon(Icons.Default.Person, contentDescription = null, tint = OrangeAccent, modifier = Modifier.size(32.dp))
                    Spacer(modifier = Modifier.width(12.dp))
                    Text("Личные данные", color = TextWhite, fontWeight = FontWeight.Bold, fontSize = 18.sp)
                }
                Text("Редактируйте информацию, чтобы оформить заказ быстрее.", color = TextSecondary, fontSize = 14.sp)
            }
        }

        OutlinedTextField(
            value = firstName,
            onValueChange = { firstName = it },
            label = { Text("Имя", color = TextSecondary) },
            modifier = Modifier.fillMaxWidth(),
            colors = OutlinedTextFieldDefaults.colors(
                focusedBorderColor = OrangeAccent,
                unfocusedBorderColor = TextSecondary.copy(0.3f)
            )
        )
        OutlinedTextField(
            value = lastName,
            onValueChange = { lastName = it },
            label = { Text("Фамилия", color = TextSecondary) },
            modifier = Modifier.fillMaxWidth(),
            colors = OutlinedTextFieldDefaults.colors(
                focusedBorderColor = OrangeAccent,
                unfocusedBorderColor = TextSecondary.copy(0.3f)
            )
        )
        OutlinedTextField(
            value = email,
            onValueChange = { email = it },
            label = { Text("Email", color = TextSecondary) },
            modifier = Modifier.fillMaxWidth(),
            keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Email),
            colors = OutlinedTextFieldDefaults.colors(
                focusedBorderColor = OrangeAccent,
                unfocusedBorderColor = TextSecondary.copy(0.3f)
            )
        )
        OutlinedTextField(
            value = phone,
            onValueChange = { phone = it },
            label = { Text("Телефон", color = TextSecondary) },
            modifier = Modifier.fillMaxWidth(),
            keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Phone),
            colors = OutlinedTextFieldDefaults.colors(
                focusedBorderColor = OrangeAccent,
                unfocusedBorderColor = TextSecondary.copy(0.3f)
            )
        )
        OutlinedTextField(
            value = telegram,
            onValueChange = { telegram = it },
            label = { Text("Telegram", color = TextSecondary) },
            modifier = Modifier.fillMaxWidth(),
            colors = OutlinedTextFieldDefaults.colors(
                focusedBorderColor = OrangeAccent,
                unfocusedBorderColor = TextSecondary.copy(0.3f)
            )
        )
        OutlinedTextField(
            value = defaultAddress,
            onValueChange = { defaultAddress = it },
            label = { Text("Адрес по умолчанию", color = TextSecondary) },
            modifier = Modifier.fillMaxWidth(),
            colors = OutlinedTextFieldDefaults.colors(
                focusedBorderColor = OrangeAccent,
                unfocusedBorderColor = TextSecondary.copy(0.3f)
            )
        )

        if (!error.isNullOrBlank()) {
            Text(error, color = Color.Red, fontSize = 14.sp)
        }
        if (!successMessage.isNullOrBlank()) {
            Text(successMessage!!, color = Color(0xFF4CAF50), fontSize = 14.sp)
        }

        Spacer(modifier = Modifier.height(8.dp))
        Button(
            onClick = {
                authViewModel.updateProfile(
                    email = email.ifBlank { null },
                    firstName = firstName.ifBlank { null },
                    lastName = lastName.ifBlank { null },
                    phone = phone.ifBlank { null },
                    telegram = telegram.ifBlank { null },
                    defaultAddress = defaultAddress.ifBlank { null },
                    onSuccess = {
                        successMessage = "Профиль обновлён"
                    },
                    onError = {
                        successMessage = null
                    }
                )
            },
            modifier = Modifier.fillMaxWidth().height(50.dp),
            shape = RoundedCornerShape(16.dp),
            colors = ButtonDefaults.buttonColors(containerColor = OrangeAccent),
            enabled = !isLoading
        ) {
            if (isLoading) {
                CircularProgressIndicator(color = Color.White, modifier = Modifier.size(24.dp))
            } else {
                Text("Сохранить", fontSize = 16.sp, fontWeight = FontWeight.Bold)
            }
        }
    }
}
