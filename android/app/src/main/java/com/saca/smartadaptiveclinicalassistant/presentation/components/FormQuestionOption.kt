package com.saca.smartadaptiveclinicalassistant.presentation.components

import androidx.annotation.DrawableRes
import androidx.annotation.StringRes

data class FormQuestionOption(
    val id: String,
    @param:StringRes val labelResourceId: Int
)

data class FormQuestionImageOption(
    val id: String,
    @param:StringRes val labelResourceId: Int,
    @param:DrawableRes val iconResourceId: Int
)