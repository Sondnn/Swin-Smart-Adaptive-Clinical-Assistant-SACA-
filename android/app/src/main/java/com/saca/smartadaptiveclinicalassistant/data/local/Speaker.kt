package com.saca.smartadaptiveclinicalassistant.data.local

import android.content.Context
import android.speech.tts.TextToSpeech
import java.util.Locale

class Speaker(context: Context) {
    private var textToSpeech: TextToSpeech? = null
    private var isEngineReady: Boolean = false
    private var pendingSpeechText: String? = null

    init {
        textToSpeech = TextToSpeech(context) { status ->
            isEngineReady = status == TextToSpeech.SUCCESS
            if (isEngineReady) {
                textToSpeech?.language = Locale.forLanguageTag("en-AU")
                pendingSpeechText?.let { queuedText ->
                    speak(queuedText)
                    pendingSpeechText = null
                }
            }
        }
    }

    fun speakText(
        text: String,
    ) {
        if (text.isEmpty()) {
            return
        }

        if (!isEngineReady) {
            pendingSpeechText = text
            return
        }

        speak(text)
    }

    private fun speak(text: String) {
        textToSpeech?.speak(text, TextToSpeech.QUEUE_FLUSH, null, "speaker")
    }

    fun release() {
        textToSpeech?.stop()
        textToSpeech?.shutdown()
        textToSpeech = null
        isEngineReady = false
        pendingSpeechText = null
    }
}
