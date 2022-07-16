// Magery Script

// Dead Check
if 'dead'
    stop
endif

// Reagents Count Check
if insysmsg 'amount is now 0'
    overhead "Not Enough Reagents!" 34
    stop
endif

// Bandage Count Check
if count 'clean bandage%s%' == 0
    overhead "No more bandaids!" 34
    stop
endif

wait 500
// Checks HP so we don't kill ourselves and then casts spell
if hits > 30 and skill 'magery' > 30 and skill 'magery' < 60
    cast 'lightning'
    waitfortarget 3000
    target 'self'
    wait 500
elseif hits > 40 skill 'magery' > 60 and skill 'magery' < 85
    cast 'energy bolt'
    waitfortarget 3000
    target 'self'
    wait 500
elseif hits > 50 skill 'magery' > 85 and skill 'magery' < 100
    cast 'flamestrike'
    waitfortarget 3000
    target 'self'
    wait 500
endif
    
for 10
    wait 100
    if insysmsg 'world is saving'
        for 30
            overhead 'Waiting for world save...'
            wait 5 sec
            if insysmsg 'save complete'
                overhead 'Save complete - continue on!' 88
                clearsysmsg 
                wait 250
                replay
             endif
        endfor
    elseif insysmsg 'world export is processing'
        for 30
            overhead 'Waiting for world export...'
            wait 5 sec
            if insysmsg 'world export completed'
                overhead 'Export complete - continue on!' 88
                clearsysmsg 
                wait 250
                replay
             endif
        endfor
    else
        // Checks our HP
        if hits < 50
            hotkey 'bandage self'
            wait 500
            // Try to sneak in a meditation, if fails, we don't try again
            skill 'Meditation'
            if insysmsg "You begin"
                while hits < 50
                    if insysmsg "You finish"
                        // Bandage Success Check
                        replay
                    elseif insysmsg "barely"
                        // Bandage Fail Check
                        replay
                    elseif insysmsg "slips"
                        // Bandage Fail Check
                        wait 1 sec
                    elseif insysmsg "is not damaged"
                        // Bandage Empty Check
                        replay
                    elseif insysmsg "cannot be used"
                        // Bandage Error Check
                        overhead "Error!" 34
                        replay
                    endif
                    wait 100
                endwhile
                clearsysmsg
            endif
        // Checks our mana
        elseif mana < 20
            skill 'Meditation'
            wait 1 sec
            if insysmsg "You enter a meditative trance"
                // Meditation Success Check
                overhead "Meditating, waiting for full mana..." 88
                while mana < maxmana
                    if insysmsg "You stop meditating"
                        // Meditation Error Check
                        overhead "Broke Meditation!" 34
                        replay
                    endif
                    wait 100
                endwhile
                overhead "Full mana, continuing..." 88
                replay
            endif
        elseif insysmsg "cannot focus"
            // Meditation Fail Check
            replay
        elseif insysmsg "You must wait"
            // Wait message
            overhead 'You must wait..' 34
            wait 1 sec
            replay
        elseif mana < maxmana
            // Spell Success Check
            replay
        endif
    endif
endfor

if insysmsg "You must wait"
    // Wait message
    overhead 'You must wait..' 34
    wait 1 sec
    replay
endif

if skill 'magery' >= 100
    overhead 'GM MAGERY, DONE.'
    overhead 'Stopping script'
    stop
endif

replay