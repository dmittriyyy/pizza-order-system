package com.diplom.pizzashop.ui.screens

import androidx.compose.foundation.*
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.ui.*
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.lifecycle.viewmodel.compose.viewModel
import com.diplom.pizzashop.data.api.CreateOrderRequest
import com.diplom.pizzashop.ui.theme.*
import com.diplom.pizzashop.ui.viewmodels.AuthViewModel
import com.diplom.pizzashop.ui.viewmodels.CartViewModel

@Composable
fun CheckoutScreen(
    cartViewModel: CartViewModel = viewModel(),
    authViewModel: AuthViewModel = viewModel(),
    onBack: () -> Unit,
    onSuccess: () -> Unit
) {
    var address by rememberSaveable { mutableStateOf("") }
    var comment by rememberSaveable { mutableStateOf("") }
    var deliveryTime by rememberSaveable { mutableStateOf("") }
    var name by rememberSaveable { mutableStateOf("") }
    var phone by rememberSaveable { mutableStateOf("") }
    var isLoading by remember { mutableStateOf(false) }
    var error by remember { mutableStateOf<String?>(null) }

    val userFullName = listOfNotNull(authViewModel.firstName, authViewModel.lastName)
        .filter { it.isNotBlank() }
        .joinToString(" ")

    LaunchedEffect(authViewModel.isAuthenticated, authViewModel.defaultAddress, userFullName, authViewModel.phone) {
        if (address.isBlank() && !authViewModel.defaultAddress.isNullOrBlank()) {
            address = authViewModel.defaultAddress!!
        }
        if (name.isBlank() && userFullName.isNotBlank()) {
            name = userFullName
        }
        if (phone.isBlank() && !authViewModel.phone.isNullOrBlank()) {
            phone = authViewModel.phone!!
        }
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(DarkBackground)
    ) {
        // Header
        Surface(color = GlassSurface, modifier = Modifier.padding(bottom = 1.dp)) {
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(16.dp),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                IconButton(onClick = onBack) {
                    Icon(Icons.Default.ArrowBack, contentDescription = "Назад", tint = TextWhite)
                }
                Text("📦 Оформление заказа", color = TextWhite, fontWeight = FontWeight.Bold, fontSize = 18.sp)
                Spacer(Modifier.width(48.dp)) // Для баланса
            }
        }

        // Form Content
        Column(
            modifier = Modifier
                .weight(1f)
                .padding(16.dp)
                .verticalScroll(rememberScrollState()),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            // Address Input
            OutlinedTextField(
                value = address,
                onValueChange = { address = it },
                label = { Text("Адрес доставки *", color = TextSecondary) },
                modifier = Modifier.fillMaxWidth(),
                leadingIcon = { Icon(Icons.Default.LocationOn, contentDescription = null, tint = OrangeAccent) },
                colors = OutlinedTextFieldDefaults.colors(
                    focusedBorderColor = OrangeAccent,
                    unfocusedBorderColor = TextSecondary.copy(0.3f)
                )
            )

            // Comment Input
            OutlinedTextField(
                value = comment,
                onValueChange = { comment = it },
                label = { Text("Комментарий к заказу", color = TextSecondary) },
                modifier = Modifier.fillMaxWidth().height(100.dp),
                leadingIcon = { Icon(Icons.Default.Comment, contentDescription = null, tint = OrangeAccent) },
                colors = OutlinedTextFieldDefaults.colors(
                    focusedBorderColor = OrangeAccent,
                    unfocusedBorderColor = TextSecondary.copy(0.3f)
                )
            )

            // Delivery Time Input
            OutlinedTextField(
                value = deliveryTime,
                onValueChange = { deliveryTime = it },
                label = { Text("Желаемое время доставки", color = TextSecondary) },
                modifier = Modifier.fillMaxWidth(),
                leadingIcon = { Icon(Icons.Default.AccessTime, contentDescription = null, tint = OrangeAccent) },
                colors = OutlinedTextFieldDefaults.colors(
                    focusedBorderColor = OrangeAccent,
                    unfocusedBorderColor = TextSecondary.copy(0.3f)
                )
            )

            Divider(color = TextSecondary.copy(0.2f))

            // Name Input
            OutlinedTextField(
                value = name,
                onValueChange = { name = it },
                label = { Text("Имя получателя", color = TextSecondary) },
                modifier = Modifier.fillMaxWidth(),
                leadingIcon = { Icon(Icons.Default.Person, contentDescription = null, tint = OrangeAccent) },
                colors = OutlinedTextFieldDefaults.colors(
                    focusedBorderColor = OrangeAccent,
                    unfocusedBorderColor = TextSecondary.copy(0.3f)
                )
            )

            // Phone Input
            OutlinedTextField(
                value = phone,
                onValueChange = { phone = it },
                label = { Text("Телефон", color = TextSecondary) },
                modifier = Modifier.fillMaxWidth(),
                leadingIcon = { Icon(Icons.Default.Phone, contentDescription = null, tint = OrangeAccent) },
                keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Phone),
                colors = OutlinedTextFieldDefaults.colors(
                    focusedBorderColor = OrangeAccent,
                    unfocusedBorderColor = TextSecondary.copy(0.3f)
                )
            )

            if (error != null) {
                Text(error!!, color = Color.Red, fontSize = 14.sp)
            }
        }

        // Footer with Total & Button
        Surface(color = GlassSurface, modifier = Modifier.padding(16.dp), shape = RoundedCornerShape(24.dp)) {
            Column(modifier = Modifier.padding(16.dp)) {
                Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                    Text("Итого:", color = TextSecondary, fontSize = 16.sp)
                    Text("${cartViewModel.total.toInt()} ₽", color = OrangeAccent, fontWeight = FontWeight.Bold, fontSize = 24.sp)
                }
                Spacer(Modifier.height(12.dp))
                Button(
                    onClick = {
                        if (address.isBlank()) {
                            error = "Укажите адрес доставки"
                            return@Button
                        }

                        isLoading = true
                        error = null
                        cartViewModel.createOrder(
                            CreateOrderRequest(
                                delivery_address = address,
                                delivery_comment = comment.ifBlank { null },
                                delivery_time = deliveryTime.ifBlank { null },
                                customer_name = name.ifBlank { null },
                                customer_phone = phone.ifBlank { null },
                                order_comment = comment.ifBlank { null }
                            ),
                            onSuccess = {
                                isLoading = false
                                onSuccess()
                            },
                            onError = { message ->
                                isLoading = false
                                error = message
                            }
                        )
                    },
                    colors = ButtonDefaults.buttonColors(containerColor = OrangeAccent),
                    shape = RoundedCornerShape(16.dp),
                    modifier = Modifier.fillMaxWidth().height(50.dp),
                    enabled = !isLoading
                ) {
                    if (isLoading) {
                        CircularProgressIndicator(color = Color.White, modifier = Modifier.size(24.dp))
                    } else {
                        Text("Оформить заказ", fontSize = 16.sp, fontWeight = FontWeight.Bold)
                    }
                }
            }
        }
    }
}