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

(define (run-in-sandbox executable-location out)
    (begin
        (define procmon-pml-file-location
            (path->string (make-temporary-file "caladium_~a.pml")))
        (define procmon-csv-file-location
            (path->string (make-temporary-file "caladium_~a.csv")))

        (send-message "Starting process monitor" out)
        (send-progress 10 out)
        (define procmon-subprocess (subprocess-and-close-ports procmon-location
            (list "/Minimized" "/BackingFile" procmon-pml-file-location)))

        (send-message "Executing file in sandboxie" out)
        (send-progress 20 out)
        (define sandboxed-subprocess (subprocess-and-close-ports sandboxie-start-location
            (list "/wait" executable-location)))

        (sleep 1)
        (define listpids-list (listpids-in-sandbox))
        (subprocess-wait sandboxed-subprocess)

        (system (string-join (list procmon-location "/Terminate") " "))
        (subprocess-wait procmon-subprocess)

        (system (string-join (list procmon-location "/OpenLog" procmon-pml-file-location
            "/SaveAs" procmon-csv-file-location) " "))

        (send-message "Filtering system calls" out)
        (system (string-join (append (list python-location "procmon_csv_filter.py" procmon-csv-file-location)
            listpids-list) " "))

        (delete-file (string->path procmon-pml-file-location))
        procmon-csv-file-location))

(define semaphore-obj (make-semaphore 1))
(define tcp-obj (tcp-listen 8080 8 #f "0.0.0.0"))

(define (analyse-syscalls syscall-list-file-location malicious-patterns-file-location out)
    (begin
        (define-values (subprocess-obj python-out python-in python-err)
            (subprocess #f #f #f python-location "syscall_analysis.py" syscall-list-file-location malicious-patterns-file-location))
        (subprocess-wait subprocess-obj)
        (display (port->string python-out) out)
        (flush-output out)
        (close-input-port python-out) (close-output-port python-in) (close-input-port python-err)))

; Execute a file in a sandbox
(define (run-file json-obj out)
    (begin
        (semaphore-wait semaphore-obj)
        (send-message "Scan beginning" out)
        (send-progress 0 out)

        (define file-location
            (string-append (path->string (make-temporary-directory)) "\\" (hash-ref json-obj 'file-name)))
        (display-to-file (base64-decode (string->bytes/utf-8 (hash-ref json-obj 'file-data))) (string->path file-location))
        (define malicious-patterns-file-location (write-patterns-to-file (hash-ref json-obj 'patterns)))

        (define procmon-csv-file-location (run-in-sandbox file-location out))

        (send-message "Syscall analysis" out)
        (send-progress 90 out)
        (analyse-syscalls procmon-csv-file-location malicious-patterns-file-location out)

        (send-message "Analysis complete" out)
        (send-progress 100 out)
        (send-state "complete" out)
        (delete-file (string->path procmon-csv-file-location))
        (delete-file (string->path malicious-patterns-file-location))
        (semaphore-post semaphore-obj)))

; Handle a ping request
(define (ping out)
    (output-json "pong" out))

; Handle a request
(define (poll-for-request)
    (begin (define-values (in out) (tcp-accept tcp-obj))
        (thread poll-for-request)
        (define json-obj (read-json in))
        (case (hash-ref json-obj 'command)
            [("ping") (ping out)]
            [("run") (run-file json-obj out)])
        (close-input-port in) (close-output-port out)))

; Main loop
(poll-for-request)
(define (wait-for-threads)
    (begin (sleep) (wait-for-threads)))
(wait-for-threads)

