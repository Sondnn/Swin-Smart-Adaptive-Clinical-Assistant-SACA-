package com.saca.smartadaptiveclinicalassistant.data.repository

import com.saca.smartadaptiveclinicalassistant.data.remote.TriageApi
import com.saca.smartadaptiveclinicalassistant.data.remote.dto.AnalysisSymptomsRequest
import com.saca.smartadaptiveclinicalassistant.data.remote.dto.AnalysisSymptomsResponse
import com.saca.smartadaptiveclinicalassistant.data.remote.dto.ExtractSymptomsRequest
import com.saca.smartadaptiveclinicalassistant.data.remote.dto.ExtractSymptomsResponse
import com.saca.smartadaptiveclinicalassistant.data.remote.dto.SpeechToTextResponse
import okhttp3.MediaType.Companion.toMediaTypeOrNull
import okhttp3.MultipartBody
import okhttp3.RequestBody.Companion.asRequestBody
import retrofit2.Response
import java.io.File

class TriageRepositoryImpl(
    private val api: TriageApi
) : TriageRepository {
    override suspend fun speechToText(
        language: Int,
        audioFile: File
    ): Result<SpeechToTextResponse> {
        return try {
            val file = audioFile.asRequestBody("audio/wav".toMediaTypeOrNull())
            val filePart = MultipartBody.Part.createFormData("files", audioFile.name, file)
            val res: Response<SpeechToTextResponse> = api.speechToText(language, filePart)
            val responseBody: SpeechToTextResponse? = res.body()
            if (responseBody != null) {
                Result.success(responseBody)
            } else {
                Result.failure(Exception("Speech to Text Error"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    override suspend fun extractSymptoms(request: ExtractSymptomsRequest): Result<ExtractSymptomsResponse> {
        return try {
            val res = api.extractSymptoms(request)
            if (res.isSuccessful && res.body() != null) {
                Result.success(res.body()!!)
            } else {
                Result.failure(Exception("Extract Symptoms Error"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    override suspend fun analysisSymptoms(request: AnalysisSymptomsRequest): Result<AnalysisSymptomsResponse> {
        return try {
            val res = api.analysisSymptoms(request)
            if (res.isSuccessful && res.body() != null) {
                Result.success(res.body()!!)
            } else {
                Result.failure(Exception("Analysis Symptoms Error"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}

