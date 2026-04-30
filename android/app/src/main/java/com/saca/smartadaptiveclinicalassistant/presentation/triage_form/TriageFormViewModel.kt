package com.saca.smartadaptiveclinicalassistant.presentation.triage_form

import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import androidx.lifecycle.ViewModel
import com.saca.smartadaptiveclinicalassistant.R

class TriageFormViewModel: ViewModel() {
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

    enum class SymptomOption(
        val value: String,
        val labelRes: Int,
        val iconRes: Int
    ) {
        FEVER("fever", R.string.triage_form_symptom_fever, R.drawable.ic_symptom_fever),
        DIARRHEA("diarrhea", R.string.triage_form_symptom_diarrhea, R.drawable.ic_symptom_diarrhea),
        COUGH("cough", R.string.triage_form_symptom_cough, R.drawable.ic_symptom_cough),
        VOMITING("vomiting", R.string.triage_form_symptom_vomiting, R.drawable.ic_symptom_vomiting),
        DIZZINESS("dizziness", R.string.triage_form_symptom_dizziness, R.drawable.ic_symptom_dizzy),
        RUNNY_NOSE("runny_nose", R.string.triage_form_symptom_runny_nose, R.drawable.ic_symptom_runny_nose),
        EYE_PAIN("eye_pain", R.string.triage_form_symptom_eye_pain, R.drawable.ic_symptom_eye_pain),
        SORE_THROAT("sore_throat", R.string.triage_form_symptom_sore_throat, R.drawable.ic_symptom_sore_throat),
        HEADACHE("headache", R.string.triage_form_symptom_headache, R.drawable.ic_symptom_headache),
        JOINT_PAIN("joint_pain", R.string.triage_form_symptom_joint_pain, R.drawable.ic_symptom_joint_pain),
        ABDOMINAL_PAIN("abdominal_pain", R.string.triage_form_symptom_abdominal_pain, R.drawable.ic_symptom_abdominal_pain),
        BODY_PAIN("body_pain", R.string.triage_form_symptom_body_pain, R.drawable.ic_symptom_back_pain),
    }

    var selectedGenderOptionId: String? by mutableStateOf(null)
        private set

    var selectedAgeOptionId: String? by mutableStateOf(null)
        private set

    var selectedSymptomIds: Set<String> by mutableStateOf(emptySet())
        private set

    var symptomDescriptionText: String by mutableStateOf("")
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

    fun onSymptomOptionSelected(optionId: String) {
        selectedSymptomIds = if (selectedSymptomIds.contains(optionId)) {
            selectedSymptomIds - optionId
        } else {
            selectedSymptomIds + optionId
        }
    }

    fun onSymptomDescriptionChanged(text: String) {
        symptomDescriptionText = text
    }

    fun onSeverityOptionSelected(optionId: String) {
        selectedSeverityOptionId = optionId
    }

    fun onDurationOptionSelected(optionId: String) {
        selectedDurationOptionId = optionId
    }
}