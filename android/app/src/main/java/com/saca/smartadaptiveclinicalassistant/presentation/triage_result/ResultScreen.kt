package com.saca.smartadaptiveclinicalassistant.presentation.triage_result

import android.util.Log
import androidx.annotation.DrawableRes
import androidx.annotation.StringRes
import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.saca.smartadaptiveclinicalassistant.R
import com.saca.smartadaptiveclinicalassistant.common.getEnglishString
import com.saca.smartadaptiveclinicalassistant.common.getLabelString
import com.saca.smartadaptiveclinicalassistant.domain.model.TriageCategory
import com.saca.smartadaptiveclinicalassistant.domain.model.TriageResult
import com.saca.smartadaptiveclinicalassistant.presentation.components.ActionBarIconButton
import com.saca.smartadaptiveclinicalassistant.presentation.components.AppBar
import com.saca.smartadaptiveclinicalassistant.presentation.components.AppButton
import com.saca.smartadaptiveclinicalassistant.presentation.components.AppButtonStyle
import com.saca.smartadaptiveclinicalassistant.presentation.components.Title
import com.saca.smartadaptiveclinicalassistant.presentation.components.form.SpeakButton
import com.saca.smartadaptiveclinicalassistant.presentation.components.form.SpeakQuestionSection
import com.saca.smartadaptiveclinicalassistant.presentation.components.form.rememberSpeaker
import com.saca.smartadaptiveclinicalassistant.ui.theme.AppBackground
import com.saca.smartadaptiveclinicalassistant.ui.theme.Brown
import com.saca.smartadaptiveclinicalassistant.ui.theme.Brown20
import com.saca.smartadaptiveclinicalassistant.ui.theme.TextDarkBrown
import org.koin.androidx.compose.koinViewModel

@Composable
fun ResultScreen(
    onOkClick: () -> Unit,
    modifier: Modifier = Modifier,
    triageResultViewModel: TriageResultViewModel = koinViewModel(),
) {
    val uiState = triageResultViewModel.uiState

    Scaffold(
        topBar = {
            AppBar(
                title = stringResource(R.string.home_action_bar_title),
                iconButton = ActionBarIconButton.BACK,
                onIconButtonClick = onOkClick,
                iconContentDescription = stringResource(R.string.home_action_bar_title),
            )
        },
        modifier = modifier.fillMaxSize(),
    ) { innerPadding ->
        Column(
            modifier = Modifier
                .padding(innerPadding)
                .fillMaxSize()
                .background(AppBackground)
                .padding(horizontal = 16.dp),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Spacer(modifier = Modifier.height(42.dp))

            when (uiState) {
                is TriageResultUIState.Success -> {
                    val result = uiState.triageResult
                    Title(text = stringResource(R.string.triage_result_title))
                    Spacer(modifier = Modifier.height(28.dp))
                    ResultCard(result = result)
                    Spacer(modifier = Modifier.height(12.dp))
                    SymptomsSummary(result.symptoms)
                }
                is TriageResultUIState.Error -> {
                    Title(text = stringResource(R.string.triage_result_error_title))
                    Spacer(modifier = Modifier.height(28.dp))
                    ErrorCard()
                    Spacer(modifier = Modifier.height(12.dp))
                    SymptomsSummary(uiState.symptoms)
                }
                else -> {
                }
            }

            Spacer(modifier = Modifier.weight(1f))

            AppButton(
                text = stringResource(R.string.triage_result_ok_button),
                style = AppButtonStyle.Brown,
                onClick = onOkClick
            )

            Spacer(modifier = Modifier.height(28.dp))
        }
    }
}

@DrawableRes
private fun triageCategoryIconRes(category: TriageCategory): Int {
    return when (category) {
        TriageCategory.A -> R.drawable.severity_category_a
        TriageCategory.B -> R.drawable.severity_category_b
        TriageCategory.C -> R.drawable.severity_category_c
        TriageCategory.D -> R.drawable.severity_category_d
        TriageCategory.E -> R.drawable.severity_category_e
        TriageCategory.F -> R.drawable.severity_category_f
        else -> {
            R.drawable.severity_category_f
        }
    }
}

@StringRes
private fun categoryTitleRes(category: TriageCategory): Int {
    return when (category) {
        TriageCategory.A -> R.string.triage_result_category_a
        TriageCategory.B -> R.string.triage_result_category_b
        TriageCategory.C -> R.string.triage_result_category_c
        TriageCategory.D -> R.string.triage_result_category_d
        TriageCategory.E -> R.string.triage_result_category_e
        TriageCategory.F -> R.string.triage_result_category_f
    }
}

