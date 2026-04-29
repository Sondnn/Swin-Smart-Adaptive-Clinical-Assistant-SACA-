package com.saca.smartadaptiveclinicalassistant.di

import com.saca.smartadaptiveclinicalassistant.data.repository.MockTriageRepositoryImpl
import com.saca.smartadaptiveclinicalassistant.data.repository.TriageRepository
import com.saca.smartadaptiveclinicalassistant.presentation.home.HomeViewModel
import com.saca.smartadaptiveclinicalassistant.presentation.session.SessionViewModel
import org.koin.dsl.module
import org.koin.core.module.dsl.viewModel

val appModule = module {
    single<TriageRepository> { MockTriageRepositoryImpl() }

    single { SessionViewModel() }

    viewModel { HomeViewModel() }
}