package com.saca.smartadaptiveclinicalassistant.presentation.navigation

import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import com.saca.smartadaptiveclinicalassistant.presentation.home.HomeScreen
import com.saca.smartadaptiveclinicalassistant.presentation.language.LanguageScreen

@Composable
fun SacaNavGraph(modifier: Modifier = Modifier) {
    val navController = rememberNavController()

    NavHost(
        navController = navController,
        startDestination = SacaDestinations.LANGUAGE,
        modifier = modifier
    ) {
        composable(SacaDestinations.LANGUAGE) {
            LanguageScreen(
                onLanguagePicked = {
                    navController.navigate(SacaDestinations.HOME) {
                        popUpTo(SacaDestinations.LANGUAGE) {
                            inclusive = true
                        }
                    }
                }
            )
        }

        composable(SacaDestinations.HOME) {
            HomeScreen(
                onGetStarted = {
                    // start the assessment
                }
            )
        }
    }

}