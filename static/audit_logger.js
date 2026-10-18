/**
 * Comprehensive Audit Logger
 * Captures all user interactions, API calls, and system responses
 * Sends logs to backend for persistent storage
 */

class AuditLogger {
    constructor() {
        this.sessionId = this.generateSessionId();
        this.logQueue = [];
        this.maxQueueSize = 100;
        this.flushInterval = 5000; // 5 seconds
        this.isFlushing = false;
        this.connectionErrorLogged = false;
        
        // Start periodic flush
        setInterval(() => this.flushLogs(), this.flushInterval);
        
        // Log session start
        this.log('SESSION_START', { timestamp: new Date().toISOString(), userAgent: navigator.userAgent });
        
        // Capture all user interactions
        this.setupGlobalEventListeners();
    }
    
    generateSessionId() {
        return 'sess_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }
    
    setupGlobalEventListeners() {
        // Capture all clicks
        document.addEventListener('click', (e) => {
            const target = e.target;
            const elementInfo = this.getElementInfo(target);
            this.log('CLICK', elementInfo);
        }, true);
        
        // Capture all input changes
        document.addEventListener('input', (e) => {
            const target = e.target;
            if (target.tagName === 'INPUT' || target.tagName === 'TEXTAREA' || target.tagName === 'SELECT') {
                const elementInfo = this.getElementInfo(target);
                elementInfo.value = target.value;
                elementInfo.valueLength = target.value.length;
                this.log('INPUT_CHANGE', elementInfo);
            }
        }, true);
        
        // Capture all focus events
        document.addEventListener('focus', (e) => {
            const target = e.target;
            const elementInfo = this.getElementInfo(target);
            this.log('FOCUS', elementInfo);
        }, true);
        
        // Capture all blur events
        document.addEventListener('blur', (e) => {
            const target = e.target;
            const elementInfo = this.getElementInfo(target);
            this.log('BLUR', elementInfo);
        }, true);
        
        // Capture form submissions
        document.addEventListener('submit', (e) => {
            const target = e.target;
            const elementInfo = this.getElementInfo(target);
            this.log('FORM_SUBMIT', elementInfo);
        }, true);
        
        // Capture keyboard events
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' || e.key === 'Escape' || e.ctrlKey || e.altKey) {
                const elementInfo = this.getElementInfo(e.target);
                elementInfo.key = e.key;
                elementInfo.ctrlKey = e.ctrlKey;
                elementInfo.altKey = e.altKey;
                elementInfo.shiftKey = e.shiftKey;
                this.log('KEYDOWN', elementInfo);
            }
        }, true);
        
        // Capture API calls (intercept fetch)
        this.interceptFetch();
        
        // Capture errors
        window.addEventListener('error', (e) => {
            this.log('ERROR', {
                message: e.message,
                filename: e.filename,
                lineno: e.lineno,
                colno: e.colno,
                stack: e.error?.stack
            });
        });
        
        // Capture unhandled promise rejections
        window.addEventListener('unhandledrejection', (e) => {
            this.log('UNHANDLED_REJECTION', {
                reason: e.reason,
                promise: e.promise
            });
        });
    }
    
    getElementInfo(element) {
        const info = {
            tagName: element.tagName,
            id: element.id,
            className: element.className,
            type: element.type,
            name: element.name,
            textContent: element.textContent?.substring(0, 100),
            href: element.href,
            src: element.src
        };
        
        // Add data attributes
        for (const attr of element.attributes) {
            if (attr.name.startsWith('data-')) {
                info[attr.name] = attr.value;
            }
        }
        
        return info;
    }
    
    interceptFetch() {
        const originalFetch = window.fetch;
        const self = this;
        
        window.fetch = async function(...args) {
            const url = args[0];
            const options = args[1] || {};
            
            // Log request
            self.log('API_REQUEST', {
                url: url,
                method: options.method || 'GET',
                headers: options.headers,
                hasBody: !!options.body
            });
            
            const startTime = Date.now();
            
            try {
                const response = await originalFetch.apply(this, args);
                const duration = Date.now() - startTime;
                
                // Log response
                self.log('API_RESPONSE', {
                    url: url,
                    method: options.method || 'GET',
                    status: response.status,
                    statusText: response.statusText,
                    duration: duration,
                    ok: response.ok
                });
                
                return response;
            } catch (error) {
                const duration = Date.now() - startTime;
                
                // Log error
                self.log('API_ERROR', {
                    url: url,
                    method: options.method || 'GET',
                    error: error.message,
                    duration: duration
                });
                
                throw error;
            }
        };
    }
    
    log(actionType, data) {
        const logEntry = {
            timestamp: new Date().toISOString(),
            sessionId: this.sessionId,
            actionType: actionType,
            data: data,
            page: window.location.pathname,
            url: window.location.href
        };
        
        this.logQueue.push(logEntry);
        
        // Flush if queue is full
        if (this.logQueue.length >= this.maxQueueSize) {
            this.flushLogs();
        }
        
        // Also log to console for debugging
        console.log('[AUDIT]', actionType, data);
    }
    
    async flushLogs() {
        if (this.isFlushing || this.logQueue.length === 0) {
            return;
        }
        
        this.isFlushing = true;
        const logsToSend = [...this.logQueue];
        this.logQueue = [];
        
        try {
            const response = await fetch('/audit/log', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ logs: logsToSend })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
        } catch (error) {
            // Only log once per batch to avoid console spam
            if (!this.connectionErrorLogged) {
                console.warn('[AUDIT] Server unavailable - audit logs will be queued locally');
                this.connectionErrorLogged = true;
            }
            // Re-add failed logs to queue (limit queue size to prevent memory issues)
            if (this.logQueue.length < this.maxQueueSize * 2) {
                this.logQueue.unshift(...logsToSend);
            } else {
                // Drop oldest logs if queue is too large
                this.logQueue.unshift(...logsToSend.slice(0, this.maxQueueSize));
            }
        } finally {
            this.isFlushing = false;
        }
    }
    
    // Manual logging for custom events
    logCustom(actionType, data) {
        this.log(actionType, data);
    }
    
    // Log preview-specific events
    logPreviewEvent(eventType, data) {
        this.log('PREVIEW_' + eventType, {
            ...data,
            timestamp: new Date().toISOString()
        });
    }
    
    // Log DOM state changes
    logDOMState(elementId, property, value) {
        this.log('DOM_STATE_CHANGE', {
            element_id: elementId,
            property: property,
            value: value
        });
    }
    
    // Log API response details
    logAPIResponseDetails(endpoint, status, data) {
        this.log('API_RESPONSE_DETAILS', {
            endpoint: endpoint,
            status: status,
            data_keys: data ? Object.keys(data) : [],
            has_pair_preview: !!data?.pair_preview,
            has_secondary_config: !!data?.pair_preview?.secondary_config_preview,
            config_preview_length: data?.config_preview?.length || 0
        });
    }
}

// Initialize audit logger when DOM is ready
let auditLogger;
if (typeof document !== 'undefined') {
    document.addEventListener('DOMContentLoaded', () => {
        auditLogger = new AuditLogger();
    });
}

// Make available globally
window.auditLogger = auditLogger;
