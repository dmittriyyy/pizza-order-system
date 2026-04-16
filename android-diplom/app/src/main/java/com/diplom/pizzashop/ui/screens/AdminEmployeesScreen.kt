@file:OptIn(ExperimentalMaterial3Api::class)

package com.diplom.pizzashop.ui.screens

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Add
import androidx.compose.material.icons.filled.Delete
import androidx.compose.material3.*
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.runtime.*
import androidx.compose.ui.*
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.lifecycle.viewmodel.compose.viewModel
import com.diplom.pizzashop.data.model.Employee
import com.diplom.pizzashop.ui.theme.*
import com.diplom.pizzashop.ui.viewmodels.AdminEmployeesViewModel

@Composable
fun AdminEmployeesScreen(
    viewModel: AdminEmployeesViewModel = viewModel(),
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
                    Text("👥 Сотрудники", color = TextWhite, fontWeight = FontWeight.Bold, fontSize = 20.sp)
                    Text("Управление командой Piazza Pizza", color = TextSecondary, fontSize = 12.sp)
                }
                FloatingActionButton(
                    onClick = { /* TODO: open add modal */ },
                    containerColor = OrangeAccent
                ) {
                    Icon(Icons.Default.Add, contentDescription = "Add employee", tint = TextWhite)
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
                            horizontalArrangement = Arrangement.spacedBy(8.dp)
                        ) {
                            val admins = viewModel.employees.count { it.role == "admin" }
                            val cooks = viewModel.employees.count { it.role == "cook" }
                            val couriers = viewModel.employees.count { it.role == "courier" }

                            StatCard("Админы", admins.toString(), "", modifier = Modifier.weight(1f))
                            StatCard("Повара", cooks.toString(), "", modifier = Modifier.weight(1f))
                            StatCard("Курьеры", couriers.toString(), "", modifier = Modifier.weight(1f))
                            StatCard("Всего", viewModel.employees.size.toString(), "", modifier = Modifier.weight(1f))
                        }
                    }

                    // Employees
                    items(viewModel.employees) { employee ->
                        EmployeeAdminCard(employee, viewModel)
                    }
                }
            }
        }
    }
}

@Composable
fun EmployeeAdminCard(employee: Employee, viewModel: AdminEmployeesViewModel) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(16.dp),
        colors = CardDefaults.cardColors(containerColor = GlassSurface)
    ) {
        Row(modifier = Modifier.padding(16.dp)) {
            // Info
            Column(modifier = Modifier.weight(1f)) {
                Text("${employee.first_name ?: ""} ${employee.last_name ?: ""}".trim(), color = TextWhite, fontWeight = FontWeight.Bold, fontSize = 16.sp)
                Text(employee.login, color = TextSecondary, fontSize = 12.sp)
                Spacer(Modifier.height(4.dp))
                RoleBadge(employee.role)
            }

            // Actions
            Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                // Role dropdown
                var expanded by remember { mutableStateOf(false) }
                ExposedDropdownMenuBox(
                    expanded = expanded,
                    onExpandedChange = { expanded = it }
                ) {
                    OutlinedButton(
                        onClick = { },
                        modifier = Modifier.menuAnchor().width(100.dp),
                        colors = ButtonDefaults.outlinedButtonColors(contentColor = TextWhite)
                    ) {
                        Text(getRoleText(employee.role), fontSize = 12.sp)
                        ExposedDropdownMenuDefaults.TrailingIcon(expanded = expanded)
                    }
                    ExposedDropdownMenu(
                        expanded = expanded,
                        onDismissRequest = { expanded = false }
                    ) {
                        DropdownMenuItem(
                            text = { Text("Клиент") },
                            onClick = {
                                viewModel.updateEmployeeRole(employee.id, "client")
                                expanded = false
                            }
                        )
                        DropdownMenuItem(
                            text = { Text("Курьер") },
                            onClick = {
                                viewModel.updateEmployeeRole(employee.id, "courier")
                                expanded = false
                            }
                        )
                        DropdownMenuItem(
                            text = { Text("Повар") },
                            onClick = {
                                viewModel.updateEmployeeRole(employee.id, "cook")
                                expanded = false
                            }
                        )
                        DropdownMenuItem(
                            text = { Text("Админ") },
                            onClick = {
                                viewModel.updateEmployeeRole(employee.id, "admin")
                                expanded = false
                            }
                        )
                    }
                }

                // Delete
                IconButton(
                    onClick = { viewModel.deleteEmployee(employee.id) },
                    modifier = Modifier.size(32.dp)
                ) {
                    Icon(Icons.Default.Delete, contentDescription = "Delete", tint = Color.Red, modifier = Modifier.size(20.dp))
                }
            }
        }
    }
}

@Composable
fun RoleBadge(role: String) {
    val (text, color) = when (role) {
        "admin" -> "Админ" to Purple
        "cook" -> "Повар" to Color.Yellow.copy(0.7f)
        "courier" -> "Курьер" to Color.Blue.copy(0.7f)
        else -> "Клиент" to TextSecondary
    }
    Surface(
        color = color.copy(alpha = 0.2f),
        shape = RoundedCornerShape(8.dp)
    ) {
        Text(text, color = color, fontSize = 11.sp, fontWeight = FontWeight.Bold, modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp))
    }
}

fun getRoleText(role: String): String = when (role) {
    "admin" -> "Админ"
    "cook" -> "Повар"
    "courier" -> "Курьер"
    else -> "Клиент"
}