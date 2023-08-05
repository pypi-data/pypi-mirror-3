jq(document).ready(function(){
    portletCounter = 1;
    jq("#portal-column-one .portlet").each(function() {
        assignPortlets(this);
    });
    portletCounter = 2; // start with different number to offset colors from column-one
    jq("#portal-column-two .portlet").each(function() {
        assignPortlets(this);
    });
    
});

// give portlets classes to alternate colors
function assignPortlets(portlet) {
    jq(portlet).addClass("color-"+portletCounter);
    if (portletCounter == 3) {
        portletCounter = 1;
    }
    else {
        portletCounter++;
    }
};