package com.saca.smartadaptiveclinicalassistant.data.local

import android.annotation.SuppressLint
import android.content.Context
import android.media.AudioFormat
import android.media.AudioRecord
import android.media.MediaRecorder
import android.util.Log
import java.io.File
import java.io.FileInputStream
import java.io.FileOutputStream
import java.io.RandomAccessFile
import java.nio.ByteBuffer
import java.nio.ByteOrder
import kotlin.concurrent.thread

class VoiceRecorder {
    private var audioRecord: AudioRecord? = null
    private var recordingThread: Thread? = null
    @Volatile
    private var isRecording = false
    private var activeOutputFile: File? = null
    private val sampleRate = 40000
    private val channelConfig = AudioFormat.CHANNEL_IN_MONO
    private val audioFormat = AudioFormat.ENCODING_PCM_32BIT

    private val bufferSize = AudioRecord.getMinBufferSize(sampleRate, channelConfig, audioFormat)


    @SuppressLint("MissingPermission")
    fun startRecording(context: Context): Result<Unit> {
        if (isRecording) {
            return Result.failure(IllegalStateException("Recording is already in progress"))
        }

        val outputFile = File(
            context.cacheDir,
            "symptom_recording_${System.currentTimeMillis()}.wav"
        )
        activeOutputFile = outputFile

        return try {
            audioRecord = AudioRecord(
                MediaRecorder.AudioSource.VOICE_RECOGNITION,
                sampleRate,
                channelConfig,
                audioFormat,
                bufferSize
            )

            if (audioRecord?.state != AudioRecord.STATE_INITIALIZED) {
                return Result.failure(Exception("AudioRecord failed to initialize"))
            }

            audioRecord?.startRecording()
            isRecording = true

            recordingThread = thread(start = true) {
                writeAudioDataToFile(outputFile)
            }

            Result.success(Unit)
        } catch (e: Exception) {
            stopRecording()
            Result.failure(e)
        }
    }

    private fun writeAudioDataToFile(file: File) {
        val data = ByteArray(bufferSize)
        val outputStream = FileOutputStream(file)

        outputStream.write(ByteArray(44))

        while (isRecording) {
            val read = audioRecord?.read(data, 0, bufferSize) ?: 0
            if (read > 0) {
                outputStream.write(data, 0, read)
            }
        }

        outputStream.close()

        updateWavHeader(file)

        verifyFileHeader(file)
    }

    private fun updateWavHeader(file: File) {
        val raf = RandomAccessFile(file, "rw")
        val totalAudioLen = file.length() - 44
        val totalDataLen = totalAudioLen + 36
        val bytesPerSample = 4
        val byteRate = sampleRate * bytesPerSample

        val header = ByteArray(44)
        val buffer = ByteBuffer.wrap(header).order(ByteOrder.LITTLE_ENDIAN)

        buffer.put("RIFF".toByteArray())
        buffer.putInt(totalDataLen.toInt())
        buffer.put("WAVE".toByteArray())
        buffer.put("fmt ".toByteArray())
        buffer.putInt(16)
        buffer.putShort(1.toShort())
        buffer.putShort(1.toShort())
        buffer.putInt(sampleRate)
        buffer.putInt(byteRate)
        buffer.putShort(bytesPerSample.toShort())
        buffer.putShort(32.toShort())
        buffer.put("data".toByteArray())
        buffer.putInt(totalAudioLen.toInt())

        raf.seek(0)
        raf.write(header)
        raf.close()
    }

    private fun verifyFileHeader(file: File) {
        try {
            val inputStream = FileInputStream(file)
            val header = ByteArray(44)
            inputStream.read(header)
            inputStream.close()

            // Clean up the header to show only letters/numbers
            val headerText = String(header.filter { it in 32..126 }.toByteArray())

            Log.d("VoiceRecorder", "--- ANDROID SIDE CONFIRMATION ---")
            Log.d("VoiceRecorder", "1. Path: ${file.absolutePath}")
            Log.d("VoiceRecorder", "2. Size: ${file.length()} bytes")
            Log.d("VoiceRecorder", "3. Header Content: $headerText")
            Log.d("VoiceRecorder", "--------------------------------")
        } catch (e: Exception) {
            Log.e("VoiceRecorder", "Could not verify header: ${e.message}")
        }
    }

    fun stopRecording(): Result<File> {
        isRecording = false
        recordingThread?.join()
        recordingThread = null

        audioRecord?.apply {
            if (state == AudioRecord.STATE_INITIALIZED) {
                stop()
            }
            release()
        }
        audioRecord = null

        val file = activeOutputFile
        return if (file != null && file.exists()) {
            Result.success(file)
        } else {
            Result.failure(IllegalStateException("Recorded WAV file missing"))
        }
    }

    fun cancelRecording() {
        stopRecording()
        activeOutputFile?.delete()
        activeOutputFile = null
    }
}
