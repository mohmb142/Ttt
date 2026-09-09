package com.mohmb142.phoneagent

import android.Manifest
import android.app.Activity
import android.content.Intent
import android.content.pm.PackageManager
import android.os.Bundle
import android.provider.Settings
import android.view.Gravity
import android.widget.Button
import android.widget.LinearLayout
import android.widget.TextView

class MainActivity : Activity() {
    private lateinit var status: TextView

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        if (checkSelfPermission(Manifest.permission.RECORD_AUDIO) != PackageManager.PERMISSION_GRANTED) {
            requestPermissions(arrayOf(Manifest.permission.RECORD_AUDIO), 10)
        }

        val box = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            gravity = Gravity.CENTER_HORIZONTAL
            setPadding(36, 50, 36, 40)
        }
        val title = TextView(this).apply { text = "مساعد الهاتف الذكي"; textSize = 28f }
        status = TextView(this).apply { text = stateText(); textSize = 17f; setPadding(0, 24, 0, 24) }
        val accessibility = Button(this).apply { text = "1) تفعيل صلاحية التحكم" }
        val listen = Button(this).apply { text = "🎙️ تحدث الآن" }
        val caller = Button(this).apply { text = "👤 من المتصل؟" }
        val answer = Button(this).apply { text = "📞 الرد على مكالمة واتساب" }
        val always = Button(this).apply { text = "🎧 تشغيل/إيقاف الاستماع الدائم" }

        box.addView(title); box.addView(status); box.addView(accessibility); box.addView(listen); box.addView(caller); box.addView(answer); box.addView(always)
        setContentView(box)

        accessibility.setOnClickListener { startActivity(Intent(Settings.ACTION_ACCESSIBILITY_SETTINGS)) }
        listen.setOnClickListener { listenForCommand() }
        caller.setOnClickListener { sayCaller() }
        answer.setOnClickListener { answerCall() }
        always.setOnClickListener { toggleAlwaysListening() }
    }

    private fun listenForCommand() {
        status.text = "أستمع... قل: من المتصل، أجب، رجوع، الرئيسية"
        VoiceAssistant.listen(this, ::handleCommand) { status.text = "تعذر تشغيل التعرف الصوتي" }
    }

    private fun handleCommand(raw: String) {
        val text = raw.lowercase()
        status.text = "سمعت: $raw"
        when {
            text.contains("من المتصل") || text.contains("مين المتصل") || text.contains("من اتصل") -> sayCaller()
            text.contains("أجب") || text.contains("اجب") || text.contains("رد على المكالمة") -> answerCall()
            text.contains("ماذا يريد") || text.contains("اسأله") -> {
                answerCall()
                VoiceAssistant.speak(this, "تم الرد. سأحاول تشغيل وضع المحادثة. ملاحظة: أندرويد لا يسمح للتطبيق بقراءة صوت الطرف الآخر من مكالمة واتساب بشكل موثوق.")
            }
            text.contains("الرئيسية") -> PhoneAccessibilityService.instance?.globalHome()
            text.contains("رجوع") -> PhoneAccessibilityService.instance?.globalBack()
            text.contains("الإشعارات") -> PhoneAccessibilityService.instance?.notifications()
            else -> VoiceAssistant.speak(this, "لم أفهم الأمر")
        }
    }

    private fun sayCaller() {
        val name = AgentState.lastCallerName
        VoiceAssistant.speak(this, if (name != null) "المتصل هو $name" else "لا أملك اسم المتصل حالياً")
        status.text = if (name != null) "المتصل: $name" else "لم يتم التعرف على اسم المتصل"
    }

    private fun answerCall() {
        val ok = PhoneAccessibilityService.instance?.answerWhatsAppCall() == true
        if (ok) {
            status.text = "تم الضغط على زر الرد في واتساب"
            VoiceAssistant.speak(this, "تم الرد على المكالمة")
        } else {
            status.text = "لم أجد زر الرد. افتح شاشة مكالمة واتساب وفعّل صلاحية Accessibility."
            VoiceAssistant.speak(this, "لم أجد زر الرد في شاشة واتساب")
        }
    }

    private fun toggleAlwaysListening() {
        val intent = Intent(this, AlwaysListeningService::class.java)
        if (AgentState.conversationMode) {
            stopService(intent)
            AgentState.conversationMode = false
            status.text = "الاستماع الدائم متوقف"
        } else {
            if (android.os.Build.VERSION.SDK_INT >= 26) startForegroundService(intent) else startService(intent)
            AgentState.conversationMode = true
            status.text = "الاستماع الدائم يعمل — يمكنك قول: من المتصل"
        }
    }

    private fun stateText() = "Android 10+\nفعّل Accessibility أولاً، ثم جرّب مكالمة واتساب تجريبية."
}
