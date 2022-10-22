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

(define procmon-log-file-location
    (path->string (make-temporary-file)))

(define-values (procmon-subprocess procmon-out procmon-in procman-err)
    (subprocess #f #f #f procmon-location "/Minimized" "/BackingFile" procmon-log-file-location))

(define-values (sandboxed-subprocess sandboxed-out sandboxed-in sandboxed-err)
    (subprocess #f #f #f sandboxie-start-location "/wait" "cmd.exe"))

(define sandboxed-subprocess-pid
    (subprocess-pid sandboxed-subprocess))

(subprocess-wait sandboxed-subprocess)

(system (string-join (list procmon-location "/Terminate") " "))
(subprocess-wait procmon-subprocess)

(system (string-join (list procmon-location "/OpenLog" (string-append procmon-log-file-location ".pml")
    "/SaveAs" (string-append procmon-log-file-location ".csv")) " "))

