package com.saca.smartadaptiveclinicalassistant.presentation.components.form

import android.Manifest
import android.content.Context
import android.content.pm.PackageManager
import android.util.Log
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.annotation.DrawableRes
import androidx.annotation.StringRes
import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.WindowInsets
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.offset
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.core.content.ContextCompat.checkSelfPermission
import com.saca.smartadaptiveclinicalassistant.R
import com.saca.smartadaptiveclinicalassistant.common.getEnglishString
import com.saca.smartadaptiveclinicalassistant.data.local.VoiceRecorder
import com.saca.smartadaptiveclinicalassistant.presentation.components.ActionBarIconButton
import com.saca.smartadaptiveclinicalassistant.presentation.components.AppBar
import com.saca.smartadaptiveclinicalassistant.presentation.components.AppButton
import com.saca.smartadaptiveclinicalassistant.presentation.components.AppButtonStyle
import com.saca.smartadaptiveclinicalassistant.presentation.components.Title
import com.saca.smartadaptiveclinicalassistant.ui.theme.AppBackground
import com.saca.smartadaptiveclinicalassistant.ui.theme.Brown
import com.saca.smartadaptiveclinicalassistant.ui.theme.Brown20
import com.saca.smartadaptiveclinicalassistant.ui.theme.Gray40
import com.saca.smartadaptiveclinicalassistant.ui.theme.Orange
import com.saca.smartadaptiveclinicalassistant.ui.theme.Orange40
import java.io.File
import kotlin.collections.chunked

@Composable
fun FormQuestionScaffold(
    modifier: Modifier = Modifier,
    appBarTitle: String,
    questionTitle: String,
    @StringRes questionResId: Int,
    continueButtonText: String,
    isContinueAlwaysAllowed: Boolean = false,
    continueButtonStyle: AppButtonStyle = AppButtonStyle.Brown,
    backButtonText: String,
    options: List<FormQuestionOption>,
    selectedOptionId: String? = null,
    selectedOptionIds: Set<String>? = emptySet(),
    currentStep: Int,
    totalSteps: Int,
    onCancelClick: () -> Unit = {},
    onBackClick: () -> Unit = {},
    onOptionClick: (String) -> Unit,
    onContinueClick: () -> Unit,
    voiceQuestionId: Int? = null,
    isTranscribing: Boolean = false,
    @StringRes recordingErrorResId: Int? = null,
    onTranscribeAudio: ((File) -> Unit)? = null
) {
    val optionResIds = options.map { option ->
        option.labelResourceId
    }

    Scaffold(
        contentWindowInsets = WindowInsets(0),
        topBar = {
            AppBar(
                title = appBarTitle,
                iconButton = ActionBarIconButton.BACK,
                iconContentDescription = stringResource(R.string.app_bar_button_back_content_description),
                onIconButtonClick = onCancelClick
            )
        },
        modifier = modifier.fillMaxWidth(),
    ) { innerPadding ->
        Column(
            modifier = Modifier
                .padding(innerPadding)
                .fillMaxWidth()
                .background(AppBackground)
                .padding(horizontal = 16.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
        ) {
            Spacer(modifier = Modifier.height(54.dp))

            Title(
                text = questionTitle
            )

            Spacer(modifier = Modifier.height(24.dp))

            QuestionOptions(
                options = options,
                selectedOptionIds = buildSet {
                    selectedOptionIds?.let { addAll(it) }
                    selectedOptionId?.let { add(it) }
                },
                onOptionClick = onOptionClick
            )

            Spacer(modifier = Modifier.height(24.dp))
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(16.dp)
            ) {
                Box(modifier = Modifier.weight(1f)) {
                    SpeakQuestionSection(
                        questionResId = questionResId,
                        optionResIds = optionResIds,
                    )
                }

                if (voiceQuestionId != null && onTranscribeAudio != null) {
                    Box(modifier = Modifier.weight(1f)) {
                    VoiceInputSection(
                        isTranscribing = isTranscribing,
                        onTranscribeAudio = onTranscribeAudio,
                    )
                }
                }
            }

            if (recordingErrorResId != null) {
                Log.d("Form question recording", recordingErrorResId.toString())
                Spacer(modifier = Modifier.height(10.dp))
                ErrorMessage(text = stringResource(recordingErrorResId))
            }

            Spacer(modifier = Modifier.weight(1f))

            QuestionBottomBar(
                backButtonText = backButtonText,
                continueButtonText = continueButtonText,
                continueButtonStyle = continueButtonStyle,
                currentStep = currentStep,
                totalSteps = totalSteps,
                canContinue = selectedOptionId != null || !selectedOptionIds.isNullOrEmpty() || isContinueAlwaysAllowed,
                onBackClick = onBackClick,
                onContinueClick = onContinueClick,
            )
        }
    }
}

