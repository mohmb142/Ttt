package com.mohmb142.phoneagent

object AgentState {
    @Volatile var lastCallerName: String? = null
    @Volatile var incomingWhatsAppCall: Boolean = false
    @Volatile var serviceConnected: Boolean = false
    @Volatile var conversationMode: Boolean = false
}
