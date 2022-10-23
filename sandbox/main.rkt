#lang racket
;
;  main.rkt
;  caladium
;
;  Created by Declan Kelly on 22-10-2022.
;  Copyright © 2022 Declan Kelly. All rights reserved.
;

(define sandboxie-start-location
    (string-append (getenv "ProgramFiles") "\\Sandboxie\\Start.exe"))
(define procmon-location
    (string-append (getenv "SystemDrive") "\\SysinternalsSuite\\Procmon64.exe"))

(define procmon-pml-file-location
    (path->string (make-temporary-file "caladium_~a.pml")))
(define procmon-csv-file-location
    (path->string (make-temporary-file "caladium_~a.csv")))

(define-values (procmon-subprocess procmon-out procmon-in procmon-err)
    (subprocess #f #f #f procmon-location "/Minimized" "/BackingFile" procmon-pml-file-location))
(define-values (sandboxed-subprocess sandboxed-out sandboxed-in sandboxed-err)
    (subprocess #f #f #f sandboxie-start-location "/wait" "cmd.exe"))

(define sandboxed-subprocess-pid
    (subprocess-pid sandboxed-subprocess))
(subprocess-wait sandboxed-subprocess)

(close-input-port sandboxed-out)
(close-output-port sandboxed-in)
(close-input-port sandboxed-err)

(system (string-join (list procmon-location "/Terminate") " "))
(subprocess-wait procmon-subprocess)

(close-input-port procmon-out)
(close-output-port procmon-in)
(close-input-port procmon-err)

(system (string-join (list procmon-location "/OpenLog" procmon-pml-file-location
    "/SaveAs" procmon-csv-file-location) " "))

(define procmon-csv-port
    (open-input-file (string->path procmon-csv-file-location)))
(define procmon-csv-data
    (port->string procmon-csv-port))
(print (string-append "procmon-csv-data size:" (number->string (string-length procmon-csv-data)) "\n"))
(close-input-port procmon-csv-port)

(delete-file (string->path procmon-pml-file-location))
(delete-file (string->path procmon-csv-file-location))