@Composable
fun SpeakQuestionSection(
    @StringRes questionResId: Int,
    @StringRes optionResIds: List<Int> = emptyList()
) {
    val context = LocalContext.current
    val questionSpeaker = rememberSpeaker()

    val questionString = context.getEnglishString(questionResId)
    var text = questionString

    if (optionResIds.isNotEmpty()) {
        val optionStrings = optionResIds.map {
            context.getEnglishString(it)
        }

         text += optionStrings.joinToString()
    }

    SpeakButton(
        text = stringResource(R.string.triage_form_listen_button),
        onClick = {
            questionSpeaker.speakText(text)
        }
    )
}

@Composable
private fun VoiceInputSection(
    isTranscribing: Boolean,
    onTranscribeAudio: (File) -> Unit,
) {
    val context = LocalContext.current
    val voiceRecorder = remember { VoiceRecorder() }
    var isRecordButtonPressed by remember { mutableStateOf(false) }

    val requestPermissionLauncher = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.RequestPermission(),
    ) { isGranted ->
        if (!isGranted) {
            Log.w("VoiceInputSection", "RECORD_AUDIO permission denied")
        }
    }

    RecordButton(
        text = when {
            isTranscribing -> stringResource(R.string.triage_form_symptom_transcribing)
            isRecordButtonPressed -> stringResource(R.string.triage_form_symptom_recording)
            else -> stringResource(R.string.triage_form_answer_button)
        },
        isRecording = isRecordButtonPressed,
        isEnabled = !isTranscribing,
        onPress = {
            if (!hasRecordAudioPermission(context)) {
                requestPermissionLauncher.launch(Manifest.permission.RECORD_AUDIO)
                return@RecordButton
            }

            val startResult = voiceRecorder.startRecording(context)
            if (startResult.isFailure) {
                Log.e("VoiceInputSection", "startRecording failed", startResult.exceptionOrNull())
                return@RecordButton
            }

            isRecordButtonPressed = true

            val didRelease = tryAwaitRelease()
            isRecordButtonPressed = false

            if (!didRelease) {
                voiceRecorder.cancelRecording()
                return@RecordButton
            }

            val stopResult = voiceRecorder.stopRecording()
            stopResult.fold(
                onSuccess = { audioFile ->
                    onTranscribeAudio(audioFile)
                },
                onFailure = {
                    Log.e("VoiceInputSection", "stopRecording failed", it)
                },
            )
        }
    )
}
private fun hasRecordAudioPermission(context: Context): Boolean {
    return checkSelfPermission(
        context,
        Manifest.permission.RECORD_AUDIO
    ) == PackageManager.PERMISSION_GRANTED
}

@Composable
private fun QuestionOptions(
    options: List<FormQuestionOption>,
    selectedOptionIds: Set<String>,
    onOptionClick: (String) -> Unit,
) {
    Column(
        modifier = Modifier.fillMaxWidth(),
        verticalArrangement = Arrangement.spacedBy(12.dp)
    ) {
        for (option in options) {
            QuestionOptionButton(
                option = option,
                selected = selectedOptionIds.contains(option.id),
                onClick = {
                    onOptionClick(option.id)
                }
            )
        }
    }
}

@Composable
fun QuestionOptionButton(
    option: FormQuestionOption,
    selected: Boolean,
    onClick: () -> Unit,
    modifier: Modifier = Modifier
) {
    val text = stringResource(option.labelResourceId)
    val borderColor = if (selected) Orange else Color.Transparent
    val bgColor = if (selected) Orange40 else Brown20

    OutlinedButton(
        onClick = onClick,
        colors = ButtonDefaults.outlinedButtonColors(
            containerColor = bgColor,
            contentColor = Brown
        ),
        border = BorderStroke(2.dp, borderColor),
        shape = RoundedCornerShape(6.dp),
        modifier = modifier
            .fillMaxWidth()
            .height(56.dp)
    ) {
        Box(
            modifier = Modifier.fillMaxWidth(),
            contentAlignment = Alignment.Center
        ) {
            if (option.iconResourceId != null) {
                Image(
                    painter = painterResource(option.iconResourceId),
                    contentDescription = null,
                    modifier = Modifier
                        .align(Alignment.CenterStart)
                        .size(30.dp)
                )
            }
            Text(
                text = text,
                color = Brown,
                style = MaterialTheme.typography.bodyMedium,
                textAlign = TextAlign.Center
            )
        }
    }
}

