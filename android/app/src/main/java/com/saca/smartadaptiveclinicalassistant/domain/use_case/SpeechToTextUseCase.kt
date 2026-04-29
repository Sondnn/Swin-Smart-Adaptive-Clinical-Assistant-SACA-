package com.saca.smartadaptiveclinicalassistant.domain.use_case
import com.saca.smartadaptiveclinicalassistant.domain.repository.TriageRepository
import java.io.File

@Suppress("unused")
class SpeechToTextUseCase (
    private val triageRepository: TriageRepository
) {
    suspend operator fun invoke(
        language: Int,
        audioFile: File
    ): Result<String> {
        return triageRepository.speechToText(language, audioFile).map { response ->
            response.symptomsDescription
        }
    }
}