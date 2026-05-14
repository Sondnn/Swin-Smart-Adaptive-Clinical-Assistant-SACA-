package com.saca.smartadaptiveclinicalassistant.presentation.components.form

import androidx.annotation.DrawableRes
import androidx.annotation.StringRes

data class FormQuestionOption(
    val id: String,
    @param:StringRes val labelResourceId: Int,
    @param:DrawableRes val iconResourceId: Int? = null
)

data class FormQuestionImageOption(
    val id: String,
    @param:StringRes val labelResourceId: Int,
    @param:DrawableRes val iconResourceId: Int
)