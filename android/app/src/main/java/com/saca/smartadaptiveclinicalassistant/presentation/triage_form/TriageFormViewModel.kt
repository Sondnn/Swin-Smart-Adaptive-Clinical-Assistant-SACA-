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

    var selectedGenderOptionId: String? by mutableStateOf(null)
        private set

    fun onGenderOptionSelected(optionId: String) {
        selectedGenderOptionId = optionId
    }
}