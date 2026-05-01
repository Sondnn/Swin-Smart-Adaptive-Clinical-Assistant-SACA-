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
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.OutlinedButton
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
import com.saca.smartadaptiveclinicalassistant.presentation.components.QuestionImageOption
import com.saca.smartadaptiveclinicalassistant.presentation.components.QuestionTextInput
import com.saca.smartadaptiveclinicalassistant.presentation.components.QuestionTitle
import com.saca.smartadaptiveclinicalassistant.ui.theme.Brown
import com.saca.smartadaptiveclinicalassistant.ui.theme.Brown20
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

            QuestionImageOption(
                options = options,
                selectedOptionIds = triageFormViewModel.selectedSymptomIds,
                isExpanded =  triageFormViewModel.isSymptomOptionsExpanded,
                initialOptionCount = 3,
                onOptionClick = triageFormViewModel::onSymptomOptionSelected
            )

            if (!triageFormViewModel.isSymptomOptionsExpanded) {
                Spacer(modifier = Modifier.height(8.dp))

                ShowMoreButton(
                    text = stringResource(R.string.triage_form_symptom_show_more),
                    onClick = triageFormViewModel::onSymptomOptionsExpandClicked
                )
            }

            Spacer(modifier = Modifier.height(24.dp))

            OrDivider(text = stringResource(R.string.triage_form_symptom_or))

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
fun ShowMoreButton(
    text: String,
    onClick: () -> Unit
) {
    OutlinedButton(
        onClick = onClick,
        colors = ButtonDefaults.outlinedButtonColors(
            containerColor = Brown20,
            contentColor = Brown,
        ),
        border = BorderStroke(0.dp, Color.Transparent),
        shape = RoundedCornerShape(2.dp),
        modifier = Modifier
            .fillMaxWidth()
            .height(32.dp)
    ) {
        Text(
            text = text,
            color = Brown,
            fontWeight = FontWeight.Bold,
            fontSize = 12.sp,
            lineHeight = 16.sp,
            textAlign = TextAlign.Center,
        )
    }
}

@Composable
private fun OrDivider(text: String) {
    Row(
        modifier = Modifier.fillMaxWidth(),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Box(
            modifier = Modifier
                .weight(1f)
                .height(1.dp)
                .background(Brown.copy(alpha = 0.35f)),
        )

        Text(
            text = text,
            color = Brown,
            fontWeight = FontWeight.Bold,
            fontSize = 12.sp,
            lineHeight = 16.sp,
            modifier = Modifier.padding(horizontal = 16.dp),
        )

        Box(
            modifier = Modifier
                .weight(1f)
                .height(1.dp)
                .background(Brown.copy(alpha = 0.35f)),
        )
    }
}
