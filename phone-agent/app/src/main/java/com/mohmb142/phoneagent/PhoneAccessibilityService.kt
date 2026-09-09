package com.mohmb142.phoneagent

import android.accessibilityservice.AccessibilityService
import android.os.Handler
import android.os.Looper
import android.view.accessibility.AccessibilityEvent
import android.view.accessibility.AccessibilityNodeInfo
import java.util.Locale

class PhoneAccessibilityService : AccessibilityService() {
    companion object {
        @Volatile var instance: PhoneAccessibilityService? = null
        const val WHATSAPP = "com.whatsapp"
    }

    private val handler = Handler(Looper.getMainLooper())
    private var lastDetection = 0L

    override fun onServiceConnected() {
        super.onServiceConnected()
        instance = this
        AgentState.serviceConnected = true
    }

    override fun onAccessibilityEvent(event: AccessibilityEvent?) {
        if (event == null || event.packageName?.toString() != WHATSAPP) return
        val root = rootInActiveWindow ?: return
        val texts = ArrayList<String>()
        collectText(root, texts)
        val joined = texts.joinToString(" | ")
        if (looksLikeIncomingCall(joined)) {
            val now = System.currentTimeMillis()
            if (now - lastDetection > 2500) {
                lastDetection = now
                val caller = findCallerName(texts)
                AgentState.lastCallerName = caller
                AgentState.incomingWhatsAppCall = true
                VoiceAssistant.speak(this, if (caller != null) "مكالمة واردة من $caller" else "لديك مكالمة واردة على واتساب")
            }
        }
    }

    private fun looksLikeIncomingCall(s: String): Boolean {
        val x = s.lowercase(Locale.ROOT)
        val callWords = listOf("incoming call", "answer", "decline", "مكالمة واردة", "اتصال وارد", "رد", "رفض")
        return callWords.count { x.contains(it.lowercase(Locale.ROOT)) } >= 2
    }

    private fun findCallerName(texts: List<String>): String? {
        val bad = setOf("whatsapp", "answer", "decline", "رد", "رفض", "مكالمة واردة", "اتصال وارد", "incoming call")
        return texts.asSequence()
            .map { it.trim() }
            .filter { it.length in 2..80 }
            .filter { !bad.contains(it.lowercase(Locale.ROOT)) }
            .filter { !it.matches(Regex("[0-9+()\\- ]+")) }
            .firstOrNull()
    }

    private fun collectText(node: AccessibilityNodeInfo, out: MutableList<String>) {
        node.text?.toString()?.takeIf { it.isNotBlank() }?.let(out::add)
        node.contentDescription?.toString()?.takeIf { it.isNotBlank() }?.let(out::add)
        for (i in 0 until node.childCount) node.getChild(i)?.let { child -> collectText(child, out); child.recycle() }
    }

    fun clickText(vararg labels: String): Boolean {
        val root = rootInActiveWindow ?: return false
        for (label in labels) {
            val nodes = root.findAccessibilityNodeInfosByText(label)
            for (node in nodes) {
                var current: AccessibilityNodeInfo? = node
                while (current != null) {
                    if (current.isClickable) return current.performAction(AccessibilityNodeInfo.ACTION_CLICK)
                    current = current.parent
                }
            }
        }
        return false
    }

    fun answerWhatsAppCall(): Boolean {
        val ok = clickText("Answer", "رد", "قبول", "Accept")
        if (ok) AgentState.incomingWhatsAppCall = false
        return ok
    }

    fun globalHome() = performGlobalAction(GLOBAL_ACTION_HOME)
    fun globalBack() = performGlobalAction(GLOBAL_ACTION_BACK)
    fun notifications() = performGlobalAction(GLOBAL_ACTION_NOTIFICATIONS)

    override fun onInterrupt() {}

    override fun onDestroy() {
        if (instance === this) instance = null
        AgentState.serviceConnected = false
        super.onDestroy()
    }
}
