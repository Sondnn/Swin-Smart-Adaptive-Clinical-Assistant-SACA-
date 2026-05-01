package com.saca.smartadaptiveclinicalassistant.presentation.home

import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.DrawerValue
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.ModalDrawerSheet
import androidx.compose.material3.NavigationDrawerItem
import androidx.compose.material3.NavigationDrawerItemDefaults
import androidx.compose.material3.ModalNavigationDrawer
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.material3.TopAppBar
import androidx.compose.material3.rememberDrawerState
import androidx.compose.runtime.Composable
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.saca.smartadaptiveclinicalassistant.R
import com.saca.smartadaptiveclinicalassistant.common.Constants.LANGUAGE_TAG_ENGLISH
import com.saca.smartadaptiveclinicalassistant.common.Constants.LANGUAGE_TAG_WALMAJARRI
import com.saca.smartadaptiveclinicalassistant.presentation.components.ActionBarIconButton
import com.saca.smartadaptiveclinicalassistant.presentation.components.AppBar
import com.saca.smartadaptiveclinicalassistant.presentation.components.AppButton
import com.saca.smartadaptiveclinicalassistant.presentation.components.AppButtonStyle
import com.saca.smartadaptiveclinicalassistant.presentation.components.SacaDrawerContent
import com.saca.smartadaptiveclinicalassistant.presentation.session.SessionViewModel
import com.saca.smartadaptiveclinicalassistant.ui.theme.AppBackground
import com.saca.smartadaptiveclinicalassistant.ui.theme.Brown
import com.saca.smartadaptiveclinicalassistant.ui.theme.Orange
import com.saca.smartadaptiveclinicalassistant.ui.theme.TextBrown
import kotlinx.coroutines.launch
import org.koin.androidx.compose.koinViewModel

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun HomeScreen(
    onGetStarted: () -> Unit,
    homeViewModel: HomeViewModel = koinViewModel(),
    sessionViewModel: SessionViewModel = koinViewModel(),
) {
    val drawerState = rememberDrawerState(initialValue = DrawerValue.Closed)
    val coroutineScope = rememberCoroutineScope()
    val currentLanguageTag: String = sessionViewModel.languageTag

    ModalNavigationDrawer(
        drawerState = drawerState,
        drawerContent = {
            SacaDrawerContent(
                currentLanguageTag = currentLanguageTag,
                onLanguagePicked =  { tag ->
                    sessionViewModel.onLanguagePicked(tag)
                    coroutineScope.launch { drawerState.close() }
                }
            )
        }
    ) {
        Scaffold(
            topBar = {
                AppBar(
                    title = stringResource(R.string.home_action_bar_title),
                    ActionBarIconButton.MENU,
                    iconContentDescription = stringResource(R.string.home_action_bar_title),
                    onIconButtonClick = {
                        coroutineScope.launch { drawerState.open() }
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
}

@Composable
fun HomeContent(
    onGetStarted: () -> Unit,
    modifier: Modifier
) {
    Box(
        modifier = Modifier
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
            modifier = modifier
                .align(Alignment.BottomCenter)
                .fillMaxWidth()
                .padding(start = 32.dp, end = 32.dp, bottom = 60.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
        ) {
            Text(
                text = stringResource(R.string.welcome_title),
                fontWeight = FontWeight.Black,
                color = TextBrown,
                fontSize = 28.sp,
                textAlign = TextAlign.Center
            )

            Text(
                text = stringResource(R.string.welcome_body),
                fontWeight = FontWeight.SemiBold,
                color = TextBrown,
                fontSize = 16.sp,
                textAlign = TextAlign.Center
            )

            Spacer(modifier = modifier.height(8.dp))

            AppButton(
                text = stringResource(R.string.welcome_get_started),
                style = AppButtonStyle.Orange,
                onClick = onGetStarted
            )
        }
    }
}
