$(document).ready(function() {
    try{
        addthis.init();
    }
    catch(e){
        console.warn('It seems this page is missing viewlet which provides ' +
                    'addthis scripts.');
    }
});
