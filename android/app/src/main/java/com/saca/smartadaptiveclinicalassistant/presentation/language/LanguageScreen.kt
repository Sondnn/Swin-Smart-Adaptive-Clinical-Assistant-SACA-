package com.saca.smartadaptiveclinicalassistant.presentation.language

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Button
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.unit.dp
import com.saca.smartadaptiveclinicalassistant.R
import com.saca.smartadaptiveclinicalassistant.presentation.session.SessionViewModel
import org.koin.androidx.compose.koinViewModel

@Composable
fun LanguageScreen(
    onLanguagePicked: () -> Unit,
    sessionViewModel: SessionViewModel = koinViewModel(),
) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(24.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center,
    ) {
        Text(
            text = stringResource(R.string.language_title),
            style = MaterialTheme.typography.headlineMedium,
        )
        Spacer(modifier = Modifier.height(8.dp))
        Text(
            text = stringResource(R.string.language_subtitle),
            style = MaterialTheme.typography.bodyLarge,
        )

        Spacer(modifier = Modifier.height(24.dp))

        Button(
            onClick = {
                sessionViewModel.onLanguagePicked(LANGUAGE_TAG_ENGLISH)
                onLanguagePicked()
            },
            modifier = Modifier
                .fillMaxWidth()
                .height(64.dp),
        ) {
            Text(text = stringResource(R.string.language_option_english))
        }

        Spacer(modifier = Modifier.height(16.dp))

        Button(
            onClick = {
                sessionViewModel.onLanguagePicked(LANGUAGE_TAG_WALMAJARRI)
                onLanguagePicked()
            },
            modifier = Modifier
                .fillMaxWidth()
                .height(64.dp),
        ) {
            Text(text = stringResource(R.string.language_option_walmajarri))
        }
    }
}

private const val LANGUAGE_TAG_ENGLISH = "en"

private const val LANGUAGE_TAG_WALMAJARRI = "wmt"