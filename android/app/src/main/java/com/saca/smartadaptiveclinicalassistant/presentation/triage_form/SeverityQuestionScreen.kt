package com.saca.smartadaptiveclinicalassistant.presentation.triage_form

import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.res.stringResource
import com.saca.smartadaptiveclinicalassistant.R
import com.saca.smartadaptiveclinicalassistant.presentation.components.AppButtonStyle
import com.saca.smartadaptiveclinicalassistant.presentation.components.form.FormQuestionOption
import com.saca.smartadaptiveclinicalassistant.presentation.components.form.FormQuestionScaffold
import com.saca.smartadaptiveclinicalassistant.presentation.session.SessionViewModel
import org.koin.androidx.compose.koinViewModel

@Composable
fun SeverityQuestionScreen(
    onBackClick: () -> Unit,
    onCancelClick: () -> Unit,
    onContinueClick: () -> Unit,
    modifier: Modifier = Modifier,
    triageFormViewModel: TriageFormViewModel = koinViewModel(),
    sessionViewModel: SessionViewModel = koinViewModel(),
) {
    val options = TriageFormViewModel.SeverityOption.entries.map {
        FormQuestionOption(
            id = it.value,
            labelResourceId = it.labelRes
        )
    }

    FormQuestionScaffold(
        appBarTitle = stringResource(R.string.triage_form_action_bar_title),
        questionTitle = stringResource(R.string.triage_form_severity_title),
        backButtonText = stringResource(R.string.triage_form_back_button),
        continueButtonText = stringResource(R.string.triage_form_continue_button),
        options = options,
        selectedOptionId = triageFormViewModel.selectedSeverityOptionId,
        currentStep = 4,
        totalSteps = 8,
        onBackClick = onBackClick,
        onCancelClick = onCancelClick,
        onOptionClick = triageFormViewModel::onSeverityOptionSelected,
        onContinueClick = onContinueClick,
        modifier = modifier,
        voiceQuestionId = TriageFormViewModel.TriageQuestionId.SEVERITY.value,
        isTranscribing = triageFormViewModel.isTranscribing,
        recordingErrorResId = triageFormViewModel.recordingErrorResId,
        onTranscribeAudio = { audioFile ->
            triageFormViewModel.transcribeAnswer(
                questionId = TriageFormViewModel.TriageQuestionId.SEVERITY.value,
                audioFile = audioFile,
                languageTag = sessionViewModel.languageTag,
            )
        },
    )
}