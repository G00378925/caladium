#lang racket
;
;  main.rkt
;  caladium
;
;  Created by Declan Kelly on 22-10-2022.
;  Copyright © 2022 Declan Kelly. All rights reserved.
;

(require net/base64)
(require json)

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

(define (run-in-sandbox executable-location)
    (begin
        (define procmon-pml-file-location
            (path->string (make-temporary-file "caladium_~a.pml")))
        (define procmon-csv-file-location
            (path->string (make-temporary-file "caladium_~a.csv")))

        (define procmon-subprocess (subprocess-and-close-ports procmon-location
            (list "/Minimized" "/BackingFile" procmon-pml-file-location)))
        (define sandboxed-subprocess (subprocess-and-close-ports sandboxie-start-location
            (list "/wait" executable-location)))

        (sleep 1)
        (define listpids-list (listpids-in-sandbox))
        (subprocess-wait sandboxed-subprocess)

        (system (string-join (list procmon-location "/Terminate") " "))
        (subprocess-wait procmon-subprocess)

        (system (string-join (list procmon-location "/OpenLog" procmon-pml-file-location
            "/SaveAs" procmon-csv-file-location) " "))
        (system (string-join (append (list "python.exe" "procmon_csv_filter.py" procmon-csv-file-location)
            listpids-list) " "))

        (define procmon-csv-port
            (open-input-file (string->path procmon-csv-file-location)))
        (define procmon-csv-data
            (port->string procmon-csv-port))
        (close-input-port procmon-csv-port)

        (delete-file (string->path procmon-pml-file-location))
        (delete-file (string->path procmon-csv-file-location))
        procmon-csv-data))

(define semaphore-obj (make-semaphore 1))
(define tcp-obj (tcp-listen 8080 8 #f "0.0.0.0"))

(define (run-file json-obj out)
    (begin
        (semaphore-wait semaphore-obj)
        (define file-location
            (string-append (path->string (make-temporary-directory)) "\\" (hash-ref json-obj 'file-name)))
        (display-to-file (base64-decode (string->bytes/utf-8 (hash-ref json-obj 'file-data))) (string->path file-location))
        (write (string-append "procmon-csv-data size:" (number->string
            (string-length (run-in-sandbox file-location))) "\n") out)
        (semaphore-post semaphore-obj)))

(define (poll-for-request)
    (begin (define-values (in out) (tcp-accept tcp-obj))
        (thread poll-for-request)
        (define json-obj (read-json in))
        (case (hash-ref json-obj 'command)
            [("run") (run-file json-obj out)])
        (close-input-port in) (close-output-port out)))

(poll-for-request)
(define (wait-for-threads)
    (begin (sleep) (wait-for-threads)))
(wait-for-threads)

