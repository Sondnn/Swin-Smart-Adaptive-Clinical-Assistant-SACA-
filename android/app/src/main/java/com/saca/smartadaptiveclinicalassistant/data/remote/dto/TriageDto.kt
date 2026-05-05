package com.saca.smartadaptiveclinicalassistant.data.remote.dto

import com.google.gson.annotations.SerializedName

data class SpeechToTextRequest(
    val language: Int
)

data class SpeechToTextResponse(
    @SerializedName("symptoms_description") val symptomsDescription: String
)

data class ExtractSymptomsRequest(
    val language: Int,
    @SerializedName("symptoms_description") val symptomsDescription: String,
    val symptoms: List<String>,
)

data class ExtractSymptomsResponse(
    val symptoms: List<String>
)

data class AnalysisSymptomsRequest(
    val language: Int,
    val symptoms: List<String>,
    val gender: Int,
    @SerializedName("age_is_over_65") val ageIsOver65: Int,
    @SerializedName("symptoms_severity") val symptomsSeverity: Int,
    @SerializedName("symptoms_duration") val symptomsDuration: Int?,
)

data class AnalysisSymptomsResponse(
    @SerializedName("triage_category") val triageCategory: Int
)

