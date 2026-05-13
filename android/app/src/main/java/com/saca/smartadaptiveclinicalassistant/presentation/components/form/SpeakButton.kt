package com.saca.smartadaptiveclinicalassistant.presentation.components.form

import androidx.compose.foundation.Image
import androidx.compose.foundation.gestures.detectTapGestures
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.DisposableEffect
import androidx.compose.ui.platform.LocalContext
import androidx.compose.runtime.remember
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import com.saca.smartadaptiveclinicalassistant.R
import com.saca.smartadaptiveclinicalassistant.data.local.Speaker
import com.saca.smartadaptiveclinicalassistant.ui.theme.Brown



//Box(
//modifier = Modifier
//.fillMaxWidth()
//.height(52.dp)
//.clip(RoundedCornerShape(6.dp))
//.background(buttonBgColor)
//.pointerInput(isEnabled) {
//    detectTapGestures(
//        onPress = {
//            if (isEnabled) onPress()
//        }
//    )
//}.padding(horizontal = 16.dp),
//) {
//    Text(
//        text = text,
//        color = Color.White,
//        style = MaterialTheme.typography.bodyMedium,
//        modifier = Modifier.align(Alignment.Center),
//        textAlign = TextAlign.Center
//    )
//
//
//    Image(
//        painter = painterResource(id = R.drawable.ic_mic),
//        contentDescription = text,
//        modifier = Modifier
//            .size(24.dp)
//            .align(Alignment.CenterEnd)
//    )
//}
@Composable
fun SpeakButton(
    text: String,
    onClick: () -> Unit,
    modifier: Modifier = Modifier,
) {
    Button(
        onClick = onClick,
        colors = ButtonDefaults.buttonColors(
            containerColor = Brown,
            contentColor = Color.White
        ),
        shape = RoundedCornerShape(6.dp),
        modifier = modifier
            .fillMaxWidth()
            .height(52.dp)
    ) {
        Row(
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            Image(
                painter = painterResource(id = R.drawable.ic_listen),
                contentDescription = text,
                modifier = Modifier.size(22.dp)
            )

            Text(
                text = text,
                style = MaterialTheme.typography.bodyMedium,
                color = Color.White,
                textAlign = TextAlign.Center
            )
        }
    }
}

@Composable
fun rememberSpeaker(): Speaker {
    val context = LocalContext.current
    val speaker = remember { Speaker(context) }

    DisposableEffect(speaker) {
        onDispose {
            speaker.release()
        }
    }
    return speaker
}