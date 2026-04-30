package com.saca.smartadaptiveclinicalassistant.presentation.triage_form

import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.res.stringResource
import com.saca.smartadaptiveclinicalassistant.R
import com.saca.smartadaptiveclinicalassistant.presentation.components.FormQuestionOption
import com.saca.smartadaptiveclinicalassistant.presentation.components.FormQuestionScaffold
import org.koin.androidx.compose.koinViewModel

@Composable
fun AgeQuestionScreen(
    onBackClick: () -> Unit,
    onContinueClick: () -> Unit,
    modifier: Modifier = Modifier,
    triageFormViewModel: TriageFormViewModel = koinViewModel(),
) {
    val options = TriageFormViewModel.AgeOption.entries.map {
        FormQuestionOption(
            id = it.value,
            labelResourceId = it.labelRes
        )
    }

    FormQuestionScaffold(
        appBarTitle = stringResource(R.string.triage_form_action_bar_title),
        questionTitle = stringResource(R.string.triage_form_age_title),
        backButtonText = stringResource(R.string.triage_form_back_button),
        continueButtonText = stringResource(R.string.triage_form_continue_button),
        backContentDescription = stringResource(R.string.app_bar_button_back_content_description),
        options = options,
        selectedOptionId = triageFormViewModel.selectedAgeOptionId,
        currentStep = 2,
        totalSteps = 5,
        onBackClick = onBackClick,
        onOptionClick = triageFormViewModel::onAgeOptionSelected,
        onContinueClick = onContinueClick,
        modifier = modifier,
    )
}