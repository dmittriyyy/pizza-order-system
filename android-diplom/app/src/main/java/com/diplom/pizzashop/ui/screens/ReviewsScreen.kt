package com.diplom.pizzashop.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.lifecycle.viewmodel.compose.viewModel
import com.diplom.pizzashop.ui.theme.DarkBackground
import com.diplom.pizzashop.ui.theme.GlassSurface
import com.diplom.pizzashop.ui.theme.OrangeAccent
import com.diplom.pizzashop.ui.theme.TextSecondary
import com.diplom.pizzashop.ui.theme.TextWhite
import com.diplom.pizzashop.ui.viewmodels.ReviewsViewModel
import java.time.OffsetDateTime
import java.time.format.DateTimeFormatter
import java.util.Locale

@Composable
fun ReviewsScreen(
    viewModel: ReviewsViewModel = viewModel(),
    onBack: () -> Unit
) {
    LaunchedEffect(Unit) {
        viewModel.loadReviews()
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(DarkBackground)
            .padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        Row(
            modifier = Modifier.fillMaxWidth(),
            verticalAlignment = Alignment.CenterVertically
        ) {
            IconButton(onClick = onBack) {
                Icon(Icons.Default.ArrowBack, contentDescription = "Назад", tint = TextWhite)
            }
            Spacer(Modifier.width(8.dp))
            Text("Отзывы", color = TextWhite, fontSize = 24.sp, fontWeight = FontWeight.Bold)
        }

        when {
            viewModel.isLoading -> {
                CircularProgressIndicator(color = OrangeAccent)
            }

            viewModel.reviews.isEmpty() -> {
                Text("Пока нет публичных отзывов.", color = TextSecondary)
            }

            else -> {
                LazyColumn(verticalArrangement = Arrangement.spacedBy(12.dp)) {
                    items(viewModel.reviews) { review ->
                        Card(
                            modifier = Modifier.fillMaxWidth(),
                            shape = RoundedCornerShape(20.dp),
                            colors = CardDefaults.cardColors(containerColor = GlassSurface)
                        ) {
                            Column(
                                modifier = Modifier.padding(16.dp),
                                verticalArrangement = Arrangement.spacedBy(8.dp)
                            ) {
                                Row(
                                    modifier = Modifier.fillMaxWidth(),
                                    horizontalArrangement = Arrangement.SpaceBetween
                                ) {
                                    Text(stars(review.rating), color = OrangeAccent, fontSize = 16.sp, fontWeight = FontWeight.Bold)
                                    Text("Заказ #${review.order_id}", color = TextSecondary, fontSize = 12.sp)
                                }
                                Text(
                                    review.comment ?: "Клиент оставил высокую оценку без комментария.",
                                    color = TextWhite,
                                    fontSize = 14.sp
                                )
                                Text(formatDate(review.created_at), color = TextSecondary, fontSize = 12.sp)
                            }
                        }
                    }
                }
            }
        }
    }
}

private fun stars(rating: Int): String = "★".repeat(rating) + "☆".repeat(5 - rating)

private fun formatDate(value: String): String {
    return try {
        val parsed = OffsetDateTime.parse(value)
        parsed.format(DateTimeFormatter.ofPattern("d MMMM yyyy", Locale("ru")))
    } catch (_: Exception) {
        value
    }
}
