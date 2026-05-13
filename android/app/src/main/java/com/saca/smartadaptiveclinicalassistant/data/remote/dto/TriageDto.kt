package com.saca.smartadaptiveclinicalassistant.data.remote.dto

import com.google.gson.annotations.SerializedName

data class SpeechToTextResponse(
    @SerializedName("question_id") val questionId: Int? = null,
    @SerializedName("parsed_response") val parsedResponse: ParsedResponse? = null,
)

data class ParsedResponse(
    @SerializedName("gender") val gender: Int? = null,
    @SerializedName("age_over_65") val ageOver65: Int? = null,
    @SerializedName("symptoms") val symptoms: List<String>? = null,
    @SerializedName("symptom_severity") val symptomSeverity: Int? = null,
    @SerializedName("symptoms_duration") val symptomsDuration: Int? = null,
    @SerializedName("chronic_conditions") val chronicConditions: List<String>? = null,
    @SerializedName("had_symptoms_before") val hadSymptomsBefore: Int? = null,
    @SerializedName("had_contact") val hadContact: Int? = null,
)

data class AnalysisSymptomsRequest(
    val language: Int,
    val symptoms: List<String>,
    val gender: Int,
    @SerializedName("age_over_65") val ageIsOver65: Int,
    @SerializedName("symptom_severity") val symptomsSeverity: Int,
    @SerializedName("symptoms_duration") val symptomsDuration: Int,
    @SerializedName("chronic_conditions") val chronicConditions: List<String>,
    @SerializedName("had_symptoms_before") val hadSymptomsBefore: Int,
    @SerializedName("had_contact") val hadSickContact: Int?,
)

data class AnalysisSymptomsResponse(
    @SerializedName("triage_category") val triageCategory: Int,
    val disease: Disease?
)

data class Disease(
    @SerializedName("disease")
    val disease: String,
)