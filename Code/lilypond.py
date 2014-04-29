import datetime
from string import Template

# Maps numbers to lilypond notes.
NOTES = {
    1: "g", 2: "a", 3: "b", 4: "c'", 5: "d'", 6: "e'", 7: "f'", 8: "g'", 9: "a'", 10: "b'", 11: "c''", 12: "d''", 13: "e''", 14: "f''", 15: "g''", 16: "a''", 17: "r"
}

TEMPLATE = """
\\version "2.12.2"

\header {
    title = "AM207 Melody"
}

result = {
    <<
    \\new Staff
    {
        \\time 4/4
        \clef treble
        {
            $contrapunctus
        }
    }
    \\new Staff
    {
        \\time 4/4
        \clef treble
        {
            $cantus_firmus
        }
    }
    >>
}

\score{
    \\result
    \midi {
        \context {
            \Score
            tempoWholesPerMinute = #(ly:make-moment 160 2)
        }
    }
    \layout {}
}
"""

# Ensure the notes are in range
def normalize(notes):
    return [n for n in notes if n > 0 and n < 18]


# Given a list of notes as integers, will return the lilypond notes for the cantus firmus.
def get_cantus_firmus(notes):

    normalized = normalize(notes)
    if not normalized:
        return ''

    result = NOTES[normalized[0]] + ' 1 ' # Set the duration against the first note.
    result += ' '.join([NOTES[n] for n in normalized[1:]]) # Translate all the others.
    result += ' \\bar "|."' # End with a double bar.
    result = result.replace('  ', ' ') # Tidy up double spaces.
    return result


# Given a representation of the contrapunctus in numeric form, turns it into correct Lilypond notation.
def get_contrapunctus(notes):    

    normalized = normalize(notes)
    if not normalized:
        return ''

    result = 'r2 ' # Start with two beats rest.

    body = [NOTES[note] for note in normalized[:-2]] # Translate all except the last two
    for pitch in body:
        result += '%s~ %s ' % (pitch, pitch)

    final = normalized.pop() # Ensure the penultimate is a semitone away (only if moving up to the final)
    penult = normalized.pop()
    next = NOTES[penult]

    if final == penult + 1:
        if final not in [4, 7, 11, 14]: # Check the note isn't a C or an F
            next = next[0] + 'is' + next[1:] # Insert 'is' to sharpen the pitch of by a semitone
    
    result += ' ' + next
    result += ' %s 1' % (NOTES[final]) # Ensure the final note is a semibreve
    result = result.replace('  ', ' ') # Tidy up double spaces
    return result

# Returns a string containing lilypond code to render the musical information as PDF/MIDI
def render(cantus_firmus, contrapunctus):

    context = {}
    context['created_on'] = datetime.datetime.today().strftime('%c')
    context['contrapunctus'] = get_contrapunctus(contrapunctus)
    context['cantus_firmus'] = get_cantus_firmus(cantus_firmus)
    
    # Sanity check...
    if context['contrapunctus'] and context['cantus_firmus']:
        score = Template(TEMPLATE)
        return score.substitute(context)
    else:
        return ''
