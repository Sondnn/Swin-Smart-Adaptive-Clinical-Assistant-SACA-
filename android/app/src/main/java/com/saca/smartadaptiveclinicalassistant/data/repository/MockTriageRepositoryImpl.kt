package com.saca.smartadaptiveclinicalassistant.data.repository

import com.saca.smartadaptiveclinicalassistant.data.remote.dto.AnalysisSymptomsRequest
import com.saca.smartadaptiveclinicalassistant.data.remote.dto.AnalysisSymptomsResponse
import com.saca.smartadaptiveclinicalassistant.data.remote.dto.ParsedResponse
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
        val parsed = when (questionId) {
            1 -> ParsedResponse(gender = 1)
            2 -> ParsedResponse(ageOver65 = 0)
            3 -> ParsedResponse(symptoms = listOf("belly_pain"))
            4 -> ParsedResponse(symptomSeverity = 2)
            5 -> ParsedResponse(symptomsDuration = 0)
            6 -> ParsedResponse(chronicConditions = listOf("hypertension"))
            8 -> ParsedResponse(hadSymptomsBefore = 1)
            9 -> ParsedResponse(hadContact = 0)
            else -> ParsedResponse()
        }

        val mockResponse = SpeechToTextV2Response(
            questionId = questionId,
            parsedResponse = parsed
        )

        return Result.success(mockResponse)
    }


    override suspend fun analysisSymptoms(request: AnalysisSymptomsRequest): Result<AnalysisSymptomsResponse> {
        return Result.success(AnalysisSymptomsResponse(triageCategory = 3))
    }
}

