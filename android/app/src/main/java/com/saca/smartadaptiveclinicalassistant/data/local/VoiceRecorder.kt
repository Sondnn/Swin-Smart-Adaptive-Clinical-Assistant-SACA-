package com.saca.smartadaptiveclinicalassistant.data.local

import android.content.Context
import android.media.MediaRecorder
import android.os.Build
import java.io.File

class VoiceRecorder {
    private var mediaRecorder: MediaRecorder? = null
    private var activeOutputFile: File? = null

    fun startRecording(context: Context): Result<Unit> {
        if (mediaRecorder != null) {
            return Result.failure(IllegalStateException("Recording is already in progress"))
        }

        val outputFile = File(
            context.cacheDir,
            "symptom_recording_${System.currentTimeMillis()}.m4a"
        )

        return try {
            val recorder = createMediaRecorder(context)
            recorder.setAudioSource(MediaRecorder.AudioSource.MIC)
            recorder.setOutputFormat(MediaRecorder.OutputFormat.MPEG_4)
            recorder.setAudioEncoder(MediaRecorder.AudioEncoder.AAC)
            recorder.setOutputFile(outputFile.absolutePath)
            recorder.prepare()
            recorder.start()

            mediaRecorder = recorder
            activeOutputFile = outputFile
            Result.success(Unit)
        } catch (error: Exception) {
            safeReleaseRecorder()
            outputFile.delete()
            Result.failure(error)
        }
    }

    fun stopRecording(): Result<File> {
        val recorder = mediaRecorder ?: return Result.failure(
            IllegalStateException("Recording has not started")
        )
        val outputFile = activeOutputFile

        return try {
            recorder.stop()
            if (outputFile != null && outputFile.exists()) {
                Result.success(outputFile)
            } else {
                Result.failure(IllegalStateException("Recorded audio file is missing"))
            }
        } catch (error: Exception) {
            outputFile?.delete()
            Result.failure(error)
        } finally {
            safeReleaseRecorder()
        }
    }

    fun cancelRecoding() {
        val recorder = mediaRecorder ?: return

        try {
            recorder.stop()
        } catch (_: Exception) {

        } finally {
            val outputFile = activeOutputFile
            safeReleaseRecorder()
            outputFile?.delete()
        }
    }

    private fun safeReleaseRecorder() {
        mediaRecorder?.apply {
            reset()
            release()
        }

        mediaRecorder = null
        activeOutputFile = null
    }


    private fun createMediaRecorder(context: Context): MediaRecorder {
        return if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
            MediaRecorder(context)
        } else {
            createLegacyMediaRecorder()
        }
    }

    @Suppress("DEPRECATION")
    private fun createLegacyMediaRecorder(): MediaRecorder {
        return MediaRecorder()
    }
}