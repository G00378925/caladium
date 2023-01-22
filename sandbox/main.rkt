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

(define sandboxie-start-location
    (string-append (getenv "ProgramFiles") "\\Sandboxie\\Start.exe"))
(define procmon-location
    (string-append (getenv "SystemDrive") "\\SysinternalsSuite\\Procmon64.exe"))

(define (subprocess-and-close-ports executable-location subprocess-parameters)
    (begin (define-values (subprocess-obj out in err)
        (apply subprocess #f #f #f executable-location subprocess-parameters))
        (close-input-port out) (close-output-port in) (close-input-port err)
        subprocess-obj))

(define (listpids-in-sandbox)
    (begin (define-values (subprocess-obj out in err)
        (subprocess #f #f #f sandboxie-start-location "/listpids"))
        (define listpids-list (string-split (port->string out) "\r\n"))
        (subprocess-wait subprocess-obj)
        (close-input-port out) (close-output-port in) (close-input-port err)
        listpids-list))

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
        (system (string-join (append (list "python.exe" "procmon_csv_filter.py" procmon-csv-file-location)
            listpids-list) " "))

        (define procmon-csv-port
            (open-input-file (string->path procmon-csv-file-location)))
        (define procmon-csv-data
            (string-split (port->string procmon-csv-port) "\n"))
        (close-input-port procmon-csv-port)

        (delete-file (string->path procmon-pml-file-location))
        (delete-file (string->path procmon-csv-file-location))
        procmon-csv-data))

(define semaphore-obj (make-semaphore 1))
(define tcp-obj (tcp-listen 8080 8 #f "0.0.0.0"))

(define (analysis-thread-func patterns receive-channel response-channel)
    (begin
        (define syscall (channel-get receive-channel))
        (channel-put response-channel #f)
        (analysis-thread-func patterns receive-channel response-channel)))

(define (analyse-syscalls syscall-list patterns out)
    (begin
        (define analysis-thread-count 4)
        (define receive-channel (make-channel))
        (define analysis-thread-channels
            (for/list ([x (build-list analysis-thread-count values)])
                (make-channel)))

        (send-message "Spawning analysis threads" out)
        (define analysis-threads
            (for/list ([x (build-list analysis-thread-count values)])
                (thread (lambda () (analysis-thread-func patterns (list-ref analysis-thread-channels x) receive-channel)))))

        (for/list ([syscall-string syscall-list])
            (channel-put (list-ref analysis-thread-channels (random 0 (- analysis-thread-count 1))) syscall-string))

        (define (receive-results syscall-number)
            (begin
                (channel-get receive-channel)
                (if (< (+ syscall-number 1) (length syscall-list)) (receive-results (+ syscall-number 1)) #f)))
        (receive-results 0)))

(define (run-file json-obj out)
    (begin
        (semaphore-wait semaphore-obj)
        (send-message "Scan beginning" out)
        (send-progress 0 out)

        (define file-location
            (string-append (path->string (make-temporary-directory)) "\\" (hash-ref json-obj 'file-name)))
        (display-to-file (base64-decode (string->bytes/utf-8 (hash-ref json-obj 'file-data))) (string->path file-location))

        (define syscall-list (run-in-sandbox file-location out))
        (send-message (string-append "procmon-csv-data size: "
            (number->string (length syscall-list)) "\n") out)
        (send-progress 90 out)

        (analyse-syscalls syscall-list (hash-ref json-obj 'patterns) out)
        (send-message "Syscall analysis" out)
        (send-progress 100 out)
        (send-state "complete" out)

        (semaphore-post semaphore-obj)))

(define (ping out)
    (output-json "pong" out))

(define (poll-for-request)
    (begin (define-values (in out) (tcp-accept tcp-obj))
        (thread poll-for-request)
        (define json-obj (read-json in))
        (case (hash-ref json-obj 'command)
            [("ping") (ping out)]
            [("run") (run-file json-obj out)])
        (close-input-port in) (close-output-port out)))

(poll-for-request)
(define (wait-for-threads)
    (begin (sleep) (wait-for-threads)))
(wait-for-threads)

