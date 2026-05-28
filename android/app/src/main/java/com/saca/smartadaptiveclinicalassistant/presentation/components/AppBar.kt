package com.saca.smartadaptiveclinicalassistant.presentation.components

import androidx.annotation.DrawableRes
import androidx.compose.foundation.Image
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.unit.dp
import com.saca.smartadaptiveclinicalassistant.R
import com.saca.smartadaptiveclinicalassistant.ui.theme.Brown
import com.saca.smartadaptiveclinicalassistant.ui.theme.Brown40
import com.saca.smartadaptiveclinicalassistant.ui.theme.TextBrown

@Composable
fun AppBar(
    title: String,
    iconButton: ActionBarIconButton? = null,
    onIconButtonClick: (() -> Unit)? = null,
    iconContentDescription: String? = null,
    languageButtonText: String? = null,
    onLanguageButtonClick: (() -> Unit)? = null,
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

            if (iconButton != null && onIconButtonClick != null && iconContentDescription != null) {
                IconButton(onIconButtonClick) {
                    Image(
                        painter = painterResource(id = iconButton.iconResourceId),
                        contentDescription = iconContentDescription,
                        modifier = Modifier.size(24.dp)
                    )
                }
                Spacer(modifier = Modifier.width(12.dp))
            }

            Text(
                text = title,
                color = TextBrown,
                style = MaterialTheme.typography.bodyLarge,
                modifier = Modifier.weight(1f)
            )

            if (languageButtonText != null && onLanguageButtonClick != null) {
                TextButton(
                    onClick = onLanguageButtonClick,
                    colors = ButtonDefaults.textButtonColors(
                        containerColor = Brown40,
                        contentColor = Brown,
                    ),
                    modifier = Modifier.height(36.dp)
                ) {
                    Text(
                        text = languageButtonText,
                        style = MaterialTheme.typography.labelLarge,
                        color = Brown
                    )
                }
            }

            Spacer(modifier = Modifier.width(12.dp))
        }
    }
}

enum class ActionBarIconButton(
    @param:DrawableRes val iconResourceId: Int,
) {
    BACK(R.drawable.button_back)
}