package com.diplom.pizzashop.ui.theme

import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.ui.graphics.Color

// iOS 26 Colors
val OrangeAccent = Color(0xFFFF6B00)
val DarkBackground = Color(0xFF0F0F1A)
val GlassSurface = Color(0xFF1A1A2E)
val TextWhite = Color(0xFFFFFFFF)
val TextSecondary = Color(0xFF8899AA)

private val AppColorScheme = darkColorScheme(
    primary = OrangeAccent,
    secondary = Color(0xFFFF8533),
    background = DarkBackground,
    surface = GlassSurface,
    onPrimary = TextWhite,
    onBackground = TextWhite,
    onSurface = TextWhite,
    error = Color(0xFFFF3B30)
)

@Composable
fun PizzaTheme(content: @Composable () -> Unit) {
    MaterialTheme(
        colorScheme = AppColorScheme,
        content = content
    )
}