package com.saca.smartadaptiveclinicalassistant.data.repository

import com.saca.smartadaptiveclinicalassistant.data.remote.TriageApi
import com.saca.smartadaptiveclinicalassistant.data.remote.dto.AnalysisSymptomsRequest
import com.saca.smartadaptiveclinicalassistant.data.remote.dto.AnalysisSymptomsResponse
import com.saca.smartadaptiveclinicalassistant.data.remote.dto.ExtractSymptomsRequest
import com.saca.smartadaptiveclinicalassistant.data.remote.dto.ExtractSymptomsResponse
import com.saca.smartadaptiveclinicalassistant.data.remote.dto.SpeechToTextResponse
import com.saca.smartadaptiveclinicalassistant.data.remote.dto.SpeechToTextV2Response
import com.saca.smartadaptiveclinicalassistant.domain.repository.TriageRepository
import java.io.File

class MockTriageRepositoryImpl: TriageRepository {
    override suspend fun speechToText(
        language: Int,
        audioFile: File
    ): Result<SpeechToTextResponse> {
        return Result.success(SpeechToTextResponse("belly pain"))
    }

    override suspend fun speechToTextV2(
        language: Int,
        questionId: Int,
        audioFile: File
    ): Result<SpeechToTextV2Response> {
        val mockResponse = when (questionId) {
            1 -> SpeechToTextV2Response(gender = 1)
            2 -> SpeechToTextV2Response(ageOver65 = 0)
            3 -> SpeechToTextV2Response(symptoms = "belly pain")
            4 -> SpeechToTextV2Response(symptomSeverity = 2)
            5 -> SpeechToTextV2Response(symptomsDuration = 0)
            6 -> SpeechToTextV2Response(chronicConditions = listOf("hypertension"))
            8 -> SpeechToTextV2Response(hadSymptomsBefore = 1)
            9 -> SpeechToTextV2Response(hadContact = 0)
            else -> SpeechToTextV2Response()
        }
        return Result.success(mockResponse)
    }

    override suspend fun extractSymptoms(request: ExtractSymptomsRequest): Result<ExtractSymptomsResponse> {
        return Result.success(ExtractSymptomsResponse(symptoms = listOf("Headache", "Fever")))
    }

    override suspend fun analysisSymptoms(request: AnalysisSymptomsRequest): Result<AnalysisSymptomsResponse> {
        return Result.success(AnalysisSymptomsResponse(triageCategory = 3))
    }
}

