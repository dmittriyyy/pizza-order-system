package com.diplom.pizzashop.ui.theme

import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.ui.graphics.Color

// App colors
val OrangeAccent = Color(0xFFFF6B00) // accent color for buttons and highlights
val DarkBackground = Color(0xFF22272F)
val GlassSurface = Color(0xFF2F3640)
val TextWhite = Color(0xFFFFFFFF)
val TextSecondary = Color(0xFF9AA5B8)
val DarkCardBackground = Color(0xFF1F262D)
val Purple = Color(0xFF8E94A6)

private val AppColorScheme = darkColorScheme(
    primary = OrangeAccent,
    secondary = Color(0xFFFF8533),
    background = DarkBackground,
    surface = GlassSurface,
    onPrimary = TextWhite,
    onBackground = TextWhite,
    onSurface = TextWhite,
    error = Color(0xFFFF6B6B)
)

@Composable
fun PizzaTheme(content: @Composable () -> Unit) {
    MaterialTheme(
        colorScheme = AppColorScheme,
        content = content
    )
}