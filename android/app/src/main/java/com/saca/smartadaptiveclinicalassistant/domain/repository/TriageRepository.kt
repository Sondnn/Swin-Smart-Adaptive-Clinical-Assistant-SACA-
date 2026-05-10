package com.saca.smartadaptiveclinicalassistant.domain.repository

import com.saca.smartadaptiveclinicalassistant.data.remote.dto.AnalysisSymptomsRequest
import com.saca.smartadaptiveclinicalassistant.data.remote.dto.AnalysisSymptomsResponse
import com.saca.smartadaptiveclinicalassistant.data.remote.dto.SpeechToTextResponse
import com.saca.smartadaptiveclinicalassistant.data.remote.dto.SpeechToTextV2Response
import java.io.File

interface TriageRepository {
    suspend fun speechToText(language: Int, audioFile: File): Result<SpeechToTextResponse>
    suspend fun speechToTextV2(language: Int, questionId: Int, audioFile: File): Result<SpeechToTextV2Response>
    suspend fun analysisSymptoms(request: AnalysisSymptomsRequest): Result<AnalysisSymptomsResponse>
}