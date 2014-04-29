
\version "2.12.2"

\header {
    title = "AM207 Melody"
}

result = {
    <<
    \new Staff
    {
        \time 4/4
        \clef treble
        {
            r2 d''~ d'' c''~ c'' g''~ g'' f''~ f'' e''~ e'' d''~ d'' c''~ c'' b'~ b' d''~ d'' cis'' d'' 1
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

\score{
    \result
    \midi {
        \context {
            \Score
            tempoWholesPerMinute = #(ly:make-moment 160 2)
        }
    }
    \layout {}
}
