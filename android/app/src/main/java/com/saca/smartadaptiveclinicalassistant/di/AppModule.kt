package com.saca.smartadaptiveclinicalassistant.di

import androidx.lifecycle.viewmodel.compose.viewModel
import com.saca.smartadaptiveclinicalassistant.data.repository.MockTriageRepositoryImpl
import com.saca.smartadaptiveclinicalassistant.data.repository.TriageRepository
import com.saca.smartadaptiveclinicalassistant.presentation.session.SessionViewModel
import org.koin.dsl.module

val appModule = module {
    single<TriageRepository> { MockTriageRepositoryImpl() }
    single { SessionViewModel() }
}