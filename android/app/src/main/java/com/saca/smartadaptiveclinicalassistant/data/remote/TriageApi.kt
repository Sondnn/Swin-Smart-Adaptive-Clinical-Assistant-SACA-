package com.saca.smartadaptiveclinicalassistant.data.remote

import com.saca.smartadaptiveclinicalassistant.data.remote.dto.AnalysisSymptomsRequest
import com.saca.smartadaptiveclinicalassistant.data.remote.dto.AnalysisSymptomsResponse
import com.saca.smartadaptiveclinicalassistant.data.remote.dto.ExtractSymptomsRequest
import com.saca.smartadaptiveclinicalassistant.data.remote.dto.ExtractSymptomsResponse
import com.saca.smartadaptiveclinicalassistant.data.remote.dto.SpeechToTextResponse
import com.saca.smartadaptiveclinicalassistant.data.remote.dto.SpeechToTextV2Response
import okhttp3.MultipartBody
import retrofit2.Response
import retrofit2.http.Body
import retrofit2.http.Multipart
import retrofit2.http.POST
import retrofit2.http.Part

interface TriageApi {
    @Multipart
    @POST("speech-to-text")
    suspend fun speechToText(
        @Part("language") language: Int,
        @Part files: MultipartBody.Part
    ): Response<SpeechToTextResponse>

    @Multipart
    @POST("speech-to-text-page")
    suspend fun speechToTextV2(
        @Part("language") language: Int,
        @Part("question_id") questionId: Int,
        @Part files: MultipartBody.Part
    ): Response<SpeechToTextV2Response>

    @POST("extract-symptoms")
    suspend fun extractSymptoms(
       @Body request: ExtractSymptomsRequest
    ): Response<ExtractSymptomsResponse>

    @POST("predict")
    suspend fun analysisSymptoms(
        @Body request: AnalysisSymptomsRequest
    ): Response<AnalysisSymptomsResponse>
}