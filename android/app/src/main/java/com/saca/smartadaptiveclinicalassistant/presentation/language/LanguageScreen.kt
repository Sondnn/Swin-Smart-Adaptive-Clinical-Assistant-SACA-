package com.saca.smartadaptiveclinicalassistant.presentation.language

import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.saca.smartadaptiveclinicalassistant.R
import com.saca.smartadaptiveclinicalassistant.common.Constants.LANGUAGE_TAG_ENGLISH
import com.saca.smartadaptiveclinicalassistant.common.Constants.LANGUAGE_TAG_WALMAJARRI
import com.saca.smartadaptiveclinicalassistant.presentation.components.AppButton
import com.saca.smartadaptiveclinicalassistant.presentation.components.AppButtonStyle
import com.saca.smartadaptiveclinicalassistant.presentation.session.SessionViewModel
import com.saca.smartadaptiveclinicalassistant.ui.theme.AppBackground
import com.saca.smartadaptiveclinicalassistant.ui.theme.AppBackgroundTeal
import org.koin.androidx.compose.koinViewModel

@Composable
fun LanguageScreen(
    onLanguagePicked: () -> Unit,
    sessionViewModel: SessionViewModel = koinViewModel(),
) {
    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(AppBackgroundTeal),
    ) {
        Image(
            painter = painterResource(R.drawable.lang_foreground),
            contentDescription = null,
            contentScale = ContentScale.FillWidth,
            modifier = Modifier
                .align(Alignment.TopCenter)
                .fillMaxWidth()
        )

        Image(
            painter = painterResource(R.drawable.lang_background),
            contentDescription = null,
            contentScale = ContentScale.FillWidth,
            modifier = Modifier
                .align(Alignment.BottomCenter)
                .fillMaxWidth()
        )

        Column(
            modifier = Modifier
                .fillMaxWidth()
                .height(330.dp)
                .padding(horizontal = 28.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.Center,
        ) {
            Text(
                text = stringResource(R.string.language_title),
                color = AppBackground,
                style = MaterialTheme.typography.titleLarge,
                textAlign = TextAlign.Center
            )

            Spacer(modifier = Modifier.height(40.dp))

            Text(
                text = stringResource(R.string.language_subtitle),
                color = AppBackground,
                style = MaterialTheme.typography.titleMedium,
                fontSize = 24.sp,
            )
        }

        Column(
            modifier = Modifier
                .align(Alignment.BottomCenter)
                .fillMaxWidth()
                .padding(horizontal = 24.dp, vertical = 28.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp),
        ) {
            AppButton(
                text = stringResource(R.string.language_option_english),
                style = AppButtonStyle.Brown,
                onClick = {
                    sessionViewModel.onLanguagePicked(LANGUAGE_TAG_ENGLISH)
                    onLanguagePicked()
                }
            )

            AppButton(
                text = stringResource(R.string.language_option_walmajarri),
                style = AppButtonStyle.Brown,
                onClick = {
                    sessionViewModel.onLanguagePicked(LANGUAGE_TAG_WALMAJARRI)
                    onLanguagePicked()
                }
            )
        }
    }
}