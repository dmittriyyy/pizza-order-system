package com.diplom.pizzashop.ui.viewmodels

import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.diplom.pizzashop.data.model.Category
import com.diplom.pizzashop.data.model.Product
import com.diplom.pizzashop.data.repository.PizzaRepository
import kotlinx.coroutines.launch

class MenuViewModel : ViewModel() {
    private val repository = PizzaRepository()

    var products by mutableStateOf<List<Product>>(emptyList())
        private set
    var categories by mutableStateOf<List<Category>>(emptyList())
        private set
    var isLoading by mutableStateOf(false)
        private set
    var error by mutableStateOf<String?>(null)
        private set
    var selectedCategory by mutableStateOf<Int?>(null)
        private set

    init {
        loadData()
    }

    fun loadData() {
        viewModelScope.launch {
            isLoading = true
            error = null
            try {
                products = repository.getProducts()
                categories = repository.getCategories()
            } catch (e: Exception) {
                error = "Ошибка загрузки: ${e.message}"
                e.printStackTrace()
            } finally {
                isLoading = false
            }
        }
    }

    fun selectCategory(categoryId: Int?) {
        selectedCategory = categoryId
    }

    val filteredProducts: List<Product>
        get() = if (selectedCategory == null) products
        else products.filter { it.category_id == selectedCategory }
}
