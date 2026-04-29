package com.saca.smartadaptiveclinicalassistant

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.appcompat.app.AppCompatActivity
import androidx.appcompat.app.AppCompatDelegate
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.tooling.preview.Preview
import com.saca.smartadaptiveclinicalassistant.presentation.navigation.SacaNavGraph
import com.saca.smartadaptiveclinicalassistant.ui.theme.SmartAdaptiveClinicalAssistantTheme

class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        if (savedInstanceState == null) {
            (application as MainApplication).resetLocaleToEnglishForNewLaunch()
        }
        enableEdgeToEdge()
        setContent {
            SmartAdaptiveClinicalAssistantTheme {
                Scaffold(modifier = Modifier.fillMaxSize()) { innerPadding ->
                    SacaNavGraph(
                        modifier = Modifier.padding(innerPadding)
                    )
                }
            }
        }
    }
}
