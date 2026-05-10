package com.saca.smartadaptiveclinicalassistant.domain.use_case

import android.util.Log
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
            symptomsSeverity = form.severity,
            chronicConditions = form.chronicConditions,
            hadSymptomsBefore = form.hadSymptomsBefore,
            hadSickContact = form.hadSickContact
        )

        return triageRepository.analysisSymptoms(request).map { response ->
            Log.d("response", response.toString())
            val normalizedCategory = response.triageCategory.coerceIn(1, 6)
            val triageCategory = when (normalizedCategory) {
                1 -> TriageCategory.A
                2 -> TriageCategory.B
                3 -> TriageCategory.C
                4 -> TriageCategory.D
                5 -> TriageCategory.E
                6 -> TriageCategory.F
                else -> TriageCategory.A
            }

            TriageResult(
                triageCategory = triageCategory,
                symptoms = form.symptoms
            )

        }
    }
}