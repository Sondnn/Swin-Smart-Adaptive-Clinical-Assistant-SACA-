package com.saca.smartadaptiveclinicalassistant.domain.use_case

import com.saca.smartadaptiveclinicalassistant.data.remote.dto.AnalysisSymptomsRequest
import com.saca.smartadaptiveclinicalassistant.domain.repository.TriageRepository
import com.saca.smartadaptiveclinicalassistant.domain.model.TriageCategory
import com.saca.smartadaptiveclinicalassistant.domain.model.TriageForm
import com.saca.smartadaptiveclinicalassistant.domain.model.TriageResult

@Suppress("unused")
class AnalyzeSymptomsUseCase(
    private val triageRepository: TriageRepository
) {
    suspend operator fun invoke(form: TriageForm): Result<TriageResult> {
        val request = AnalysisSymptomsRequest(
            language = form.language,
            symptoms = form.symptoms,
            gender = form.gender,
            ageIsOver65 = form.ageIsOver65,
            symptomsDuration = form.duration,
            symptomsSeverity = form.severity
        )

        return triageRepository.analysisSymptoms(request).map { response ->
            val normalizedCategory = response.triageCategory.coerceIn(1, 6)
            val triageCategory = when (normalizedCategory) {
                1 -> TriageCategory.NON_URGENT
                2 -> TriageCategory.SEMI_URGENT
                3 -> TriageCategory.MODERATE
                4 -> TriageCategory.URGENT
                5 -> TriageCategory.EMERGENCY
                6 -> TriageCategory.IMMEDIATE
                else -> null
            }

            TriageResult(
                triageCategory = triageCategory,
                symptoms = form.symptoms
            )

        }
    }
}