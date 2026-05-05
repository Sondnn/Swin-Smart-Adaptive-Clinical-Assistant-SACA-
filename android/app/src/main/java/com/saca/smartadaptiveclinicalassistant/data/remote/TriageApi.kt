package com.saca.smartadaptiveclinicalassistant.data.remote

import com.saca.smartadaptiveclinicalassistant.data.remote.dto.AnalysisSymptomsRequest
import com.saca.smartadaptiveclinicalassistant.data.remote.dto.AnalysisSymptomsResponse
import com.saca.smartadaptiveclinicalassistant.data.remote.dto.ExtractSymptomsRequest
import com.saca.smartadaptiveclinicalassistant.data.remote.dto.ExtractSymptomsResponse
import com.saca.smartadaptiveclinicalassistant.data.remote.dto.SpeechToTextResponse
import okhttp3.MultipartBody
import retrofit2.Response
import retrofit2.http.Body
import retrofit2.http.POST
import retrofit2.http.Part

interface TriageApi {
    @POST("speech-to-text")
    suspend fun speechToText(
        @Part("language") language: Int,
        @Part files: MultipartBody.Part
    ): Response<SpeechToTextResponse>

    @POST("extract-symptoms")
    suspend fun extractSymptoms(
       @Body request: ExtractSymptomsRequest
    ): Response<ExtractSymptomsResponse>

    @POST("analysis-symptoms")
    suspend fun analysisSymptoms(
        @Body request: AnalysisSymptomsRequest
    ): Response<AnalysisSymptomsResponse>
}