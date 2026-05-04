package com.saca.smartadaptiveclinicalassistant.presentation.result

import android.util.Log
import androidx.annotation.DrawableRes
import androidx.annotation.StringRes
import androidx.compose.foundation.Image
import androidx.compose.foundation.background
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
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.saca.smartadaptiveclinicalassistant.R
import com.saca.smartadaptiveclinicalassistant.domain.model.TriageCategory
import com.saca.smartadaptiveclinicalassistant.domain.model.TriageResult
import com.saca.smartadaptiveclinicalassistant.presentation.components.ActionBarIconButton
import com.saca.smartadaptiveclinicalassistant.presentation.components.AppBar
import com.saca.smartadaptiveclinicalassistant.presentation.components.AppButton
import com.saca.smartadaptiveclinicalassistant.presentation.components.AppButtonStyle
import com.saca.smartadaptiveclinicalassistant.presentation.components.Title
import com.saca.smartadaptiveclinicalassistant.presentation.triage_result.TriageResultUIState
import com.saca.smartadaptiveclinicalassistant.presentation.triage_result.TriageResultViewModel
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
    val result = if (uiState is TriageResultUIState.Success) {
        uiState.triageResult
    } else {
        TriageResult(
            triageCategory = TriageCategory.A,
            symptoms = listOf()
        )
    }

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

            Title(text = stringResource(R.string.triage_result_title))

            Spacer(modifier = Modifier.height(28.dp))

            ResultCard(result = result)

            Spacer(modifier = Modifier.height(12.dp))

            SymptomsSummary(result.symptoms)

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
        TriageCategory.A, TriageCategory.B -> R.drawable.severity_category_1
        TriageCategory.C, TriageCategory.D -> R.drawable.severity_category_2
        else -> {
            R.drawable.severity_category_3
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

        Log.d("Result", symptoms.toString())
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
                    text = symptom,
                    style = MaterialTheme.typography.bodySmall,
                    color = TextDarkBrown,
                    modifier = Modifier.padding(start = 12.dp)
                )
            }
        }
    }
}