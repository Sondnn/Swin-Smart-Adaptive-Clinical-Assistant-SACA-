package com.saca.smartadaptiveclinicalassistant.presentation.triage_result

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.sp
import com.saca.smartadaptiveclinicalassistant.R
import com.saca.smartadaptiveclinicalassistant.domain.model.TriageForm
import com.saca.smartadaptiveclinicalassistant.ui.theme.AppBackground
import com.saca.smartadaptiveclinicalassistant.ui.theme.Brown
import org.koin.androidx.compose.koinViewModel

@Composable
fun LoadingScreen(
    formAnswers: TriageForm,
    onAnalysisSuccess: () -> Unit,
    modifier: Modifier = Modifier,
    triageResultViewModel: TriageResultViewModel = koinViewModel()
) {
    val uiState = triageResultViewModel.uiState

    LaunchedEffect(formAnswers) {
        triageResultViewModel.analyzeSymptoms(formAnswers)
    }

    LaunchedEffect(uiState) {
        if (uiState is TriageResultUIState.Success) {
            onAnalysisSuccess()
        }
    }

    Box(
        modifier = modifier
            .fillMaxSize()
            .background(AppBackground),
        contentAlignment = Alignment.Center
    ) {
        Column(
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.Center
        ) {
            Text(
                text = stringResource(R.string.triage_result_analyzing),
                color = Brown,
                fontSize = 20.sp,
                textAlign = TextAlign.Center
            )
        }
    }
}