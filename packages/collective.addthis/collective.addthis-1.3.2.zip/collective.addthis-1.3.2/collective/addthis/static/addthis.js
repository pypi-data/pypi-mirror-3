$(document).ready(function() {
    try{
        addthis.init();
    }
    catch(e){
        // Do nothing as our page template doesn't have
        // IBelowContent viewlet provider.
    }
});
