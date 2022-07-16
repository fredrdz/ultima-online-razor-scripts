// Lumberjacking

if weight > 170
        overhead "Reached Weight Threshold!" 34
        stop
endif
        
if lhandempty ?? 0 
    if findtype "hatchet" backpack
        dclicktype 'hatchet' backpack
        wait 200
    endif
endif
            
if lhandempty ?? 0 
    overhead "No more hatchets!" 34
    stop
endif

wait 500
overhead 'Lumberjacking' 0
hotkey 'Use item in hand'
waitfortarget 1000
targetrelloc -1 1

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
    elseif lhandempty ?? 0 
        overhead "Broke axe!" 34
        replay
    else
        if insysmsg "world is saving" or insysmsg 'World save complete'
        // World Save Check
            replay
        elseif insysmsg "You hack"
            // Fail Check
            replay
        elseif insysmsg "You put"
            // Success Check
            replay
        elseif insysmsg "There's not enough"
            // Empty Check
            break
        elseif insysmsg "You can't"
            // Error Check
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
    wait 1000
    replay
else
    overhead 'Move to next spot' 88
    wait 5 sec
    replay  
endif
  
overhead 'Stopping script' 34