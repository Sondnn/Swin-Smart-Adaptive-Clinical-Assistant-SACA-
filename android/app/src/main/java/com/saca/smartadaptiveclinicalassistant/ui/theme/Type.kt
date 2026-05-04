package com.saca.smartadaptiveclinicalassistant.ui.theme

import androidx.compose.material3.Typography
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.Font
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.sp
import com.saca.smartadaptiveclinicalassistant.R

val LexendFontFamily = FontFamily(
    Font(R.font.lexend_thin, FontWeight.Thin),
    Font(R.font.lexend_extra_light, FontWeight.ExtraLight),
    Font(R.font.lexend_light, FontWeight.Light),
    Font(R.font.lexend_regular, FontWeight.Normal),
    Font(R.font.lexend_medium, FontWeight.Medium),
    Font(R.font.lexend_semi_bold, FontWeight.SemiBold),
    Font(R.font.lexend_bold, FontWeight.Bold),
    Font(R.font.lexend_extra_bold, FontWeight.ExtraBold),
    Font(R.font.lexend_black, FontWeight.Black),
)

val Typography = Typography(
    titleLarge = TextStyle(
        fontFamily = LexendFontFamily,
        fontWeight = FontWeight.Black,
        fontSize = 36.sp,
        lineHeight = 45.sp,
        letterSpacing = 0.sp
    ),
    titleMedium = TextStyle(
        fontFamily = LexendFontFamily,
        fontWeight = FontWeight.Black,
        fontSize = 28.sp,
        lineHeight = 32.sp,
        letterSpacing = 0.sp
    ),
    bodyLarge = TextStyle(
        fontFamily = LexendFontFamily,
        fontWeight = FontWeight.Bold,
        fontSize = 20.sp,
        lineHeight = 32.sp,
        letterSpacing = 0.sp
    ),
    bodyMedium = TextStyle(
        fontFamily = LexendFontFamily,
        fontWeight = FontWeight.SemiBold,
        fontSize = 20.sp,
        lineHeight = 32.sp,
        letterSpacing = 0.sp
    ),
    bodySmall = TextStyle(
        fontFamily = LexendFontFamily,
        fontWeight = FontWeight.Normal,
        fontSize = 18.sp,
        lineHeight = 32.sp,
        letterSpacing = 0.sp
    ),
    labelLarge = TextStyle(
        fontFamily = LexendFontFamily,
        fontWeight = FontWeight.SemiBold,
        fontSize = 16.sp,
        lineHeight = 24.sp,
        letterSpacing = 0.sp
    ),
)