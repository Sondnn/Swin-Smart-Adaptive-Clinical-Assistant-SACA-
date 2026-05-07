package com.saca.smartadaptiveclinicalassistant.presentation.triage_form

import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.res.stringResource
import com.saca.smartadaptiveclinicalassistant.R
import com.saca.smartadaptiveclinicalassistant.presentation.components.form.FormQuestionOption
import com.saca.smartadaptiveclinicalassistant.presentation.components.form.FormQuestionScaffold
import org.koin.androidx.compose.koinViewModel

@Composable
fun ChronicConditionsQuestionScreen(
    onBackClick: () -> Unit,
    onCancelClick: () -> Unit,
    onContinueClick: () -> Unit,
    modifier: Modifier = Modifier,
    triageFormViewModel: TriageFormViewModel = koinViewModel(),
) {
    val options = TriageFormViewModel.ChronicConditionsOption.entries.map {
        FormQuestionOption(
            id = it.value,
            labelResourceId = it.labelRes
        )
    }

    FormQuestionScaffold(
        appBarTitle = stringResource(R.string.triage_form_action_bar_title),
        questionTitle = stringResource(R.string.triage_form_chronic_conditions_history_title),
        backButtonText = stringResource(R.string.triage_form_back_button),
        continueButtonText = stringResource(R.string.triage_form_continue_button),
        isContinueAlwaysAllowed = true,
        backContentDescription = stringResource(R.string.app_bar_button_back_content_description),
        options = options,
        selectedOptionIds = triageFormViewModel.selectedChronicConditionsOptionIds,
        currentStep = 7,
        totalSteps = 8,
        onBackClick = onBackClick,
        onOptionClick = triageFormViewModel::onChronicConditionsOptionSelected,
        onCancelClick = onCancelClick,
        onContinueClick = onContinueClick,
        modifier = modifier
    )
}