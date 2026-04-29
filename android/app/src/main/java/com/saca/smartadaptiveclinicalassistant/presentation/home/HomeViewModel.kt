package com.saca.smartadaptiveclinicalassistant.presentation.home

import android.util.Log
import androidx.lifecycle.ViewModel

class HomeViewModel: ViewModel() {
    fun onGetStartedClicked() {
        Log.d(TAG, "Get Started tapped")
    }

    private companion object {
        const val TAG = "HomeViewModel"
    }
}