package com.saca.smartadaptiveclinicalassistant.presentation.session

import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import androidx.lifecycle.ViewModel
import com.saca.smartadaptiveclinicalassistant.common.Constants.DEFAULT_LANGUAGE_TAG

class SessionViewModel: ViewModel() {
    var languageTag: String by mutableStateOf(DEFAULT_LANGUAGE_TAG)
        private set

    fun onLanguagePicked(tag: String) {
        languageTag = tag
        LocaleManager.apply(tag)
    }
}

