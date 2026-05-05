package com.saca.smartadaptiveclinicalassistant.data.repository

import android.util.Log
import com.saca.smartadaptiveclinicalassistant.data.remote.TriageApi
import com.saca.smartadaptiveclinicalassistant.data.remote.dto.AnalysisSymptomsRequest
import com.saca.smartadaptiveclinicalassistant.data.remote.dto.AnalysisSymptomsResponse
import com.saca.smartadaptiveclinicalassistant.data.remote.dto.ExtractSymptomsRequest
import com.saca.smartadaptiveclinicalassistant.data.remote.dto.ExtractSymptomsResponse
import com.saca.smartadaptiveclinicalassistant.data.remote.dto.SpeechToTextResponse
import com.saca.smartadaptiveclinicalassistant.domain.repository.TriageRepository
import okhttp3.MediaType.Companion.toMediaTypeOrNull
import okhttp3.MultipartBody
import okhttp3.RequestBody.Companion.asRequestBody
import retrofit2.Response
import java.io.File

class TriageRepositoryImpl(
    private val api: TriageApi
): TriageRepository {
    override suspend fun speechToText(
        language: Int,
        audioFile: File
    ): Result<SpeechToTextResponse> {
        return try {
            val file = audioFile.asRequestBody("audio/wav".toMediaTypeOrNull())
            Log.d("speechToText", language.toString())
            val filePart = MultipartBody.Part.createFormData("files", audioFile.name, file)

            Log.d("speechToText", "exists=${audioFile.exists()}")
            Log.d("speechToText", "name=${audioFile.name}")
            Log.d("speechToText", "path=${audioFile.absolutePath}")
            Log.d("speechToText", "size=${audioFile.length()}")

            val res: Response<SpeechToTextResponse> = api.speechToText(language, filePart)
            val responseBody: SpeechToTextResponse? = res.body()

            if (res.isSuccessful && responseBody != null) {
                Log.d("speechToText", responseBody.toString())
                Result.success(responseBody)
            } else {
                Log.d("speechToText", "failed")
                Result.failure(Exception("Speech to Text Error: ${res.code()} ${res.message()}"))
            }
        } catch (e: Exception) {
            Log.d("speechToText", e.toString())
            Result.failure(e)
        }
    }

    override suspend fun extractSymptoms(request: ExtractSymptomsRequest): Result<ExtractSymptomsResponse> {
        return try {
            Log.d("extractSymptoms", request.toString())
            val res = api.extractSymptoms(request)
            val responseBody: ExtractSymptomsResponse? = res.body()
            if (res.isSuccessful && responseBody != null) {
                Log.d("extractSymptoms", responseBody.toString())
                Result.success(responseBody)
            } else {
                Log.d("extractSymptoms", "failed")
                Result.failure(Exception("Extract Symptoms Error"))
            }
        } catch (e: Exception) {
            Log.d("extractSymptoms", e.toString())
            Result.failure(e)
        }
    }

    override suspend fun analysisSymptoms(request: AnalysisSymptomsRequest): Result<AnalysisSymptomsResponse> {
        return try {
            Log.d("analysisSymptoms", request.toString())
            val res = api.analysisSymptoms(request)
            val responseBody: AnalysisSymptomsResponse? = res.body()
            if (res.isSuccessful && responseBody != null) {
                Log.d("analysisSymptoms", responseBody.toString())
                Result.success(responseBody)
            } else {
                Result.failure(Exception("Analysis Symptoms Error"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}

