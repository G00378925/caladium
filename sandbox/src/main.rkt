#lang racket
;
;  main.rkt
;  caladium
;
;  Created by Declan Kelly on 22-10-2022.
;  Copyright © 2022 Declan Kelly. All rights reserved.
;

(require json)
(require net/base64)

; Locations of executables
(define python-location
    (string-append (getenv "windir") "\\py.exe"))
(define sandboxie-start-location
    (string-append (getenv "ProgramFiles") "\\Sandboxie\\Start.exe"))
(define procmon-location
    (string-append (getenv "SystemDrive") "\\SysinternalsSuite\\Procmon64.exe"))

(define port-number 37372)

; Execute an execute a file with a list of parameters
(define (subprocess-and-close-ports executable-location subprocess-parameters)
    (begin (define-values (subprocess-obj out in err)
        (apply subprocess #f #f #f executable-location subprocess-parameters))
        (close-input-port out) (close-output-port in) (close-input-port err)
        subprocess-obj))

; Get a list of pids in the sandbox
(define (listpids-in-sandbox)
    (begin (define-values (subprocess-obj out in err)
        (subprocess #f #f #f sandboxie-start-location "/listpids"))
        (define listpids-list (string-split (port->string out) "\r\n"))
        (subprocess-wait subprocess-obj)
        (close-input-port out) (close-output-port in) (close-input-port err)
        listpids-list))

; Writes patterns to a file
(define (write-patterns-to-file patterns)
    (begin
        (define malicious-patterns-file-location
            (path->string (make-temporary-file "caladium_patterns_~a.txt")))
        (delete-file (string->path malicious-patterns-file-location))
        (display-to-file (string-join patterns "\n") (string->path malicious-patterns-file-location))
        malicious-patterns-file-location))

; Output JSON obj to a port
(define (output-json hash-obj out)
    (begin
        (define json-out-string
            (with-output-to-string
                (lambda () (write-json hash-obj))))
        (display (integer->integer-bytes (string-length json-out-string) 4 #f #t) out)
        (display json-out-string out)
        (flush-output out)))

(define (send-message text out)
    (output-json (hash 'type "message" 'text text) out))

(define (send-progress value out)
    (output-json (hash 'type "progress" 'value value) out))

(define (send-state state out)
    (output-json (hash 'type "state" 'state state) out))

(define (send-update text value out)
    (begin (send-message text out) (send-progress value out)))

(define (terminate-sandboxie)
    (subprocess-and-close-ports sandboxie-start-location (list "/terminate_all")))
(define (terminate-procmon)
    (system (string-join (list procmon-location "/Terminate") " ")))

(define (run-in-sandbox executable-location out)
    (begin
        (define procmon-pml-file-location
            (path->string (make-temporary-file "caladium_~a.pml")))
        (define procmon-csv-file-location
            (path->string (make-temporary-file "caladium_~a.csv")))

        (send-update "[*] Starting Process Monitor" 10 out)
        (define procmon-subprocess (subprocess-and-close-ports procmon-location
            (list "/Minimized" "/BackingFile" procmon-pml-file-location)))

        (send-update "[*] Executing file in Sandboxie" 20 out)
        (define sandboxed-subprocess (subprocess-and-close-ports sandboxie-start-location
            (list "/wait" executable-location)))

        (sleep 10) ; Pause for a bit, to avoid racing
        (define listpids-list (listpids-in-sandbox))

        ; Terminate process if it runs for too long
        (define (sandbox-timeout)
            (begin
                (sleep 20) (terminate-sandboxie)))
        (thread sandbox-timeout)

        (subprocess-wait sandboxed-subprocess)

        ; Terminate procmon and wait for it to close
        (terminate-procmon)
        (subprocess-wait procmon-subprocess)

        (system (string-join (list procmon-location "/OpenLog" procmon-pml-file-location
            "/SaveAs" procmon-csv-file-location) " "))

        (send-update "[*] Filtering system calls" 25 out)
        (system (string-join (append (list python-location "procmon_csv_filter.py"
            procmon-csv-file-location executable-location) listpids-list) " "))

        (delete-file (string->path procmon-pml-file-location))
        procmon-csv-file-location))

; Need to open TCP even if its being used by another process
(define tcp-obj (tcp-listen port-number 8 #f "0.0.0.0"))

(define (analyse-syscalls syscall-list-file-location malicious-patterns-file-location out)
    (begin
        (define-values (subprocess-obj python-out python-in python-err)
            (subprocess #f #f #f python-location "syscall_analysis.py" syscall-list-file-location malicious-patterns-file-location))
        (display (port->string python-out) out)
        (flush-output out)
        (close-input-port python-out) (close-output-port python-in) (close-input-port python-err)
        subprocess-obj))

(define (static-analysis file-location out)
    (begin
        (define-values (subprocess-obj python-out python-in python-err)
            (subprocess #f #f #f python-location "static_analysis.py" file-location))
        (display (port->string python-out) out)
        (flush-output out)
        (close-input-port python-out) (close-output-port python-in) (close-input-port python-err)
        subprocess-obj))

(define scan-in-progress #f)

; Execute a file in a sandbox
(define (analyse-file json-obj out)
    (begin
        ; Timeout if a scan is taking too long
        (define (analysis-timeout-kill)
            (begin
                (sleep 60) ; Wait for 60 seconds
                (if scan-in-progress
                    (begin
                        (terminate-sandboxie) (terminate-procmon)
                        (set! scan-in-progress #f)) (void))))
        (thread analysis-timeout-kill) ; Start timeout thread

        (define dynamic-analysis-enabled (hash-ref json-obj 'dynamic-analysis))

        (send-update (string-append "[*] Beginning analysis of \""
            (hash-ref json-obj 'file-name) "\"") 0 out)
        (set! scan-in-progress #t)

        ; Write file to disk
        (define file-location
            (string-append (path->string (make-temporary-directory)) "\\" (hash-ref json-obj 'file-name)))
        (display-to-file (base64-decode (string->bytes/utf-8 (hash-ref json-obj 'file-data))) (string->path file-location))

        ; Check if dynamic analysis is enabled
        (if dynamic-analysis-enabled
            (let ([malicious-patterns-file-location (write-patterns-to-file (hash-ref json-obj 'patterns))]
                [procmon-csv-file-location (run-in-sandbox file-location out)])
                (send-update "[*] Beginning analysis of system calls" 25 out)

                ; Wait for the syscall analysis to complete
                (subprocess-wait
                    (analyse-syscalls procmon-csv-file-location malicious-patterns-file-location out))

                (delete-file (string->path procmon-csv-file-location))
                (delete-file (string->path malicious-patterns-file-location))

                (send-message "[+] Dynamic analysis complete" out))
            (send-message "[!] Dynamic analysis disabled, Skipping" out))

        ; Run static analysis
        (send-update "[*] Beginning static analysis" 50 out)

        (define static-analysis-subprocess (static-analysis file-location out))
        (subprocess-wait static-analysis-subprocess) ; Wait for the analysis to complete
        
        (send-update "[+] Static analysis complete" 100 out)
        (send-state "clean" out)
        
        ; Set scan-in-progress to false
        (set! scan-in-progress #f)))

; Handle a ping request
(define (ping out)
    (output-json "pong" out))

(define (kill-sandbox)
    (begin (tcp-close tcp-obj) (exit)))

; Handle a request
(define (poll-for-request)
    (begin (define-values (in out) (tcp-accept tcp-obj))
        (thread poll-for-request)
        (define json-obj (read-json in))

        ; Check if a scan is already in progress
        (if (not scan-in-progress)
            (begin
                (case (hash-ref json-obj 'command)
                    [("ping") (ping out)]
                    [("kill") (kill-sandbox)]
                    [("run") (analyse-file json-obj out)]))
            (begin
                (send-message "Scan already in progress . . ." out)
                (send-progress 100 out)
                (send-state "complete" out)))

        (close-input-port in) (close-output-port out)))

(display (string-append "Listening on port "
    (number->string port-number) "\n") (current-error-port))

; Main loop of execution
(poll-for-request)
(define (wait-for-threads)
    (begin (sleep) (wait-for-threads)))
(wait-for-threads)
