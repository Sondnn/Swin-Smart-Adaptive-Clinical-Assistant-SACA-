package com.saca.smartadaptiveclinicalassistant.presentation.navigation

import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import com.saca.smartadaptiveclinicalassistant.presentation.home.HomeScreen
import com.saca.smartadaptiveclinicalassistant.presentation.language.LanguageScreen
import com.saca.smartadaptiveclinicalassistant.presentation.session.SessionViewModel
import com.saca.smartadaptiveclinicalassistant.presentation.triage_form.AgeQuestionScreen
import com.saca.smartadaptiveclinicalassistant.presentation.triage_form.DurationQuestionScreen
import com.saca.smartadaptiveclinicalassistant.presentation.triage_form.GenderQuestionScreen
import com.saca.smartadaptiveclinicalassistant.presentation.triage_form.SeverityQuestionScreen
import com.saca.smartadaptiveclinicalassistant.presentation.triage_form.SymptomQuestionScreen
import com.saca.smartadaptiveclinicalassistant.presentation.triage_form.TriageFormViewModel
import org.koin.androidx.compose.koinViewModel

@Composable
fun SacaNavGraph(modifier: Modifier = Modifier) {
    val navController = rememberNavController()
    val triageFormViewModel: TriageFormViewModel = koinViewModel()

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
                    navController.navigate(SacaDestinations.TRIAGE_FORM_GENDER) {
                    }
                }
            )
        }

        composable(SacaDestinations.TRIAGE_FORM_GENDER) {
            GenderQuestionScreen(
                onBackClick = {
                    navController.popBackStack()
                },
                onContinueClick = {
                    navController.navigate(SacaDestinations.TRIAGE_FORM_AGE)
                },
                triageFormViewModel = triageFormViewModel
            )
        }

        composable(SacaDestinations.TRIAGE_FORM_AGE) {
            AgeQuestionScreen(
                onBackClick = {
                    navController.popBackStack()
                },
                onContinueClick = {
                    navController.navigate(SacaDestinations.TRIAGE_FORM_SYMPTOM)
                },
                triageFormViewModel = triageFormViewModel
            )
        }

        composable(SacaDestinations.TRIAGE_FORM_SYMPTOM) {
            SymptomQuestionScreen(
                onBackClick = {
                    navController.popBackStack()
                },
                onContinueClick = {
                    navController.navigate(SacaDestinations.TRIAGE_FORM_SEVERITY)
                },
                triageFormViewModel = triageFormViewModel
            )
        }

        composable(SacaDestinations.TRIAGE_FORM_SEVERITY) {
            SeverityQuestionScreen(
                onBackClick = {
                    navController.popBackStack()
                },
                onContinueClick = {
                    navController.navigate(SacaDestinations.TRIAGE_FORM_DURATION)
                },
                triageFormViewModel = triageFormViewModel
            )
        }

        composable(SacaDestinations.TRIAGE_FORM_DURATION) {
            DurationQuestionScreen(
                onBackClick = {
                    navController.popBackStack()
                },
                onContinueClick = {
                    navController.popBackStack()
                },
                triageFormViewModel = triageFormViewModel
            )
        }

        composable(SacaDestinations.TRIAGE_RESULT_LOADING) {
            // Todo: Triage from loading
        }

        composable(SacaDestinations.TRIAGE_RESULT) {
            // Todo: Triage from result
        }
    }

}