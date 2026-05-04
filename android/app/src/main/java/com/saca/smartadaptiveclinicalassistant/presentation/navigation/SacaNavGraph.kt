package com.saca.smartadaptiveclinicalassistant.presentation.navigation

import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import com.saca.smartadaptiveclinicalassistant.domain.model.TriageForm
import com.saca.smartadaptiveclinicalassistant.presentation.home.HomeScreen
import com.saca.smartadaptiveclinicalassistant.presentation.language.LanguageScreen
import com.saca.smartadaptiveclinicalassistant.presentation.result.ResultScreen
import com.saca.smartadaptiveclinicalassistant.presentation.session.SessionViewModel
import com.saca.smartadaptiveclinicalassistant.presentation.triage_form.AgeQuestionScreen
import com.saca.smartadaptiveclinicalassistant.presentation.triage_form.DurationQuestionScreen
import com.saca.smartadaptiveclinicalassistant.presentation.triage_form.GenderQuestionScreen
import com.saca.smartadaptiveclinicalassistant.presentation.triage_form.SeverityQuestionScreen
import com.saca.smartadaptiveclinicalassistant.presentation.triage_form.SymptomQuestionScreen
import com.saca.smartadaptiveclinicalassistant.presentation.triage_form.TriageFormViewModel
import com.saca.smartadaptiveclinicalassistant.presentation.triage_result.LoadingScreen
import com.saca.smartadaptiveclinicalassistant.presentation.triage_result.TriageResultViewModel
import org.koin.androidx.compose.koinViewModel

@Composable
fun SacaNavGraph(modifier: Modifier = Modifier) {
    val navController = rememberNavController()
    val triageFormViewModel: TriageFormViewModel = koinViewModel()
    val sessionViewModel: SessionViewModel = koinViewModel()
    val triageResultViewModel: TriageResultViewModel = koinViewModel()

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
                onCancelClick = {
                    triageFormViewModel.resetFormState()
                    navController.navigate(SacaDestinations.HOME) {
                        popUpTo(SacaDestinations.HOME) {
                            inclusive = false
                        }
                        launchSingleTop = true
                    }
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
                onCancelClick = {
                    triageFormViewModel.resetFormState()
                    navController.navigate(SacaDestinations.HOME) {
                        popUpTo(SacaDestinations.HOME) {
                            inclusive = false
                        }
                        launchSingleTop = true
                    }
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
                onCancelClick = {
                    triageFormViewModel.resetFormState()
                    navController.navigate(SacaDestinations.HOME) {
                        popUpTo(SacaDestinations.HOME) {
                            inclusive = false
                        }
                        launchSingleTop = true
                    }
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
                onCancelClick = {
                    triageFormViewModel.resetFormState()
                    navController.navigate(SacaDestinations.HOME) {
                        popUpTo(SacaDestinations.HOME) {
                            inclusive = false
                        }
                        launchSingleTop = true
                    }
                },
                triageFormViewModel = triageFormViewModel
            )
        }

        composable(SacaDestinations.TRIAGE_FORM_DURATION) {
            DurationQuestionScreen(
                onBackClick = {
                    navController.popBackStack()
                },
                onAssessClick = {
                    navController.navigate(SacaDestinations.TRIAGE_RESULT_LOADING)
                },
                onCancelClick = {
                    triageFormViewModel.resetFormState()
                    navController.navigate(SacaDestinations.HOME) {
                        popUpTo(SacaDestinations.HOME) {
                            inclusive = false
                        }
                        launchSingleTop = true
                    }
                },
                triageFormViewModel = triageFormViewModel,
            )
        }

        composable(SacaDestinations.TRIAGE_RESULT_LOADING) {
            LoadingScreen(
                formAnswers = triageFormViewModel.getFormAnswers(
                    languageTag = sessionViewModel.languageTag
                ),
                onAnalysisSuccess = {
                    navController.navigate(SacaDestinations.TRIAGE_RESULT) {
                        popUpTo(SacaDestinations.TRIAGE_RESULT_LOADING) {
                            inclusive = true
                        }
                    }
                },
                triageResultViewModel = triageResultViewModel
            )
        }

        composable(SacaDestinations.TRIAGE_RESULT) {
            ResultScreen(
                onOkClick = {
                    triageFormViewModel.resetFormState()
                    navController.navigate(SacaDestinations.HOME) {
                        popUpTo(SacaDestinations.HOME) {
                            inclusive = false
                        }
                        launchSingleTop = true
                    }
                },
                triageResultViewModel = triageResultViewModel
            )
        }
    }

}