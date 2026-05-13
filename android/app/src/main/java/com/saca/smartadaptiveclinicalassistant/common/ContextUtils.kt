package com.saca.smartadaptiveclinicalassistant.common

import android.content.Context
import android.content.res.Configuration
import androidx.annotation.StringRes
import java.util.Locale

fun Context.getEnglishString(@StringRes resId: Int): String {
    val config = Configuration(resources.configuration)
    config.setLocale(Locale.ENGLISH)

    val context = createConfigurationContext(config)
    return context.getString(resId)
}