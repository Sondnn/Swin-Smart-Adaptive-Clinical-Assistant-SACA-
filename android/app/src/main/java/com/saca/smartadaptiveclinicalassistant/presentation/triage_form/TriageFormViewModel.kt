package com.saca.smartadaptiveclinicalassistant.presentation.triage_form

import android.util.Log
import androidx.annotation.StringRes
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.saca.smartadaptiveclinicalassistant.R
import com.saca.smartadaptiveclinicalassistant.common.Constants.LANGUAGE_TAG_WALMAJARRI
import com.saca.smartadaptiveclinicalassistant.data.remote.dto.SpeechToTextResponse
import com.saca.smartadaptiveclinicalassistant.domain.model.TriageForm
import com.saca.smartadaptiveclinicalassistant.domain.use_case.SpeechToTextUseCase
import kotlinx.coroutines.launch
import java.io.File

class TriageFormViewModel(
    private val speechToTextUseCase: SpeechToTextUseCase,
): ViewModel() {
    enum class TriageQuestionId(val value: Int) {
        GENDER(1),
        AGE(2),
        SYMPTOM(3),
        SEVERITY(5),
        DURATION(6),
        SYMPTOMS_BEFORE(7),
        CHRONIC_CONDITIONS(8),
        SICK_CONTACT_HISTORY(9),
    }
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

    var recordedSymptoms: Set<String> by mutableStateOf(emptySet())
        private set

    var isTranscribing: Boolean by mutableStateOf(false)
        private set

    var recordingErrorResId: Int? by mutableStateOf(null)
        private set

    var shouldShowNoSymptomError: Boolean by mutableStateOf(false)

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

        clearRecordingError()
        hideSymptomErrorIfExists()
    }

    fun showRecordingError(@StringRes messageResId: Int) {
        isTranscribing = false
        recordingErrorResId = messageResId
    }

    fun clearRecordingError() {
        recordingErrorResId = null
    }

    fun hideSymptomErrorIfExists() {
        if (selectedSymptomIds.isNotEmpty() || recordedSymptoms.isNotEmpty()) {
            shouldShowNoSymptomError = false
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

    fun transcribeAnswer(questionId: Int, audioFile: File, languageTag: String) {
        if (isTranscribing) {
            return
        }

        isTranscribing = true
        clearRecordingError()

        viewModelScope.launch {
            try {
                val result = speechToTextUseCase(
                    language = getLanguageCode(languageTag),
                    questionId = questionId,
                    audioFile = audioFile,
                )

                result.fold(
                    onSuccess = { response ->
                        val applied = applyVoiceAnswer(questionId, response)
                        Log.d("Record success", response.toString())
                        if (!applied) {
                            recordingErrorResId = R.string.triage_form_symptom_transcription_failed_message
                        }
                    },
                    onFailure = {
                        recordingErrorResId = R.string.triage_form_symptom_transcription_failed_message
                    },
                )
            } catch (_: Exception) {
                recordingErrorResId = R.string.triage_form_symptom_transcription_failed_message
            } finally {
                isTranscribing = false
                // audioFile is stored for testing purpose, but should be deleted after recording in production
                // audioFile.delete()
            }
        }
    }

    private fun applyVoiceAnswer(questionId: Int, response: SpeechToTextResponse): Boolean {
        return when (questionId) {
            TriageQuestionId.GENDER.value -> {
                val optionId = when (response.parsedResponse?.gender) {
                    0 -> "female"
                    1 -> "male"
                    2 -> "prefer_not_to_say"
                    else -> null
                }
                if (optionId != null) {
                    selectedGenderOptionId = optionId
                    true
                } else {
                    false
                }
            }

            TriageQuestionId.AGE.value -> {
                val optionId = when (response.parsedResponse?.ageOver65) {
                    0 -> "older_adult_or_younger"
                    1 -> "over_older_adult"
                    2 -> "prefer_not_to_say"
                    else -> null
                }
                if (optionId != null) {
                    selectedAgeOptionId = optionId
                    true
                } else {
                    false
                }
            }

            TriageQuestionId.SYMPTOM.value -> {
                val symptoms = response.parsedResponse?.symptoms
                if (symptoms != null) {
                    recordedSymptoms = symptoms.toSet()
                    hideSymptomErrorIfExists()
                    true
                } else {
                    false
                }
            }

            TriageQuestionId.SEVERITY.value -> {
                val optionId = when (response.parsedResponse?.symptomSeverity) {
                    1 -> "mild"
                    2 -> "low"
                    3 -> "moderate"
                    4 -> "high"
                    5 -> "severe"
                    else -> null
                }
                if (optionId != null) {
                    selectedSeverityOptionId = optionId
                    true
                } else {
                    false
                }
            }

            TriageQuestionId.DURATION.value -> {
                val optionId = when (response.parsedResponse?.symptomsDuration) {
                    0 -> "less_than_day"
                    1 -> "more_than_day"
                    2 -> "unknown"
                    else -> null
                }
                if (optionId != null) {
                    selectedDurationOptionId = optionId
                    true
                } else {
                    false
                }
            }

            TriageQuestionId.CHRONIC_CONDITIONS.value -> {
                val conditions = response.parsedResponse?.chronicConditions
                if (conditions != null) {
                    selectedChronicConditionsOptionIds = conditions.toSet()
                    true
                } else {
                    false
                }
            }

            TriageQuestionId.SYMPTOMS_BEFORE.value -> {
                val optionId = when (response.parsedResponse?.hadSymptomsBefore) {
                    0 -> "no"
                    1 -> "yes"
                    2 -> "unknown"
                    else -> null
                }
                if (optionId != null) {
                    selectedSymptomsBeforeOptionId = optionId
                    true
                } else {
                    false
                }
            }

            TriageQuestionId.SICK_CONTACT_HISTORY.value -> {
                val optionId = when (response.parsedResponse?.hadContact) {
                    0 -> "no"
                    1 -> "yes"
                    2 -> "unknown"
                    else -> null
                }
                if (optionId != null) {
                    selectedSickContactHistoryOptionId = optionId
                    true
                } else {
                    false
                }
            }

            else -> false
        }
    }

    fun canContinueFromSymptomQuestion(): Boolean {
        shouldShowNoSymptomError = selectedSymptomIds.isEmpty() && recordedSymptoms.isEmpty()
        return !shouldShowNoSymptomError
    }

    fun getFormAnswers(languageTag: String): TriageForm {
        return TriageForm(
            language = getLanguageCode(languageTag),
            symptoms = (selectedSymptomIds + recordedSymptoms).toList(),
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
        recordedSymptoms = emptySet()
        isSymptomOptionsExpanded = false
        isTranscribing = false
        recordingErrorResId = null
        shouldShowNoSymptomError = false
    }
}