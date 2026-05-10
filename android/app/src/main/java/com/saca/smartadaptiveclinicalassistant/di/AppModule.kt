package com.saca.smartadaptiveclinicalassistant.di

import com.saca.smartadaptiveclinicalassistant.common.Constants
import com.saca.smartadaptiveclinicalassistant.data.remote.TriageApi
import com.saca.smartadaptiveclinicalassistant.data.repository.TriageRepositoryImpl
import com.saca.smartadaptiveclinicalassistant.domain.repository.TriageRepository
import com.saca.smartadaptiveclinicalassistant.domain.use_case.AnalyzeSymptomsUseCase
import com.saca.smartadaptiveclinicalassistant.domain.use_case.SpeechToTextUseCase
import com.saca.smartadaptiveclinicalassistant.presentation.home.HomeViewModel
import com.saca.smartadaptiveclinicalassistant.presentation.session.SessionViewModel
import com.saca.smartadaptiveclinicalassistant.presentation.triage_form.TriageFormViewModel
import com.saca.smartadaptiveclinicalassistant.presentation.triage_result.TriageResultViewModel
import okhttp3.OkHttpClient
import org.koin.dsl.module
import org.koin.core.module.dsl.viewModel
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import java.util.concurrent.TimeUnit

val appModule = module {
    single {
        OkHttpClient.Builder()
            .connectTimeout(60, TimeUnit.SECONDS)
            .readTimeout(60, TimeUnit.SECONDS)
            .writeTimeout(60, TimeUnit.SECONDS)
            .build()
    }
    single {
        Retrofit.Builder()
            .baseUrl(Constants.BASE_URL)
            .client(get())
            .addConverterFactory(GsonConverterFactory.create())
            .build()
    }

    single {
        get<Retrofit>().create(TriageApi::class.java)
    }

    single<TriageRepository> { TriageRepositoryImpl(get()) }

    single { SpeechToTextUseCase(get()) }

    single { AnalyzeSymptomsUseCase(get()) }

    single { SessionViewModel() }

    viewModel { HomeViewModel() }

    viewModel { TriageFormViewModel(get()) }

    viewModel { TriageResultViewModel(get()) }
}