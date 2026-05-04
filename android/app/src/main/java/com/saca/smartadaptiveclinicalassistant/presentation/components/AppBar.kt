package com.saca.smartadaptiveclinicalassistant.presentation.components

import androidx.annotation.DrawableRes
import androidx.compose.foundation.Image
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.saca.smartadaptiveclinicalassistant.R
import com.saca.smartadaptiveclinicalassistant.ui.theme.TextBrown

@Composable
fun AppBar(
    title: String,
    iconButton: ActionBarIconButton,
    onIconButtonClick: () -> Unit,
    iconContentDescription: String,
    modifier: Modifier = Modifier
) {
    Surface(
        color = MaterialTheme.colorScheme.surface,
        shadowElevation = 2.dp,
        modifier = modifier.fillMaxWidth()
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .height(56.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Spacer(modifier = Modifier.width(12.dp))

            IconButton(onIconButtonClick) {
                Image(
                    painter = painterResource(id = iconButton.iconResourceId),
                    contentDescription = iconContentDescription,
                    modifier = Modifier.size(24.dp)
                )
            }

            Spacer(modifier = Modifier.width(12.dp))

            Text(
                text = title,
                color = TextBrown,
                style = MaterialTheme.typography.bodyLarge,
            )
        }
    }
}

enum class ActionBarIconButton(
    @param:DrawableRes val iconResourceId: Int,
) {
    MENU(R.drawable.button_menu),
    BACK(R.drawable.button_back)
}