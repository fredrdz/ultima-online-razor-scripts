// Bandage Processing
if insysmsg 'world is saving'
    // World Save Check
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
elseif weight > 170
    // Weight Check
    overhead 'weight threshold reached' 34
    stop
elseif insysmsg "You must wait"
    // Wait Check
    wait 1250
    replay
elseif count 'bale%s% of cotton' > 0 and findtype 'spinning wheel' true
    dclicktype 'bale%s% of cotton'
    waitfortarget 2000
    targettype 'spinning wheel'
    replay
elseif count 'spool%s% of thread' > 0 and findtype 'upright loom' true
    dclicktype 'spool%s% of thread' backpack
    waitfortarget 1000
    targettype 'upright loom'
    replay
elseif count 'bolt%s% of cloth' > 0 and findtype 'scissors' true
    dclicktype 'scissors'
    waitfortarget 2000
    targettype 'bolt%s% of cloth' backpack
    replay
elseif count 'cut cloth' > 0 and findtype 'scissors' true
    dclicktype 'scissors'
    waitfortarget 2000
    targettype 'cut cloth' backpack
    replay
endif

sysmsg 'we are done'