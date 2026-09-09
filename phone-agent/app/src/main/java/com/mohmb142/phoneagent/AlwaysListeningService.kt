package com.mohmb142.phoneagent

import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.Service
import android.content.Intent
import android.os.Build
import android.os.IBinder
import android.speech.SpeechRecognizer
import android.speech.RecognizerIntent
import android.os.Bundle
import android.speech.RecognitionListener

class AlwaysListeningService : Service() {
    private var recognizer: SpeechRecognizer? = null
    private val channelId = "phone_agent_voice"

    override fun onCreate() {
        super.onCreate()
        createChannel()
        val notification = Notification.Builder(this, channelId)
            .setContentTitle("مساعد الهاتف")
            .setContentText("الاستماع الصوتي مفعّل — اضغط إيقاف من التطبيق لإيقافه")
            .setSmallIcon(android.R.drawable.ic_btn_speak_now)
            .setOngoing(true)
            .build()
        if (Build.VERSION.SDK_INT >= 29) startForeground(7, notification, android.content.pm.ServiceInfo.FOREGROUND_SERVICE_TYPE_MICROPHONE)
        else startForeground(7, notification)
        listenAgain()
    }

    private fun listenAgain() {
        if (isFinishing()) return
        if (!SpeechRecognizer.isRecognitionAvailable(this)) return
        recognizer?.destroy()
        recognizer = SpeechRecognizer.createSpeechRecognizer(this).also { r ->
            r.setRecognitionListener(object : RecognitionListener {
                override fun onResults(results: Bundle?) {
                    results?.getStringArrayList(SpeechRecognizer.RESULTS_RECOGNITION)?.firstOrNull()?.let { command ->
                        handle(command)
                    }
                    listenAgain()
                }
                override fun onError(error: Int) { if (!isFinishing()) listenAgain() }
                override fun onReadyForSpeech(params: Bundle?) {}
                override fun onBeginningOfSpeech() {}
                override fun onRmsChanged(rmsdB: Float) {}
                override fun onBufferReceived(buffer: ByteArray?) {}
                override fun onEndOfSpeech() {}
                override fun onPartialResults(partialResults: Bundle?) {}
                override fun onEvent(eventType: Int, params: Bundle?) {}
            })
            val i = Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH).apply {
                putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL, RecognizerIntent.LANGUAGE_MODEL_FREE_FORM)
                putExtra(RecognizerIntent.EXTRA_LANGUAGE, "ar-SA")
            }
            r.startListening(i)
        }
    }

    private fun handle(command: String) {
        val t = command.lowercase()
        when {
            t.contains("من المتصل") || t.contains("مين المتصل") -> {
                val name = AgentState.lastCallerName
                VoiceAssistant.speak(this, if (name != null) "المتصل هو $name" else "لا أستطيع تحديد اسم المتصل")
            }
            t.contains("أجب") || t.contains("اجب") || t.contains("رد") -> {
                PhoneAccessibilityService.instance?.answerWhatsAppCall()
            }
            t.contains("رجوع") -> PhoneAccessibilityService.instance?.globalBack()
            t.contains("الرئيسية") -> PhoneAccessibilityService.instance?.globalHome()
        }
    }

    private fun createChannel() {
        if (Build.VERSION.SDK_INT >= 26) {
            val nm = getSystemService(NotificationManager::class.java)
            nm.createNotificationChannel(NotificationChannel(channelId, "مساعد الهاتف", NotificationManager.IMPORTANCE_LOW))
        }
    }

    private fun isFinishing(): Boolean = AgentState.conversationMode.not()

    override fun onDestroy() {
        recognizer?.destroy()
        recognizer = null
        AgentState.conversationMode = false
        super.onDestroy()
    }

    override fun onBind(intent: Intent?): IBinder? = null
}
