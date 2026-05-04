package com.saca.smartadaptiveclinicalassistant.presentation.triage_result

import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.saca.smartadaptiveclinicalassistant.domain.model.TriageForm
import com.saca.smartadaptiveclinicalassistant.domain.use_case.AnalyzeSymptomsUseCase
import kotlinx.coroutines.launch

class TriageResultViewModel(
    private val analysisSymptomsUseCase: AnalyzeSymptomsUseCase
): ViewModel() {
    var uiState: TriageResultUIState by mutableStateOf(TriageResultUIState.Idle)
    private set

    fun analyzeSymptoms(formAnswer: TriageForm) {
        if (uiState == TriageResultUIState.Loading) {
            return
        }

        uiState = TriageResultUIState.Loading

        viewModelScope.launch {
            val result = analysisSymptomsUseCase(formAnswer)

            uiState = result.fold(
                onSuccess = { triageResult ->
                    TriageResultUIState.Success(triageResult)
                },
                onFailure = { error ->
                    TriageResultUIState.Error(error.message ?: "Analysis failed")
                }
            )
        }
    }

}