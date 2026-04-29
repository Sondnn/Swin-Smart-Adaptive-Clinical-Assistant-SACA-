package com.saca.smartadaptiveclinicalassistant.presentation.triage_form

import android.util.Log
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.res.stringResource
import com.saca.smartadaptiveclinicalassistant.R
import com.saca.smartadaptiveclinicalassistant.presentation.components.FormQuestionOption
import com.saca.smartadaptiveclinicalassistant.presentation.components.FormQuestionScaffold
import org.koin.androidx.compose.koinViewModel

@Composable
fun GenderQuestionScreen(
    onBackClick: () -> Unit,
    onContinueClick: () -> Unit,
    modifier: Modifier = Modifier,
    triageFormViewModel: TriageFormViewModel = koinViewModel(),
) {
    Log.d("GenderScreen", "GenderScreen")
    val genderOptions = TriageFormViewModel.GenderOption.entries.map {
        FormQuestionOption(
            id = it.value,
            labelResourceId = it.labelRes
        )
    }

    FormQuestionScaffold(
        appBarTitle = stringResource(R.string.triage_form_action_bar_title),
        questionTitle = stringResource(R.string.triage_form_gender_title),
        backButtonText = stringResource(R.string.triage_form_back_button),
        continueButtonText = stringResource(R.string.triage_form_continue_button),
        backContentDescription = stringResource(R.string.app_bar_button_back_content_description),
        options = genderOptions,
        selectedOptionId = triageFormViewModel.selectedGenderOptionId,
        currentStep = 1,
        totalSteps = 5,
        onBackClick = onBackClick,
        onOptionClick = triageFormViewModel::onGenderOptionSelected,
        onContinueClick = onContinueClick,
        modifier = modifier,
    )
}