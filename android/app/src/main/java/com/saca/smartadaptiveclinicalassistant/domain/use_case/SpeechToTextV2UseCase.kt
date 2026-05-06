package com.saca.smartadaptiveclinicalassistant.domain.use_case

import com.saca.smartadaptiveclinicalassistant.data.remote.dto.SpeechToTextV2Response
import com.saca.smartadaptiveclinicalassistant.domain.repository.TriageRepository
import java.io.File

class SpeechToTextV2UseCase (
    private val triageRepository: TriageRepository
) {
    suspend operator fun invoke(
        language: Int,
        questionId: Int,
        audioFile: File
    ): Result<SpeechToTextV2Response> {
        return triageRepository.speechToTextV2(language, questionId, audioFile)
    }
}