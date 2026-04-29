package com.saca.smartadaptiveclinicalassistant

import android.app.Application
import com.saca.smartadaptiveclinicalassistant.common.Constants.DEFAULT_LANGUAGE_TAG
import com.saca.smartadaptiveclinicalassistant.data.repository.MockTriageRepositoryImpl
import com.saca.smartadaptiveclinicalassistant.data.repository.TriageRepository
import com.saca.smartadaptiveclinicalassistant.di.appModule
import com.saca.smartadaptiveclinicalassistant.presentation.session.LocaleManager
import org.koin.android.ext.koin.androidContext
import org.koin.android.ext.koin.androidLogger
import org.koin.core.context.GlobalContext.startKoin
import org.koin.dsl.module

class MainApplication : Application() {
    override fun onCreate() {
        super.onCreate()

        startKoin {
            androidLogger()
            androidContext(this@MainApplication)
            modules(appModule)
        }
    }

    fun resetLocaleToEnglishForNewLaunch() {
        LocaleManager.apply(DEFAULT_LANGUAGE_TAG)
    }
}
