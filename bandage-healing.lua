// Bandaid Healing
if weight > 300
    overhead "Reached Weight Threshold!" 34
    wait 1 sec
endif
      
if count 'clean bandage%s%' == 0
    overhead "No more bandaids!" 34
    stop
endif

wait 500
if skill 'Healing' < 100
    hotkey 'bandage lasttarget'
    //hotkey 'use bandage (no timer)'
    hotkey 'next friend target'
    //waitfortarget 1 sec
    //target next 'friendly' humanoid
    //target closest 'friendly' humanoid
endif

for 20
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
        if insysmsg "world is saving" or insysmsg 'save complete'
        // World Save Check
            replay
        elseif insysmsg "export is processing" or insysmsg 'export completed'
        // World Save Check
            replay
        elseif insysmsg "You finish"
            // Success Check
            replay
        elseif insysmsg "slips"
            // Fail Check
            wait 1 sec
            replay
        elseif insysmsg "is not damaged"
            // Empty Check
            replay
        elseif insysmsg "cannot be used"
            // Error Check
            overhead "Error!" 34
            break
        elseif insysmsg "target is out of range"
            // Error Check
            overhead "Out of range!" 34
            replay
        elseif insysmsg "too far away"
            // Error Check
            overhead "Too far!" 34
            replay
        elseif insysmsg "You must wait"
            // Wait message
            overhead 'You must wait..' 34
            wait 1 sec
            replay
        endif
    endif
endfor

if insysmsg "You must wait"
    // Wait message
    overhead 'You must wait..' 34
    wait 1 sec
    replay
else
    overhead 'Reposition' 88
    wait 3 sec
    replay  
endif
  
overhead 'Stopping script' 34