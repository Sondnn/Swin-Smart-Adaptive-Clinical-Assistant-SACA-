package com.saca.smartadaptiveclinicalassistant.data.remote

import com.saca.smartadaptiveclinicalassistant.data.remote.dto.AnalysisSymptomsRequest
import com.saca.smartadaptiveclinicalassistant.data.remote.dto.AnalysisSymptomsResponse
import com.saca.smartadaptiveclinicalassistant.data.remote.dto.SpeechToTextResponse
import okhttp3.MultipartBody
import retrofit2.Response
import retrofit2.http.Body
import retrofit2.http.Multipart
import retrofit2.http.POST
import retrofit2.http.Part

interface TriageApi {
    @Multipart
    @POST("speech-to-text-page")
    suspend fun speechToText(
        @Part("language") language: Int,
        @Part("question_id") questionId: Int,
        @Part files: MultipartBody.Part
    ): Response<SpeechToTextResponse>

    @POST("predict")
    suspend fun analysisSymptoms(
        @Body request: AnalysisSymptomsRequest
    ): Response<AnalysisSymptomsResponse>
}