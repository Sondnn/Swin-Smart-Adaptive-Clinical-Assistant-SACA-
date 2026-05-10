package com.saca.smartadaptiveclinicalassistant.domain.use_case
import android.util.Log
import com.saca.smartadaptiveclinicalassistant.data.remote.dto.SpeechToTextResponse
import com.saca.smartadaptiveclinicalassistant.domain.repository.TriageRepository
import java.io.File

class SpeechToTextUseCase (
    private val triageRepository: TriageRepository
) {
    suspend operator fun invoke(
        language: Int,
        questionId: Int,
        audioFile: File
    ): Result<SpeechToTextResponse> {
        Log.d("speech-to-text",questionId.toString())
        return triageRepository.speechToText(language, questionId, audioFile)
    }
}