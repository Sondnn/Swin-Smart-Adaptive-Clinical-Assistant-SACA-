package com.saca.smartadaptiveclinicalassistant.presentation.components

import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.saca.smartadaptiveclinicalassistant.ui.theme.AppBackground
import com.saca.smartadaptiveclinicalassistant.ui.theme.Brown
import com.saca.smartadaptiveclinicalassistant.ui.theme.Brown20
import com.saca.smartadaptiveclinicalassistant.ui.theme.Gray40
import com.saca.smartadaptiveclinicalassistant.ui.theme.Orange
import com.saca.smartadaptiveclinicalassistant.ui.theme.Orange40
import com.saca.smartadaptiveclinicalassistant.ui.theme.TextBrown

@Composable
fun FormQuestionScaffold(
    modifier: Modifier = Modifier,
    appBarTitle: String,
    questionTitle: String,
    backContentDescription: String,
    continueButtonText: String,
    continueButtonStyle: AppButtonStyle = AppButtonStyle.Brown,
    backButtonText: String,
    options: List<FormQuestionOption>,
    selectedOptionId: String?,
    currentStep: Int,
    totalSteps: Int,
    onBackClick: () -> Unit,
    onOptionClick: (String) -> Unit,
    onContinueClick: () -> Unit,
) {
    Scaffold(
        topBar = {
            AppBar(
                title = appBarTitle,
                iconButton = ActionBarIconButton.BACK,
                iconContentDescription = backContentDescription,
                onIconButtonClick = onBackClick
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

            Text(
                text = questionTitle,
                color = TextBrown,
                fontWeight = FontWeight.Black,
                fontSize = 24.sp,
                lineHeight = 32.sp,
                textAlign = TextAlign.Center
            )

            Spacer(modifier = Modifier.height(24.dp))

            QuestionOptions(
                options = options,
                selectedOptionId = selectedOptionId,
                onOptionClick = onOptionClick
            )

            Spacer(modifier = Modifier.weight(1f))

            QuestionBottomBar(
                backButtonText = backButtonText,
                continueButtonText = continueButtonText,
                continueButtonStyle = continueButtonStyle,
                currentStep = currentStep,
                totalSteps = totalSteps,
                canContinue = selectedOptionId != null,
                onBackClick = onBackClick,
                onContinueClick = onContinueClick,
            )
        }
    }
}

@Composable
private fun QuestionOptions(
    options: List<FormQuestionOption>,
    selectedOptionId: String?,
    onOptionClick: (String) -> Unit,
) {
    Column(
        modifier = Modifier.fillMaxWidth(),
        verticalArrangement = Arrangement.spacedBy(12.dp)
    ) {
        for (option in options) {
            QuestionOptionButton(
                text = stringResource(option.labelResourceId),
                selected = option.id == selectedOptionId,
                onClick = {
                    onOptionClick(option.id)
                }
            )
        }
    }
}

@Composable
fun QuestionOptionButton(
    text: String,
    selected: Boolean,
    onClick: () -> Unit,
    modifier: Modifier = Modifier
) {
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
        Text(
            text = text,
            color = Brown,
            fontWeight = FontWeight.Bold,
            textAlign = TextAlign.Center
        )
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
    onBackClick: () -> Unit,
    onContinueClick: () -> Unit,
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
            AppButton(
                text = backButtonText,
                style = AppButtonStyle.Transparent,
                onClick = onBackClick,
                modifier = Modifier.weight(1f),
            )

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