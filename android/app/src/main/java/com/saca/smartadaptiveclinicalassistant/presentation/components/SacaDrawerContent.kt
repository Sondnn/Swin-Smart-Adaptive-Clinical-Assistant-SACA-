package com.saca.smartadaptiveclinicalassistant.presentation.components

import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.ModalDrawerSheet
import androidx.compose.material3.NavigationDrawerItem
import androidx.compose.material3.NavigationDrawerItemDefaults
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.saca.smartadaptiveclinicalassistant.R
import com.saca.smartadaptiveclinicalassistant.common.Constants.LANGUAGE_TAG_ENGLISH
import com.saca.smartadaptiveclinicalassistant.common.Constants.LANGUAGE_TAG_WALMAJARRI
import com.saca.smartadaptiveclinicalassistant.ui.theme.DrawerBackground
import com.saca.smartadaptiveclinicalassistant.ui.theme.TextBrown
import com.saca.smartadaptiveclinicalassistant.ui.theme.TextDarkBrown

@Composable
fun SacaDrawerContent(
    currentLanguageTag: String,
    onLanguagePicked: (String) -> Unit,
) {
    ModalDrawerSheet(
        drawerContainerColor = DrawerBackground,
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(horizontal = 16.dp, vertical = 24.dp)
        ) {
            Text(
                text = stringResource(R.string.app_name),
                style = MaterialTheme.typography.titleMedium,
                color = TextBrown,
                fontWeight = FontWeight.Black,
                lineHeight = 35.sp
            )

            Spacer(modifier = Modifier.height(16.dp))

            Row(
                modifier = Modifier.padding(horizontal = 16.dp, vertical = 14.dp),
                verticalAlignment =  Alignment.CenterVertically
            ) {
                Text(
                    text = stringResource(R.string.home_drawer_section_assessment),
                    style = MaterialTheme.typography.bodyLarge,
                    fontSize = 24.sp,
                    color = TextBrown,
                )
            }

            Spacer(modifier = Modifier.height(24.dp))

            HorizontalDivider()

            Spacer(modifier = Modifier.height(16.dp))

            Text(
                text = stringResource(R.string.home_drawer_section_language),
                style = MaterialTheme.typography.bodyMedium,
                color = TextDarkBrown,
            )

            Spacer(modifier = Modifier.height(16.dp))

            DrawerLanguageRow(
                label = stringResource(R.string.language_option_english),
                isSelected = currentLanguageTag == LANGUAGE_TAG_ENGLISH,
                onClick = { onLanguagePicked(LANGUAGE_TAG_ENGLISH) }
            )

            Spacer(modifier = Modifier.height(8.dp))

            DrawerLanguageRow(
                label = stringResource(R.string.language_option_walmajarri),
                isSelected = currentLanguageTag == LANGUAGE_TAG_WALMAJARRI,
                onClick = { onLanguagePicked(LANGUAGE_TAG_WALMAJARRI) }
            )
        }
    }
}


@Composable
private fun DrawerLanguageRow(
    label: String,
    isSelected: Boolean,
    onClick: () -> Unit,
) {
    NavigationDrawerItem(
        label = {
            Text(
                text = label,
                style = MaterialTheme.typography.bodyLarge,
                color = TextDarkBrown
            )
        },
        selected = isSelected,
        onClick = onClick,
        badge = {
            if (isSelected) {
                Text(
                    text = "\u2713",
                    color = MaterialTheme.colorScheme.primary,
                    fontSize = 18.sp,
                )
            }
        },
        colors = NavigationDrawerItemDefaults.colors(
            selectedContainerColor = Color(0xFFEEECEB)
        ),
        modifier = Modifier.fillMaxWidth(),
    )
}