package com.saca.smartadaptiveclinicalassistant.presentation.components.form

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.saca.smartadaptiveclinicalassistant.ui.theme.Brown
import com.saca.smartadaptiveclinicalassistant.ui.theme.Brown20

@Composable
fun ErrorMessage(text: String) {
    Box(
        modifier = Modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(4.dp))
            .background(Brown20)
            .padding(vertical = 12.dp, horizontal = 10.dp),
        contentAlignment = Alignment.Center,
    ) {
        Text(
            text = text,
            color = Brown,
            fontWeight = FontWeight.Bold,
            fontSize = 11.sp,
            lineHeight = 15.sp,
            textAlign = TextAlign.Center,
        )
    }
}