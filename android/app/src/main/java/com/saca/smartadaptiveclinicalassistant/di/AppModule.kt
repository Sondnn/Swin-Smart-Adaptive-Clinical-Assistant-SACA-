package com.saca.smartadaptiveclinicalassistant.di

import com.saca.smartadaptiveclinicalassistant.data.repository.MockTriageRepositoryImpl
import com.saca.smartadaptiveclinicalassistant.domain.repository.TriageRepository
import com.saca.smartadaptiveclinicalassistant.domain.use_case.ExtractSymptomsUseCase
import com.saca.smartadaptiveclinicalassistant.domain.use_case.SpeechToTextUseCase
import com.saca.smartadaptiveclinicalassistant.presentation.home.HomeViewModel
import com.saca.smartadaptiveclinicalassistant.presentation.session.SessionViewModel
import com.saca.smartadaptiveclinicalassistant.presentation.triage_form.TriageFormViewModel
import org.koin.dsl.module
import org.koin.core.module.dsl.viewModel

val appModule = module {
    single<TriageRepository> { MockTriageRepositoryImpl() }
    single { SpeechToTextUseCase(get()) }
    single { ExtractSymptomsUseCase(get()) }

    single { SessionViewModel() }

    viewModel { HomeViewModel() }

    viewModel { TriageFormViewModel(get(), get()) }
}