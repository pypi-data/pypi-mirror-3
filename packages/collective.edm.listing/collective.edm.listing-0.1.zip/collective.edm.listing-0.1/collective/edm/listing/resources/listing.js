var edmlisting = {}
edmlisting.initoverlay = function(){
    jq('.edm-popup-link').unbind('mouseover').mouseover(function(){
    	jq(this).prepOverlay({
            subtype: 'ajax',
            filter: common_content_filter,
            closeselector: '[name=form.button.Cancel]'
            });
    	jq(this).removeClass('edm-popup-link');
    })


    // Content history popup
    jq('.edm-history-popup').prepOverlay({
       subtype: 'ajax',
       filter: 'h2, #content-history',
       urlmatch: '@@historyview',
       urlreplace: '@@contenthistorypopup'
    });

}
jq(document).ready(edmlisting.initoverlay)