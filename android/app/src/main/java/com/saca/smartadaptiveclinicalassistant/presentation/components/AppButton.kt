package com.saca.smartadaptiveclinicalassistant.presentation.components

import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.saca.smartadaptiveclinicalassistant.ui.theme.AppBackground
import com.saca.smartadaptiveclinicalassistant.ui.theme.DisabledTextBrown
import com.saca.smartadaptiveclinicalassistant.ui.theme.Brown as ColorBrown
import com.saca.smartadaptiveclinicalassistant.ui.theme.Orange as ColorOrange

@Composable
fun AppButton(
    text: String,
    onClick: () -> Unit,
    modifier: Modifier = Modifier,
    style: AppButtonStyle = AppButtonStyle.Brown,
    enabled: Boolean = true,
) {
    val buttonColors = ButtonDefaults.buttonColors(
        containerColor = style.backgroundColor,
        contentColor = style.textColor,
        disabledContainerColor = style.backgroundColor.copy(alpha = 0.45f),
        disabledContentColor = style.textColor.copy(alpha = 0.45f),
    )

    Button(
        onClick = onClick,
        enabled = enabled,
        colors = buttonColors,
        contentPadding = PaddingValues(vertical = 14.dp),
        modifier = modifier.fillMaxWidth()
    ) {
        Text(
            text = text,
            color = style.textColor,
            fontSize = 19.sp,
            fontWeight = FontWeight.Bold,
            textAlign = TextAlign.Center
        )
    }
}

enum class AppButtonStyle(
    val backgroundColor: Color,
    val textColor: Color
) {
    Brown(
        backgroundColor = ColorOrange,
        textColor = Color.White
    ),
    Orange(
        backgroundColor = ColorBrown,
        textColor = Color.White
    ),

    Transparent(
        backgroundColor = AppBackground,
        textColor = DisabledTextBrown
    )
}