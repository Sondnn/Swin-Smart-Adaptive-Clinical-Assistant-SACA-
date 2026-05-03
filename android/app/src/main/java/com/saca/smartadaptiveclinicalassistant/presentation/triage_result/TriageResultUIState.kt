package com.saca.smartadaptiveclinicalassistant.presentation.triage_result

import com.saca.smartadaptiveclinicalassistant.domain.model.TriageResult

interface TriageResultUIState {
    data object Idle: TriageResultUIState
    data object Loading: TriageResultUIState
    data class Success(val triageResult: TriageResult): TriageResultUIState
    data class Error(val message: String): TriageResultUIState
}