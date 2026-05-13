package com.saca.smartadaptiveclinicalassistant.presentation.home

import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import com.saca.smartadaptiveclinicalassistant.R
import com.saca.smartadaptiveclinicalassistant.common.Constants.LANGUAGE_TAG_ENGLISH
import com.saca.smartadaptiveclinicalassistant.presentation.components.AppBar
import com.saca.smartadaptiveclinicalassistant.presentation.components.AppButton
import com.saca.smartadaptiveclinicalassistant.presentation.components.AppButtonStyle
import com.saca.smartadaptiveclinicalassistant.presentation.session.SessionViewModel
import com.saca.smartadaptiveclinicalassistant.ui.theme.AppBackground
import com.saca.smartadaptiveclinicalassistant.ui.theme.TextBrown
import org.koin.androidx.compose.koinViewModel

@Composable
fun HomeScreen(
    onGetStarted: () -> Unit,
    homeViewModel: HomeViewModel = koinViewModel(),
    sessionViewModel: SessionViewModel = koinViewModel(),
) {
    val currentLanguageTag: String = sessionViewModel.languageTag
    val languageButtonText = if (currentLanguageTag == LANGUAGE_TAG_ENGLISH) {
        stringResource(R.string.language_option_walmajarri)
    } else {
        stringResource(R.string.language_option_english)
    }

    Scaffold(
        topBar = {
            AppBar(
                title = stringResource(R.string.home_action_bar_title),
                languageButtonText = languageButtonText,
                onLanguageButtonClick = {
                    sessionViewModel.toggleLanguage()
                }
            )
        }
    ) { innerPadding ->
        HomeContent(
            onGetStarted = {
                homeViewModel.onGetStartedClicked()
                onGetStarted()
            },
            modifier = Modifier.padding(innerPadding),
        )
    }
}

@Composable
fun HomeContent(
    onGetStarted: () -> Unit,
    modifier: Modifier
) {
    Box(
        modifier = modifier
            .fillMaxSize()
            .background(AppBackground),
    ) {
        Image(
            painter = painterResource(R.drawable.home_screen_welcome),
            contentDescription = null,
            contentScale = ContentScale.Fit,
            modifier = Modifier
                .align(Alignment.BottomCenter)
                .padding(bottom = 425.dp)
                .size(256.dp)
        )

        Image(
            painter = painterResource(R.drawable.home_screen_background),
            contentDescription = null,
            contentScale = ContentScale.FillWidth,
            modifier = Modifier
                .align(Alignment.BottomCenter)
                .fillMaxWidth()
        )

        Column(
            modifier = Modifier
                .align(Alignment.BottomCenter)
                .padding(vertical = 60.dp, horizontal = 60.dp)
                .fillMaxWidth(),
            horizontalAlignment = Alignment.CenterHorizontally,
        ) {
            Text(
                text = stringResource(R.string.welcome_title),
                color = TextBrown,
                style = MaterialTheme.typography.titleMedium,
                textAlign = TextAlign.Center
            )

            Spacer(modifier = Modifier.height(24.dp))

            Text(
                text = stringResource(R.string.welcome_body),
                style = MaterialTheme.typography.labelLarge,
                color = TextBrown,
                textAlign = TextAlign.Center
            )

            Spacer(modifier = Modifier.height(80.dp))

            AppButton(
                text = stringResource(R.string.welcome_get_started),
                style = AppButtonStyle.Orange,
                onClick = onGetStarted
            )

        }
    }
}
