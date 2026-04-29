package com.saca.smartadaptiveclinicalassistant.data.repository

import com.saca.smartadaptiveclinicalassistant.data.remote.dto.AnalysisSymptomsRequest
import com.saca.smartadaptiveclinicalassistant.data.remote.dto.AnalysisSymptomsResponse
import com.saca.smartadaptiveclinicalassistant.data.remote.dto.ExtractSymptomsRequest
import com.saca.smartadaptiveclinicalassistant.data.remote.dto.ExtractSymptomsResponse
import com.saca.smartadaptiveclinicalassistant.data.remote.dto.SpeechToTextResponse
import java.io.File

interface TriageRepository {
    suspend fun speechToText(language: Int, audioFile: File): Result<SpeechToTextResponse>

    suspend fun extractSymptoms(request: ExtractSymptomsRequest): Result<ExtractSymptomsResponse>

    suspend fun analysisSymptoms(request: AnalysisSymptomsRequest): Result<AnalysisSymptomsResponse>
}