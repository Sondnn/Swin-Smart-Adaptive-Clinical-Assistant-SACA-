package com.saca.smartadaptiveclinicalassistant.presentation.components.form

import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.gestures.PressGestureScope
import androidx.compose.foundation.gestures.detectTapGestures
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.input.pointer.pointerInput
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.saca.smartadaptiveclinicalassistant.R
import com.saca.smartadaptiveclinicalassistant.ui.theme.Brown

@Composable
fun RecordButton(
    text: String,
    isRecording: Boolean,
    isEnabled: Boolean,
    onPress: suspend PressGestureScope.() -> Unit
) {
    val buttonBgColor = when {
        !isEnabled -> Brown.copy(alpha = 0.45f)
        isRecording -> Brown
        else -> Brown
    }

    Row(
        modifier = Modifier
            .fillMaxWidth()
            .height(52.dp)
            .clip(RoundedCornerShape(6.dp))
            .background(buttonBgColor)
            .pointerInput(isEnabled) {
                detectTapGestures(
                    onPress = {
                        if (isEnabled) {
                            onPress()
                        }
                    }
                )
            }.padding(horizontal = 16.dp),
        verticalAlignment = Alignment.CenterVertically,
        horizontalArrangement = Arrangement.SpaceBetween,
    ) {
        Text(
            text = text,
            color = Color.White,
            style = MaterialTheme.typography.bodyMedium,
            fontWeight = FontWeight.Black,
            textAlign = TextAlign.Center
        )

        Image(
            painter = painterResource(id = R.drawable.ic_mic),
            contentDescription = text,
            modifier = Modifier.size(24.dp)
        )
    }
}
