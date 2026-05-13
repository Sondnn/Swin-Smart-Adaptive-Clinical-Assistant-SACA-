package com.saca.smartadaptiveclinicalassistant.domain.model

data class TriageResult(
    val triageCategory: TriageCategory,
    val symptoms: List<String>,
    val possibleCondition: String?
)
