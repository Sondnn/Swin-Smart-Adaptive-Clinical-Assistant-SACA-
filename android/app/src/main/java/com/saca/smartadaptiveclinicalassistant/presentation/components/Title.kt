package com.saca.smartadaptiveclinicalassistant.presentation.components

import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.text.style.TextAlign
import com.saca.smartadaptiveclinicalassistant.ui.theme.TextBrown


@Composable
fun Title(
    text: String
) {
    Text(
        text = text,
        color = TextBrown,
        style = MaterialTheme.typography.titleMedium,
        textAlign = TextAlign.Center
    )
}