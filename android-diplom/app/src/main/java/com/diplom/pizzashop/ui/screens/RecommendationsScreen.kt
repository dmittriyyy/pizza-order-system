package com.diplom.pizzashop.ui.screens

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Scaffold
import androidx.compose.material3.SnackbarHost
import androidx.compose.material3.SnackbarHostState
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import coil.compose.AsyncImage
import com.diplom.pizzashop.data.api.RecommendationSuggestion
import com.diplom.pizzashop.data.model.Product
import com.diplom.pizzashop.ui.theme.DarkBackground
import com.diplom.pizzashop.ui.theme.DarkCardBackground
import com.diplom.pizzashop.ui.theme.GlassSurface
import com.diplom.pizzashop.ui.theme.OrangeAccent
import com.diplom.pizzashop.ui.theme.TextSecondary
import com.diplom.pizzashop.ui.theme.TextWhite
import kotlinx.coroutines.launch

private data class RecommendationCardUi(
    val productId: Int,
    val name: String,
    val reason: String,
    val price: Double?,
    val imageUrl: String?
)

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun RecommendationsScreen(
    isLoading: Boolean,
    message: String,
    suggestions: List<RecommendationSuggestion>,
    productsById: Map<Int, Product>,
    onBack: () -> Unit,
    onAddToCart: (Int) -> Unit
) {
    val snackbarHostState = remember { SnackbarHostState() }
    val scope = rememberCoroutineScope()
    val cards = suggestions.take(3).map { suggestion ->
        val product = productsById[suggestion.product_id]
        RecommendationCardUi(
            productId = suggestion.product_id,
            name = suggestion.name,
            reason = suggestion.reason,
            price = product?.price,
            imageUrl = product?.image_url
        )
    }

    Scaffold(
        containerColor = DarkBackground,
        snackbarHost = { SnackbarHost(snackbarHostState) },
        topBar = {
            Surface(color = DarkBackground) {
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(horizontal = 8.dp, vertical = 12.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    IconButton(onClick = onBack) {
                        Icon(
                            imageVector = Icons.AutoMirrored.Filled.ArrowBack,
                            contentDescription = "Назад",
                            tint = TextWhite
                        )
                    }
                    Spacer(Modifier.width(8.dp))
                    Text(
                        text = "AI рекомендации",
                        color = TextWhite,
                        style = MaterialTheme.typography.titleLarge,
                        fontWeight = FontWeight.Bold
                    )
                }
            }
        }
    ) { paddingValues ->
        if (isLoading) {
            Box(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(paddingValues),
                contentAlignment = Alignment.Center
            ) {
                CircularProgressIndicator(color = OrangeAccent)
            }
        } else {
            LazyColumn(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(paddingValues),
                contentPadding = PaddingValues(16.dp),
                verticalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                item {
                    Card(
                        shape = RoundedCornerShape(24.dp),
                        colors = CardDefaults.cardColors(containerColor = GlassSurface)
                    ) {
                        Column(
                            modifier = Modifier.padding(18.dp),
                            verticalArrangement = Arrangement.spacedBy(8.dp)
                        ) {
                            Text(
                                text = "Для вас",
                                color = OrangeAccent,
                                fontWeight = FontWeight.SemiBold,
                                fontSize = 12.sp
                            )
                            Text(
                                text = message,
                                color = TextWhite,
                                fontSize = 15.sp
                            )
                        }
                    }
                }

                if (cards.isEmpty()) {
                    item {
                        Card(
                            shape = RoundedCornerShape(24.dp),
                            colors = CardDefaults.cardColors(containerColor = GlassSurface)
                        ) {
                            Text(
                                text = "Сейчас персональные рекомендации недоступны.",
                                color = TextSecondary,
                                modifier = Modifier.padding(18.dp)
                            )
                        }
                    }
                } else {
                    items(cards) { item ->
                        Card(
                            shape = RoundedCornerShape(24.dp),
                            colors = CardDefaults.cardColors(containerColor = GlassSurface)
                        ) {
                            Column(
                                modifier = Modifier.padding(14.dp),
                                verticalArrangement = Arrangement.spacedBy(12.dp)
                            ) {
                                if (!item.imageUrl.isNullOrBlank()) {
                                    AsyncImage(
                                        model = if (item.imageUrl.startsWith("http")) item.imageUrl else "http://10.0.2.2:8000${item.imageUrl}",
                                        contentDescription = item.name,
                                        contentScale = ContentScale.Crop,
                                        modifier = Modifier
                                            .fillMaxWidth()
                                            .height(180.dp)
                                            .clip(RoundedCornerShape(18.dp))
                                    )
                                }

                                Text(
                                    text = item.name,
                                    color = TextWhite,
                                    fontSize = 22.sp,
                                    fontWeight = FontWeight.Bold,
                                    maxLines = 1,
                                    overflow = TextOverflow.Ellipsis
                                )
                                Text(
                                    text = item.reason,
                                    color = TextSecondary,
                                    fontSize = 14.sp
                                )
                                Row(
                                    modifier = Modifier.fillMaxWidth(),
                                    horizontalArrangement = Arrangement.SpaceBetween,
                                    verticalAlignment = Alignment.CenterVertically
                                ) {
                                    Text(
                                        text = item.price?.let { "${it.toInt()} ₽" } ?: "",
                                        color = OrangeAccent,
                                        fontSize = 26.sp,
                                        fontWeight = FontWeight.Bold
                                    )
                                    Button(
                                        onClick = {
                                            onAddToCart(item.productId)
                                            scope.launch {
                                                snackbarHostState.showSnackbar("${item.name} добавлен в корзину")
                                            }
                                        },
                                        shape = RoundedCornerShape(16.dp),
                                        colors = ButtonDefaults.buttonColors(containerColor = OrangeAccent)
                                    ) {
                                        Text("В корзину")
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}
