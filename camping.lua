// Camping Script
if weight > 365
    overhead "Reached Weight Threshold!" 34
    while count 'kindling' > 0
        dclicktype 'kindling' backpack
        wait 1 sec
    endwhile
endif
      
if count 'dagger' == 0
    overhead "No more daggers!" 34
    stop
endif

wait 500
overhead 'Using Dagger' 0
//lifttype 'dagger'
//droprelloc -1 0
dclicktype 'dagger' backpack
waitfortarget 1000
targetrelloc -1 0

for 15
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
        elseif insysmsg "You put"
            // Success Check
            replay
        elseif insysmsg "There's not enough"
            // Empty Check
            overhead "Out of wood!" 88
            break
        elseif insysmsg "You can't"
            // Error Check
            overhead "Error!" 34
            break
        elseif insysmsg "Target cannot"
            // Error Check2
            overhead "Error!" 34
            break
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