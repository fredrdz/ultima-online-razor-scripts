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
if hits >= 30 and skill 'magery' >= 30.1 and skill 'magery' <= 60
    cast 'lightning'
    waitfortarget 3000
    target 'self'
    wait 1 sec
elseif hits >= 40 skill 'magery' >= 60.1 and skill 'magery' <= 85
    cast 'energy bolt'
    waitfortarget 3000
    target 'self'
    wait 1 sec
elseif hits >= 55 skill 'magery' >= 85.1 and skill 'magery' < 100
    cast 'flamestrike'
    waitfortarget 3000
    target 'self'
    wait 1 sec
endif
    
for 10
    wait 200
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
    elseif insysmsg "You must wait"
        // Wait message
        overhead 'You must wait..' 34
        wait 2 sec
        replay
    else
        // Health Check
        if hits < 55
            hotkey 'bandage self'
            wait 500
            skill 'Meditation'
            // Healing sub-loop
            for 60
                if insysmsg "You finish"
                    // Bandage Success Check
                    break
                elseif insysmsg "barely"
                    // Bandage Fail Check
                    break
                elseif insysmsg "slips"
                    // Bandage Fail Check
                    wait 1 sec
                elseif insysmsg "is not damaged"
                    // Bandage Empty Check
                    break
                elseif insysmsg "cannot be used"
                    // Bandage Error Check
                    overhead "Error!" 34
                    break
                endif
                wait 100
            endfor
            clearsysmsg
            replay
        // Mana Check
        elseif mana <= 39 and hp >= 54
            skill 'Meditation'
            // Meditation sub-loop
            for 15
                if insysmsg "You enter a meditative trance"
                    // Meditation Success Check
                    overhead "Meditating, waiting for full mana.." 88
                    while mana < maxmana
                        if insysmsg "You stop meditating"
                            // Meditation Error Check
                            overhead "Broke Meditation!" 34
                            clearsysmsg
                            replay
                        endif
                        wait 200
                    endwhile
                    overhead "Full mana, continuing.." 88
                    break
                elseif insysmsg "cannot focus"
                    // Meditation Fail Check
                    // Re-try Meditation
                    wait 1 sec
                    skill 'Meditation'
                endif
                wait 200
            endfor
            clearsysmsg
            replay
        elseif mana < maxmana
            // Spell Success Check
            replay
        endif
    endif
endfor

if skill 'magery' >= 100
    overhead 'GM MAGERY, DONE.'
    overhead 'Stopping script'
    stop
endif

replay