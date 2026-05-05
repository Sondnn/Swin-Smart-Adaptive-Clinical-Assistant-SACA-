package com.saca.smartadaptiveclinicalassistant.presentation.components.form

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
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.BasicTextField
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
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.saca.smartadaptiveclinicalassistant.presentation.components.ActionBarIconButton
import com.saca.smartadaptiveclinicalassistant.presentation.components.AppBar
import com.saca.smartadaptiveclinicalassistant.presentation.components.AppButton
import com.saca.smartadaptiveclinicalassistant.presentation.components.AppButtonStyle
import com.saca.smartadaptiveclinicalassistant.ui.theme.AppBackground
import com.saca.smartadaptiveclinicalassistant.ui.theme.Brown
import com.saca.smartadaptiveclinicalassistant.ui.theme.Brown20
import com.saca.smartadaptiveclinicalassistant.ui.theme.Gray40
import com.saca.smartadaptiveclinicalassistant.ui.theme.Orange
import com.saca.smartadaptiveclinicalassistant.ui.theme.Orange40
import com.saca.smartadaptiveclinicalassistant.ui.theme.TextBrown
import kotlin.collections.chunked

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
    onBackClick: () -> Unit = {},
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

            QuestionTitle(
                text = questionTitle
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
fun QuestionTitle(
    text: String
) {
    Text(
        text = text,
        color = TextBrown,
        fontWeight = FontWeight.Black,
        fontSize = 24.sp,
        lineHeight = 32.sp,
        textAlign = TextAlign.Center
    )
}

@Composable
fun QuestionTextInput(
    text: String,
    placeholder: String,
    onTextChanged: (String) -> Unit,
) {
    BasicTextField(
        value = text,
        onValueChange = onTextChanged,
        textStyle = TextStyle(
            color = Color.Black,
        ),
        modifier = Modifier
            .fillMaxWidth()
            .height(130.dp)
            .clip(RoundedCornerShape(12.dp))
            .background(Color.White)
            .padding(14.dp),
        decorationBox = { innerTextField ->
            Box(modifier = Modifier.fillMaxWidth()) {
                if (text.isEmpty()) {
                    Text(

                        text = placeholder,
                        color = Color.Gray,
                    )
                }

                innerTextField()
            }
        }
    )
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
            AppButton(
                text = backButtonText,
                style = AppButtonStyle.Transparent,
                enabled = currentStep > 1,
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