@Composable
fun QuestionImageOption(
    options: List<FormQuestionImageOption>,
    selectedOptionIds: Set<String>,
    isExpanded: Boolean,
    initialOptionCount: Int,
    onOptionClick: (String) -> Unit,
) {
    val visibleOptions = if (isExpanded) {
        options
    } else {
        options.take(initialOptionCount)
    }

    Column(
        verticalArrangement = Arrangement.spacedBy(8.dp),
        modifier = Modifier.fillMaxWidth()
    ) {
        for (rowOptions in visibleOptions.chunked(3)) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(8.dp),
            ) {
                for (option in rowOptions) {
                    QuestionImageOptionButton(
                        option = option,
                        selected = selectedOptionIds.contains(option.id),
                        onClick = {
                            onOptionClick(option.id)
                        },
                        modifier = Modifier.weight(1f)
                    )
                }

                repeat(3 - rowOptions.size) {
                    Spacer(modifier = Modifier.weight(1f))
                }
            }
        }
    }
}


@Composable
private fun SelectedCheckMark(modifier: Modifier = Modifier) {
    Box(
        modifier = modifier
            .size(30.dp),
        contentAlignment = Alignment.Center,
    ) {
        Image(
            painter = painterResource(R.drawable.ic_cicle_check),
            contentDescription = null,
            modifier = Modifier
                .size(30.dp)
        )
    }
}

@Composable
fun QuestionImageOptionButton(
    option: FormQuestionImageOption,
    selected: Boolean,
    onClick: () -> Unit,
    modifier: Modifier = Modifier,
) {
    val backgroundColor = Color.White
    val borderColor = if (selected) Orange else Color.Transparent

    Box(
        modifier = modifier
            .height(120.dp)
    ) {
        Box(
            modifier = Modifier
                .matchParentSize()
                .clip(RoundedCornerShape(6.dp))
                .background(backgroundColor)
                .border(
                    BorderStroke(2.dp, borderColor),
                    RoundedCornerShape(6.dp))
                .clickable(onClick = onClick)
                .padding(horizontal = 4.dp, vertical = 8.dp)
        ) {
            Column(
                modifier = Modifier.align(Alignment.Center),
                horizontalAlignment = Alignment.CenterHorizontally,
            ) {
                Image(
                    painter = painterResource(option.iconResourceId),
                    contentDescription = stringResource(option.labelResourceId),
                    contentScale = ContentScale.Fit,
                    modifier = Modifier.size(50.dp)
                )

                Spacer(modifier = Modifier.height(8.dp))

                Text(
                    text = stringResource(option.labelResourceId),
                    style = MaterialTheme.typography.labelLarge,
                    lineHeight = 18.sp,
                    color = Color.Black,
                    textAlign = TextAlign.Center
                )
            }
        }

        if (selected) {
            SelectedCheckMark(
                modifier = Modifier
                    .align(Alignment.TopEnd)
                    .offset(x = 3.dp, y = (-5).dp)
            )
        }
    }
}


@Composable
fun QuestionBottomBar(
    backButtonText: String,
    continueButtonText: String,
    continueButtonStyle: AppButtonStyle = AppButtonStyle.Brown,
    currentStep: Int,
    totalSteps: Int,
    canContinue: Boolean,
    onContinueClick: () -> Unit,
    onBackClick: () -> Unit = {},
) {
    Column(
        modifier = Modifier
            .fillMaxWidth()
            .padding(bottom = 24.dp),
    ) {
        QuestionProgressBar(
            currentStep = currentStep,
            totalSteps = totalSteps,
        )

        Spacer(modifier = Modifier.height(16.dp))

        Row(
            modifier = Modifier.fillMaxWidth(),
            verticalAlignment = Alignment.CenterVertically,
        ) {
            if (currentStep > 1) {
                AppButton(
                    text = backButtonText,
                    style = AppButtonStyle.Transparent,
                    onClick = onBackClick,
                    modifier = Modifier.weight(1f),
                )
            } else {
                Spacer(modifier = Modifier.weight(1f))
            }

            Spacer(modifier = Modifier.width(16.dp))

            AppButton(
                text = continueButtonText,
                style = continueButtonStyle,
                enabled = canContinue,
                onClick = onContinueClick,
                modifier = Modifier.weight(1f),
            )
        }
    }
}

@Composable
private fun QuestionProgressBar(
    currentStep: Int,
    totalSteps: Int,
) {
    val progress = currentStep.toFloat() / totalSteps.toFloat()

    Box(
        modifier = Modifier
            .fillMaxWidth()
            .height(3.dp)
            .background(Gray40),
    ) {
        Box(
            modifier = Modifier
                .fillMaxWidth(progress)
                .height(3.dp)
                .background(Orange),
        )
    }
}