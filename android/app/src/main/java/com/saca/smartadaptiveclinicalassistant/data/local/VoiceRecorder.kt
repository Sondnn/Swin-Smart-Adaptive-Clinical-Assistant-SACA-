package com.saca.smartadaptiveclinicalassistant.data.local

import android.annotation.SuppressLint
import android.content.Context
import android.media.AudioFormat
import android.media.AudioRecord
import android.media.MediaRecorder
import java.io.File
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
    private val sampleRate = 16000
    private val channelConfig = AudioFormat.CHANNEL_IN_MONO
    private val audioFormat = AudioFormat.ENCODING_PCM_16BIT
    private val bufferSize = AudioRecord.getMinBufferSize(sampleRate, channelConfig, audioFormat)

    @SuppressLint("MissingPermission")
    fun startRecording(context: Context): Result<Unit> {
        if (isRecording) return Result.failure(IllegalStateException("Already recording"))

        val outputFile = File(context.cacheDir, "recording_${System.currentTimeMillis()}.wav")
        activeOutputFile = outputFile

        return try {
            audioRecord = AudioRecord(
                MediaRecorder.AudioSource.MIC,
                sampleRate,
                channelConfig,
                audioFormat,
                bufferSize
            )

            if (audioRecord?.state != AudioRecord.STATE_INITIALIZED) {
                return Result.failure(Exception("Failed to initialize recorder"))
            }

            audioRecord?.startRecording()
            isRecording = true

            recordingThread = thread(start = true) {
                writeAudioDataToFile(outputFile)
            }
            Result.success(Unit)
        } catch (e: Exception) {
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
    }

    private fun updateWavHeader(file: File) {
        val raf = RandomAccessFile(file, "rw")
        val totalAudioLen = file.length() - 44
        val totalDataLen = totalAudioLen + 36
        val byteRate = sampleRate * 2

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
        buffer.putShort(2.toShort())
        buffer.putShort(16.toShort())
        buffer.put("data".toByteArray())
        buffer.putInt(totalAudioLen.toInt())

        raf.seek(0)
        raf.write(header)
        raf.close()
    }

    fun stopRecording(): Result<File> {
        isRecording = false
        recordingThread?.join()
        recordingThread = null

        audioRecord?.apply {
            if (state == AudioRecord.STATE_INITIALIZED) stop()
            release()
        }
        audioRecord = null

        val file = activeOutputFile
        return if (file != null && file.exists()) {
            Result.success(file)
        } else {
            Result.failure(IllegalStateException("File missing"))
        }
    }

    fun cancelRecording() {
        isRecording = false
        recordingThread?.join()
        activeOutputFile?.delete()
        audioRecord?.release()
        audioRecord = null
    }
}