
\version "2.12.2"

\header {
    title = "AM207 Melody"
    subtitle = "Created on: Mon Apr 28 18:05:28 2014"
    composer = "Aymen Jaffry and Nikhil Sud"
}

result = {
    <<
    \new Staff
    {
        \time 4/4
        \clef treble
        {
            r2 a'~ a' d''~ d'' c''~ c'' b'~ b' e''~ e'' d''~ d'' c''~ c'' b'~ b' d''~ d'' cis'' d'' 1
        }
    }
    \new Staff
    {
        \time 4/4
        \clef treble
        {
            d' 1 f' e' d' g' f' a' g' f' e' d' \bar "|."
        }
    }
    >>
}

\paper {
    raggedbottom = ##t
    indent = 7. \mm
    linewidth = 183.5 \mm
    betweensystemspace = 25\mm
    betweensystempadding = 0\mm
}

\score{
    \result
    \midi {
        \context {
            \Score
            tempoWholesPerMinute = #(ly:make-moment 160 4)
        }
    }
    \layout {}
}
