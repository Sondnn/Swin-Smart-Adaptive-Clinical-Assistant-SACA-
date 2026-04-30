package com.saca.smartadaptiveclinicalassistant.presentation.triage_form

import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import androidx.lifecycle.ViewModel
import com.saca.smartadaptiveclinicalassistant.R

class TriageFormViewModel(
): ViewModel() {
    enum class GenderOption(
        val value: String,
        val labelRes: Int
    ) {
        MALE("male", R.string.triage_form_gender_option_male),
        FEMALE("female", R.string.triage_form_gender_option_female),
        PREFER_NOT_TO_SAY("prefer_not_to_say", R.string.triage_form_gender_option_prefer_not_to_say)
    }

    enum class AgeOption(
        val value: String,
        val labelRes: Int
    ) {
        OVER_OLDER_ADULT("over_older_adult", R.string.triage_form_age_option_over_older_adult),
        OLDER_ADULT_OR_YOUNGER("older_adult_or_younger", R.string.triage_form_age_option_older_adult_or_younger)
    }

    enum class SeverityOption(
        val value: String,
        val labelRes: Int
    ) {
        MILD("mild", R.string.triage_form_severity_option_mild),
        LOW("low", R.string.triage_form_severity_option_low),
        MODERATE("moderate", R.string.triage_form_severity_option_moderate),
        HIGH("high", R.string.triage_form_severity_option_high),
        SEVERE("severe", R.string.triage_form_severity_option_severe),
    }

    enum class DurationOption(
        val value: String,
        val labelRes: Int
    ) {
        LESS_THAN_DAY("less_than_day", R.string.triage_form_duration_option_less_than_day),
        MORE_THAN_DAY("more_than_day", R.string.triage_form_duration_option_more_than_day),
        UNKNOWN("unknown", R.string.triage_form_duration_option_unknown),
    }


    var selectedGenderOptionId: String? by mutableStateOf(null)
        private set

    var selectedAgeOptionId: String? by mutableStateOf(null)
        private set

    var selectedSeverityOptionId: String? by mutableStateOf(null)
        private set

    var selectedDurationOptionId: String? by mutableStateOf(null)
        private set

    fun onGenderOptionSelected(optionId: String) {
        selectedGenderOptionId = optionId
    }

    fun onAgeOptionSelected(optionId: String) {
        selectedAgeOptionId = optionId
    }

    fun onSeverityOptionSelected(optionId: String) {
        selectedSeverityOptionId = optionId
    }

    fun onDurationOptionSelected(optionId: String) {
        selectedDurationOptionId = optionId
    }
}