@StringRes
private fun categoryRecommendationRes(category: TriageCategory): Int {
    return when (category) {
        TriageCategory.A -> R.string.triage_result_category_a_recommendation
        TriageCategory.B -> R.string.triage_result_category_b_recommendation
        TriageCategory.C -> R.string.triage_result_category_c_recommendation
        TriageCategory.D -> R.string.triage_result_category_d_recommendation
        TriageCategory.E -> R.string.triage_result_category_e_recommendation
        TriageCategory.F -> R.string.triage_result_category_f_recommendation
    }
}

@Composable
private fun ResultCard(result: TriageResult) {
    val iconResourceId = triageCategoryIconRes(result.triageCategory)
    val categoryTitle = stringResource(categoryTitleRes(result.triageCategory))
    val categoryRecommendation = stringResource(categoryRecommendationRes(result.triageCategory))
    val possibleCondition = result.possibleCondition?: stringResource(R.string.triage_result_possible_condition_unknown)
    val context = LocalContext.current
    val resultSpeaker = rememberSpeaker()

    val resultStringIds = mutableListOf(
        R.string.triage_result_severity_label,
        categoryTitleRes(result.triageCategory),
        R.string.triage_result_recommendation_title,
        categoryRecommendationRes(result.triageCategory),
        R.string.triage_result_possible_condition_title
    )
    val resultStrings = resultStringIds.map {
        context.getEnglishString(it)
    }.toMutableList()

    resultStrings.add(possibleCondition)
    val resultSpeakerText = resultStrings.joinToString()

    Column(
        modifier = Modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(8.dp))
            .background(Brown20)
            .padding(18.dp),
    ) {
        Row(verticalAlignment = Alignment.CenterVertically) {
            Image(
                painter = painterResource(iconResourceId),
                contentDescription = categoryTitle,
                modifier = Modifier
                    .size(56.dp)
            )

            Column(modifier = Modifier.padding(start = 14.dp)) {
                Text(
                    text = stringResource(R.string.triage_result_severity_label),
                    style = MaterialTheme.typography.labelLarge,
                    color = TextDarkBrown,
                )

                Text(
                    text = categoryTitle,
                    style = MaterialTheme.typography.titleMedium,
                    color = TextDarkBrown,
                    fontSize = 30.sp,
                    fontWeight = FontWeight.SemiBold,
                )
            }
        }

        Spacer(modifier = Modifier.height(20.dp))

        Text(
            text = stringResource(R.string.triage_result_recommendation_title),
            style = MaterialTheme.typography.bodyMedium,
            color = TextDarkBrown
        )

        Spacer(modifier = Modifier.height(6.dp))

        Text(
            text = categoryRecommendation,
            style = MaterialTheme.typography.bodySmall,
            color = TextDarkBrown
        )

        Spacer(modifier = Modifier.height(20.dp))

        Text(
            text = stringResource(R.string.triage_result_possible_condition_title),
            style = MaterialTheme.typography.bodyMedium,
            color = TextDarkBrown
        )

        Spacer(modifier = Modifier.height(6.dp))

        Text(
            text = possibleCondition,
            style = MaterialTheme.typography.bodySmall,
            color = TextDarkBrown
        )

        Spacer(modifier = Modifier.height(20.dp))

        SpeakButton(
            text = stringResource(R.string.triage_form_listen_button),
            onClick = {
                resultSpeaker.speakText(resultSpeakerText)
            }
        )
    }
}

@Composable
private fun SymptomsSummary(symptoms: List<String>) {
    Column(
        modifier = Modifier
            .fillMaxWidth()
            .padding(18.dp)
    ) {
        Text(
            text = stringResource(R.string.triage_result_symptoms_summary_title),
            style = MaterialTheme.typography.bodyMedium,
            color = TextDarkBrown
        )

        Spacer(modifier = Modifier.height(6.dp))

        for (symptom in symptoms) {
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(vertical = 4.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                Box(
                    modifier = Modifier
                        .size(8.dp)
                        .clip(CircleShape)
                        .background(Brown.copy(alpha = 0.35f))
                        .padding(horizontal = 10.dp)
                )

                Text(
                    text = getLabelString(symptom),
                    style = MaterialTheme.typography.bodySmall,
                    color = TextDarkBrown,
                    modifier = Modifier.padding(start = 12.dp)
                )
            }
        }
    }
}


@Composable
private fun ErrorCard() {
    Box(
        modifier = Modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(8.dp))
            .background(Brown20)
            .padding(24.dp)
    ) {
        Text(
            text = stringResource(R.string.triage_result_error_message),
            style = MaterialTheme.typography.bodySmall,
            fontWeight = FontWeight.SemiBold,
            color = TextDarkBrown,
        )
    }
}