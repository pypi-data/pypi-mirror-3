;; -*-mode: scheme; coding: utf-8; -*-
(define *cal* (import "calendar"))
(define *datetime* (import "datetime"))
(define *date* (attr *datetime* 'date))

(define month-names
  '#("January" "February" "March" "April" "May" "June" "July" 
     "August" "September" "October" "November" "December"))
(define day-names '#("Mon" "Tue" "Wed" "Thu" "Fri" "Sat" "Sun"))
(define (day-name wday)
  (vector-ref day-names
	      (if (isa? wday (attr *datetime* "date"))
		  (invoke wday 'weekday) wday)))

;; Display a day of the week header
(define (disp-weekheader year month day)
  (display "<tr>")
  (display "<td colspan='2'>&nbsp;</td>")
  (for-each
   (lambda (id)
     (let ((dname (day-name id)))
       (format #t "<td class='wday_~A'>~A</td>"
	       (string-downcase dname) dname)))
   '(6 0 1 2 3 4 5))
  (display "<td colspan='2'>&nbsp;</td>")
  (display "</tr>\n"))

;; Display days
(define (disp-weekdays year month day weekdays)
  (display "<tr>")
  (display "<td colspan='2'>&nbsp;</td>")
  (for-each
   (lambda (date)
     (let ((dname (day-name date))
	   (mm (attr date 'month))
	   (dd (attr date 'day)))
       (display "<td align='center' valign='middle'>")
       ;;   <span class="wday_sun">>DD</span>
       (format #t "<span class='day_~A'>~A</span>"
	       (if (= mm month) (string-downcase dname) "out") dd)
       (display "</td>")
       )) weekdays)
  (display "<td colspan='2'>&nbsp;</td>")
  (display "</tr>\n"))

;; BUG: raise overflowError in the following case
;;   (define maxdate (attr *date* 'max))
;;   (define mindate (attr (attr *date* 'min)))
;;   (dispcal :year (attr maxdate 'year) :month (attr maxdate 'month))
;;   (dispcal :year (attr mindate 'year) :month (attr mindate 'month))
(define (dispcal . args )
  (letrec ((year (get-keyword :year args 2012))
	   (month (get-keyword :month args 1))
	   (day (get-keyword :day args 1))
	   (prev-month-link (get-keyword :prev-month args #f))
	   (next-month-link (get-keyword :next-month args #f))
	   (prev-year-link (get-keyword :prev-year args #f))
	   (next-year-link (get-keyword :next-year args #f))
	   (dsp-weekheader (get-keyword :disp-weekheader args disp-weekheader))
	   (dsp-week (get-keyword :disp-weekdays args disp-weekdays))
	   (cd (invoke *cal* 'Calendar 6)) ;; Make calendar
	   (mdlist (lambda (yy mm) ;; Get month/day vector
		     (invoke cd 'monthdatescalendar yy mm)))
	   )
    ;; Display TABLE tag
    (display "<table class='cal_table' cellpadding='1' border='0'>\n")

    (display "<tr>")
    ;; Display previous-link
    (format
     #t "<td>~A</td><td>~A</td>"
     (if prev-year-link
	 (format "<a href='~A' class='cal_link'>&lt;&lt;</a>" prev-year-link) "")
     (if prev-month-link
	 (format "<a href='~A' class='cal_link'>&nbsp;&lt;</a>" prev-month-link) ""))
    ;; Display caption
    (format #t "<td colspan='7' class='cal_caption'>~A</td>\n"
	    ;;  Display month/year
	    (format "<span class='cal_date'>~A ~A</span>" 
		    (vector-ref month-names (- month 1)) year))
    ;; Display next links
    (format
     #t "<td>~A</td><td>~A</td>"
     (if next-month-link
	 (format "<a href='~A' class='cal_link'>&gt;&nbsp;</a>" next-month-link) "")
     (if next-year-link
	 (format "<a href='~A' class='cal_link'>&gt;&gt;</a>" next-year-link) ""))
    (display "</tr>")

    ;; Display week header
    (dsp-weekheader year month day)

    ;; Display weeks
    (for-each
     (lambda (wlst)
       (dsp-week year month day wlst)
       ) (mdlist year month))

    ;; Display TABLE end tag
    (display "</table>\n")
    ;; Display div end-tag for frame
    ))
#<none>
