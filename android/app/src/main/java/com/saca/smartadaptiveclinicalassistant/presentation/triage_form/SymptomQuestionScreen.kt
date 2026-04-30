package com.saca.smartadaptiveclinicalassistant.presentation.triage_form

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
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.saca.smartadaptiveclinicalassistant.presentation.components.ActionBarIconButton
import com.saca.smartadaptiveclinicalassistant.presentation.components.AppBar
import com.saca.smartadaptiveclinicalassistant.presentation.components.QuestionBottomBar
import com.saca.smartadaptiveclinicalassistant.ui.theme.AppBackground
import com.saca.smartadaptiveclinicalassistant.ui.theme.TextBrown
import org.koin.androidx.compose.koinViewModel


import com.saca.smartadaptiveclinicalassistant.R
import com.saca.smartadaptiveclinicalassistant.presentation.components.FormQuestionImageOption
import com.saca.smartadaptiveclinicalassistant.presentation.components.QuestionTextInput
import com.saca.smartadaptiveclinicalassistant.presentation.components.QuestionTitle
import com.saca.smartadaptiveclinicalassistant.ui.theme.Orange
import kotlin.collections.chunked

@Composable
fun SymptomQuestionScreen(
    onBackClick: () -> Unit,
    onContinueClick: () -> Unit,
    modifier: Modifier = Modifier,
    triageFormViewModel: TriageFormViewModel = koinViewModel(),
) {
    val options = TriageFormViewModel.SymptomOption.entries.map {
        FormQuestionImageOption(
            id = it.value,
            labelResourceId = it.labelRes,
            iconResourceId = it.iconRes
        )
    }
    Scaffold(
        topBar = {
            AppBar(
                title = stringResource(R.string.triage_form_action_bar_title),
                iconButton = ActionBarIconButton.BACK,
                iconContentDescription = stringResource(R.string.triage_form_action_bar_title),
                onIconButtonClick = onBackClick
            )
        },
        modifier = modifier.fillMaxSize(),
    ) { innerPadding ->
        Column(
            modifier = Modifier
                .padding(innerPadding)
                .fillMaxSize()
                .background(AppBackground)
                .verticalScroll(rememberScrollState())
                .padding(horizontal = 16.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
        ) {
            Spacer(modifier = Modifier.height(54.dp))

            QuestionTitle(
                text = stringResource(R.string.triage_form_symptom_title)
            )

            Spacer(modifier = Modifier.height(24.dp))

            SymptomGrid(
                symptomOptions = options,
                selectedSymptomIds = triageFormViewModel.selectedSymptomIds,
                onSymptomClick = triageFormViewModel::onSymptomOptionSelected
            )

            Spacer(modifier = Modifier.height(24.dp))

            QuestionTitle(
                text = stringResource(R.string.triage_form_symptom_describe_title)
            )

            Spacer(modifier = Modifier.height(16.dp))

            QuestionTextInput(
                text = triageFormViewModel.symptomDescriptionText,
                placeholder = stringResource(R.string.triage_form_symptom_details_placeholder),
                onTextChanged = triageFormViewModel::onSymptomDescriptionChanged
            )

            Spacer(modifier = Modifier.height(24.dp))

            QuestionBottomBar(
                backButtonText = stringResource(R.string.triage_form_back_button),
                continueButtonText = stringResource(R.string.triage_form_continue_button),
                currentStep = 3,
                totalSteps = 5,
                canContinue = triageFormViewModel.selectedSymptomIds.isNotEmpty(),
                onBackClick = onBackClick,
                onContinueClick = onContinueClick,
            )
        }
    }
}


@Composable
fun SymptomGrid(
    symptomOptions: List<FormQuestionImageOption>,
    selectedSymptomIds: Set<String>,
    onSymptomClick: (String) -> Unit,
) {
    Column(
        verticalArrangement = Arrangement.spacedBy(8.dp),
        modifier = Modifier.fillMaxWidth()
    ) {
        for (rowOptions in symptomOptions.chunked(3)) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(8.dp),
            ) {
                for (option in rowOptions) {
                    SymptomCard(
                        option = option,
                        selected = selectedSymptomIds.contains(option.id),
                        onClick = {
                            onSymptomClick(option.id)
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
fun SymptomCard(
    option: FormQuestionImageOption,
    selected: Boolean,
    onClick: () -> Unit,
    modifier: Modifier = Modifier,
) {
    val backgroundColor = Color.White
    val borderColor = if (selected) Orange else Color.Transparent

    Box(
        modifier = modifier
            .height(100.dp)
            .clip(RoundedCornerShape(6.dp))
            .background(backgroundColor)
            .border(BorderStroke(2.dp, borderColor), RoundedCornerShape(6.dp))
            .clickable(onClick = onClick)
            .padding(horizontal = 4.dp, vertical = 6.dp)
    ) {
        Column(
            modifier = Modifier.align(Alignment.Center),
            horizontalAlignment = Alignment.CenterHorizontally,
        ) {

            Image(
                painter = painterResource(option.iconResourceId),
                contentDescription = stringResource(option.labelResourceId),
                contentScale = ContentScale.Fit,
                modifier = Modifier.size(36.dp)
            )

            Spacer(modifier = Modifier.height(8.dp))

            Text(
                text = stringResource(option.labelResourceId),
                color = Color.Black,
                fontWeight = FontWeight.Bold,
                lineHeight = 11.sp,
                textAlign = TextAlign.Center
            )
        }
    }
}
