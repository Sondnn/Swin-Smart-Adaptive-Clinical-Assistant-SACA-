package com.saca.smartadaptiveclinicalassistant.presentation.triage_form

import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.res.stringResource
import com.saca.smartadaptiveclinicalassistant.R
import com.saca.smartadaptiveclinicalassistant.presentation.components.AppButtonStyle
import com.saca.smartadaptiveclinicalassistant.presentation.components.form.FormQuestionOption
import com.saca.smartadaptiveclinicalassistant.presentation.components.form.FormQuestionScaffold
import org.koin.androidx.compose.koinViewModel

@Composable
fun DurationQuestionScreen(
    onBackClick: () -> Unit,
    onCancelClick: () -> Unit,
    onAssessClick: () -> Unit,
    modifier: Modifier = Modifier,
    triageFormViewModel: TriageFormViewModel = koinViewModel(),
) {
    val options = TriageFormViewModel.DurationOption.entries.map {
        FormQuestionOption(
            id = it.value,
            labelResourceId = it.labelRes
        )
    }

    FormQuestionScaffold(
        appBarTitle = stringResource(R.string.triage_form_action_bar_title),
        questionTitle = stringResource(R.string.triage_form_duration_title),
        backButtonText = stringResource(R.string.triage_form_back_button),
        continueButtonText = stringResource(R.string.triage_form_assess_button),
        continueButtonStyle = AppButtonStyle.Orange,
        backContentDescription = stringResource(R.string.app_bar_button_back_content_description),
        options = options,
        selectedOptionId = triageFormViewModel.selectedDurationOptionId,
        currentStep = 5,
        totalSteps = 5,
        onBackClick = onBackClick,
        onCancelClick = onCancelClick,
        onOptionClick = triageFormViewModel::onDurationOptionSelected,
        onContinueClick = onAssessClick,
        modifier = modifier,
    )
}