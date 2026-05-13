package com.saca.smartadaptiveclinicalassistant.presentation.session

import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.saca.smartadaptiveclinicalassistant.common.Constants.DEFAULT_LANGUAGE_TAG
import com.saca.smartadaptiveclinicalassistant.common.Constants.LANGUAGE_TAG_ENGLISH
import com.saca.smartadaptiveclinicalassistant.common.Constants.LANGUAGE_TAG_WALMAJARRI
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch

class SessionViewModel: ViewModel() {
    var languageTag: String by mutableStateOf(DEFAULT_LANGUAGE_TAG)
        private set

    fun onLanguagePicked(tag: String) {
        if (languageTag == tag) return
        languageTag = tag
        LocaleManager.apply(tag)
    }

    fun toggleLanguage() {
        val toggleTag = if (languageTag == LANGUAGE_TAG_ENGLISH) {
            LANGUAGE_TAG_WALMAJARRI
        } else {
            LANGUAGE_TAG_ENGLISH
        }

        onLanguagePicked(toggleTag)
    }
}

