package com.saca.smartadaptiveclinicalassistant.domain.model

data class TriageForm(
    val language: Int,
    val symptoms: List<String>,
    val gender: Int,
    val ageIsOver65: Int,
    val severity: Int,
    val duration: Int,
    val chronicConditions: List<String>,
    val hadSymptomsBefore: Int,
    val hadSickContact: Int,
)
