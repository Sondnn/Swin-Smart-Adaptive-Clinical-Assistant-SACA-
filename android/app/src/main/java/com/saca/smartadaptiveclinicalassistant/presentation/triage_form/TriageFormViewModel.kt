package com.saca.smartadaptiveclinicalassistant.presentation.triage_form

import androidx.annotation.StringRes
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.saca.smartadaptiveclinicalassistant.R
import com.saca.smartadaptiveclinicalassistant.common.Constants.LANGUAGE_TAG_WALMAJARRI
import com.saca.smartadaptiveclinicalassistant.domain.model.TriageForm
import com.saca.smartadaptiveclinicalassistant.domain.use_case.ExtractSymptomsUseCase
import com.saca.smartadaptiveclinicalassistant.domain.use_case.SpeechToTextUseCase
import kotlinx.coroutines.launch
import java.io.File

class TriageFormViewModel(
    private val speechToTextUseCase: SpeechToTextUseCase,
    private val extractSymptomsUseCase: ExtractSymptomsUseCase
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
        OLDER_ADULT_OR_YOUNGER("older_adult_or_younger", R.string.triage_form_age_option_older_adult_or_younger),
        PREFER_NOT_TO_SAY("prefer_not_to_say", R.string.triage_form_gender_option_prefer_not_to_say)
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
        DIARRHOEA("diarrhoea", R.string.triage_form_symptom_diarrhoea, R.drawable.ic_symptom_diarrhoea),
        COUGH("cough", R.string.triage_form_symptom_cough, R.drawable.ic_symptom_cough),
        VOMITING("vomiting", R.string.triage_form_symptom_vomiting, R.drawable.ic_symptom_vomiting),
        DIZZINESS("dizziness", R.string.triage_form_symptom_dizziness, R.drawable.ic_symptom_dizzy),
        NOSEBLEED("nosebleed", R.string.triage_form_symptom_nosebleed, R.drawable.ic_symptom_nosebleed),
        EYE_PAIN("eye_pain", R.string.triage_form_symptom_eye_pain, R.drawable.ic_symptom_eye_pain),
        SORE_THROAT("sore_throat", R.string.triage_form_symptom_sore_throat, R.drawable.ic_symptom_sore_throat),
        HEADACHE("headache", R.string.triage_form_symptom_headache, R.drawable.ic_symptom_headache),
        JOINT_PAIN("joint_pain", R.string.triage_form_symptom_joint_pain, R.drawable.ic_symptom_joint_pain),
        ABDOMINAL_PAIN("abdominal_pain", R.string.triage_form_symptom_abdominal_pain, R.drawable.ic_symptom_abdominal_pain),
        BACK_PAIN("back_pain", R.string.triage_form_symptom_back_pain, R.drawable.ic_symptom_back_pain),
    }

    enum class SymptomsBeforeOption(
        val value: String,
        val labelRes: Int
    ) {
        YES("yes", R.string.triage_form_symptoms_before_option_yes),
        NO("no", R.string.triage_form_symptoms_before_option_no),
        UNKNOWN("unknown", R.string.triage_form_symptoms_before_option_unknown),
    }

    enum class ChronicConditionsOption(
        val value: String,
        val labelRes: Int
    ) {
        HYPERTENSION("hypertension", R.string.triage_form_chronic_conditions_option_hypertension),
        TYPE_2_DIABETES("type2_diabetes", R.string.triage_form_chronic_conditions_option_type2_diabetes),
        HEART_DISEASE("heart_disease", R.string.triage_form_chronic_conditions_option_heart_disease),
        ASTHMA_COPD("asthma_copd", R.string.triage_form_chronic_conditions_option_asthma_copds),
        DEPRESSION_ANXIETY("depression_anxiety", R.string.triage_form_chronic_conditions_option_depression_anxiety),
    }

    enum class SickContactHistoryOption(
        val value: String,
        val labelRes: Int
    ) {
        YES("yes", R.string.triage_form_sick_contact_history_option_yes),
        NO("no", R.string.triage_form_sick_contact_history_option_no),
        UNKNOWN("unknown", R.string.triage_form_sick_contact_history_option_unknown),
    }

    var selectedGenderOptionId: String? by mutableStateOf(null)
        private set

    var selectedAgeOptionId: String? by mutableStateOf(null)
        private set

    var isSymptomOptionsExpanded: Boolean by mutableStateOf(false)
        private set

    var selectedSymptomIds: Set<String> by mutableStateOf(emptySet())
        private set

    var symptomDescriptionText: String by mutableStateOf("")
        private set

    var isTranscribing: Boolean by mutableStateOf(false)
        private set

    var recordingErrorResId: Int? by mutableStateOf(null)
        private set

    var shouldShowSymptomError: Boolean by mutableStateOf(false)

    var isExtractingSymptoms: Boolean by mutableStateOf(false)
        private set

    var extractSymptomsErrorResId: Int? by mutableStateOf(null)
        private set

    private var extractedSymptomsFromBackend: List<String> by mutableStateOf(emptyList())

    var selectedSeverityOptionId: String? by mutableStateOf(null)
        private set

    var selectedDurationOptionId: String? by mutableStateOf(null)
        private set

    var selectedSymptomsBeforeOptionId: String? by mutableStateOf(null)
        private set

    var selectedChronicConditionsOptionIds: Set<String> by mutableStateOf(emptySet())
        private set

    var selectedSickContactHistoryOptionId: String? by mutableStateOf(null)
        private set

    fun onGenderOptionSelected(optionId: String) {
        selectedGenderOptionId = optionId
    }

    fun onAgeOptionSelected(optionId: String) {
        selectedAgeOptionId = optionId
    }

    fun onSymptomOptionsExpandClicked() {
        isSymptomOptionsExpanded = true
    }

    fun onSymptomOptionSelected(optionId: String) {
        selectedSymptomIds = if (selectedSymptomIds.contains(optionId)) {
            selectedSymptomIds - optionId
        } else {
            selectedSymptomIds + optionId
        }

        clearExtractSymptomsError()
        hideSymptomErrorIfExists()
    }

    fun onSymptomDescriptionChanged(text: String) {
        symptomDescriptionText = text

        clearRecordingError()
        clearExtractSymptomsError()
        hideSymptomErrorIfExists()
    }

    fun showRecordingError(@StringRes messageResId: Int) {
        isTranscribing = false
        recordingErrorResId = messageResId
    }

    fun clearRecordingError() {
        recordingErrorResId = null
    }

    fun clearExtractSymptomsError() {
        extractSymptomsErrorResId = null
    }

    fun hideSymptomErrorIfExists() {
        if (selectedSymptomIds.isNotEmpty() || symptomDescriptionText.isNotBlank()) {
            shouldShowSymptomError = false
        }
    }

    fun onSeverityOptionSelected(optionId: String) {
        selectedSeverityOptionId = optionId
    }

    fun onDurationOptionSelected(optionId: String) {
        selectedDurationOptionId = optionId
    }

    fun onSymptomsBeforeOptionSelected(optionId: String) {
        selectedSymptomsBeforeOptionId = optionId
    }

    fun onSickContactHistoryOptionSelected(optionId: String) {
        selectedSickContactHistoryOptionId = optionId
    }

    fun onChronicConditionsOptionSelected(optionId: String) {
        selectedChronicConditionsOptionIds = if (selectedChronicConditionsOptionIds.contains(optionId)) {
            selectedChronicConditionsOptionIds - optionId
        } else {
            selectedChronicConditionsOptionIds + optionId
        }
    }

    private fun getLanguageCode(languageTag: String): Int {
        return if (languageTag == LANGUAGE_TAG_WALMAJARRI) 0 else 1
    }

    private fun getGenderCode(): Int {
        return when (selectedGenderOptionId) {
            "male" -> 1
            "female" -> 0
            else -> 2
        }
    }

    private fun getAgeOver65Code(): Int {
        return when (selectedAgeOptionId) {
            "older_adult_or_younger" -> 0
            "over_older_adult" -> 1
            else -> 2
        }
    }

    private fun getSeverityCode(): Int {
        return when (selectedSeverityOptionId) {
            "mild" -> 1
            "low" -> 2
            "moderate" -> 3
            "high" -> 4
            "severe" -> 5
            else -> 0
        }
    }

    private fun getDurationCode(): Int {
        return when (selectedDurationOptionId) {
            "less_than_day" -> 0
            "more_than_day" -> 1
            "unknown" -> 2
            else -> 2
        }
    }


    private fun getSymptomsBeforeCode(): Int {
        return when (selectedSymptomsBeforeOptionId) {
            "no" -> 0
            "yes" -> 1
            "unknown" -> 2
            else -> 2
        }
    }

    private fun getHadSickContactCode(): Int {
        return when (selectedSickContactHistoryOptionId) {
            "no" -> 0
            "yes" -> 1
            "unknown" -> 2
            else -> 2
        }
    }

    fun transcribeRecordedAudio(audioFile: File, languageTag: String) {
        if (isTranscribing) {
            return
        }

        isTranscribing = true
        clearRecordingError()

        viewModelScope.launch {
            try {
                val result = speechToTextUseCase(
                    language = getLanguageCode(languageTag),
                    audioFile = audioFile,
                )

                result.fold(
                    onSuccess = { transcribedText ->
                        if (transcribedText.isBlank()) {
                            recordingErrorResId = R.string.triage_form_symptom_transcription_failed_message
                            return@fold
                        }

                        symptomDescriptionText += transcribedText
                    },
                    onFailure = {
                        recordingErrorResId = R.string.triage_form_symptom_transcription_failed_message
                    },
                )
            } catch (_: Exception) {
                recordingErrorResId = R.string.triage_form_symptom_transcription_failed_message
            } finally {
                isTranscribing = false
                //audioFile.delete()
            }
        }
    }

    fun canContinueFromSymptomQuestion(): Boolean {
        val hasSelectedSymptom = selectedSymptomIds.isNotEmpty()
        val hasWrittenDetails = symptomDescriptionText.isNotBlank()

        shouldShowSymptomError = !hasSelectedSymptom && !hasWrittenDetails
        return !shouldShowSymptomError
    }

    suspend fun extractSymptoms(languageTag: String): Boolean {
        if (!canContinueFromSymptomQuestion() || isExtractingSymptoms) {
            return false
        }

        isExtractingSymptoms = true

        return try {
            val result = extractSymptomsUseCase(
                language = getLanguageCode(languageTag),
                symptomsDescription = symptomDescriptionText.trim(),
                selectedSymptoms = selectedSymptomIds.toList()
            )

            result.fold(
                onSuccess = { extractedSymptoms ->
                    if (extractedSymptoms.isEmpty()) {
                        extractSymptomsErrorResId = R.string.triage_form_symptom_extract_empty_message
                        return@fold false
                    }

                    extractedSymptomsFromBackend = extractedSymptoms
                    hideSymptomErrorIfExists()
                    true
                },
                onFailure =  {
                    extractSymptomsErrorResId = R.string.triage_form_symptom_extract_failed_message
                    false
                }
            )
        } catch (_: Exception) {
            extractSymptomsErrorResId = R.string.triage_form_symptom_extract_failed_message
            false
        } finally {
            isExtractingSymptoms = false
        }
    }


    fun getFormAnswers(languageTag: String): TriageForm {
        val symptoms = extractedSymptomsFromBackend.ifEmpty {
            selectedSymptomIds.toList()
        }

        return TriageForm(
            language = getLanguageCode(languageTag),
            symptoms = symptoms,
            gender = getGenderCode(),
            ageIsOver65 = getAgeOver65Code(),
            severity = getSeverityCode(),
            duration = getDurationCode(),
            chronicConditions = selectedChronicConditionsOptionIds.toList(),
            hadSymptomsBefore = getSymptomsBeforeCode(),
            hadSickContact = getHadSickContactCode(),
        )
    }

    fun resetFormState() {
        selectedGenderOptionId = null
        selectedAgeOptionId = null
        selectedSymptomIds = emptySet()
        selectedSeverityOptionId = null
        selectedDurationOptionId = null
        selectedChronicConditionsOptionIds = emptySet()
        selectedSickContactHistoryOptionId = null
        selectedSymptomsBeforeOptionId = null
        symptomDescriptionText = ""
        isSymptomOptionsExpanded = false
        isTranscribing = false
        isExtractingSymptoms = false
        extractedSymptomsFromBackend = emptyList()
        recordingErrorResId = null
        extractSymptomsErrorResId = null
        shouldShowSymptomError = false
    }
}