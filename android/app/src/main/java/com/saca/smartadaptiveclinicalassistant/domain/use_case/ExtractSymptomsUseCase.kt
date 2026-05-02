package com.saca.smartadaptiveclinicalassistant.domain.use_case
import com.saca.smartadaptiveclinicalassistant.data.remote.dto.ExtractSymptomsRequest
import com.saca.smartadaptiveclinicalassistant.domain.repository.TriageRepository

@Suppress("unused")
class ExtractSymptomsUseCase (
    private val triageRepository: TriageRepository
) {
    suspend operator fun invoke(
        language: Int,
        symptomsDescription: String,
        selectedSymptoms: List<String>,
    ): Result<List<String>> {
        val request = ExtractSymptomsRequest(
            language = language,
            symptomsDescription = symptomsDescription,
            symptoms = selectedSymptoms
        )

        return triageRepository.extractSymptoms(request).map { response ->
            response.symptoms
        }
    }
}