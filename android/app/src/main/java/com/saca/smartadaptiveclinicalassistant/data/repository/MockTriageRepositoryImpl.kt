package com.saca.smartadaptiveclinicalassistant.data.repository

import com.saca.smartadaptiveclinicalassistant.data.remote.TriageApi
import com.saca.smartadaptiveclinicalassistant.data.remote.dto.AnalysisSymptomsRequest
import com.saca.smartadaptiveclinicalassistant.data.remote.dto.AnalysisSymptomsResponse
import com.saca.smartadaptiveclinicalassistant.data.remote.dto.ExtractSymptomsRequest
import com.saca.smartadaptiveclinicalassistant.data.remote.dto.ExtractSymptomsResponse
import com.saca.smartadaptiveclinicalassistant.data.remote.dto.SpeechToTextResponse
import com.saca.smartadaptiveclinicalassistant.domain.repository.TriageRepository
import java.io.File

class MockTriageRepositoryImpl: TriageRepository {
    override suspend fun speechToText(
        language: Int,
        audioFile: File
    ): Result<SpeechToTextResponse> {
        return Result.success(SpeechToTextResponse("belly pain"))
    }

    override suspend fun extractSymptoms(request: ExtractSymptomsRequest): Result<ExtractSymptomsResponse> {
        return Result.success(ExtractSymptomsResponse(symptoms = listOf("Headache", "Fever")))
    }

    override suspend fun analysisSymptoms(request: AnalysisSymptomsRequest): Result<AnalysisSymptomsResponse> {
        return Result.success(AnalysisSymptomsResponse(triageCategory = 3))
    }
}

