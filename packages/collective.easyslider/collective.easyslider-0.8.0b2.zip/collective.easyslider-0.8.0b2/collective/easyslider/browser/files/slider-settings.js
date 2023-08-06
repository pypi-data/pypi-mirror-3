
function reload_slides(){
    //reloads the list of slides--just calls the widget info
    (function($){
    //begin $ namespace
    $.get($('input#slides-view-url').val(), {}, function(data, status){
        $('div#slides-view').html($(data).html());
        setup_events();
    });
    //end $ endspace
    })(jQuery);
}

function setup_events(){
    //needs to be recalled whenever slides are retrieved
    (function($){
    //begin $ namespace
    function move_action(){
        //event for all move actions(up, down, delete)
        
        if($(this).hasClass('remove')){
            if(!window.confirm("Are you sure you want to remove this slide?")){
                return false;
            }
        }
        $.get($(this).attr('href') + '?ajax=true', {}, function(data, status){
            reload_slides();
        });
        return false;
    }

    $("div.slide-buttons a.move-up").click(move_action);
    $("div.slide-buttons a.move-down").click(move_action);
    $("div.slide-buttons a.remove").click(move_action);

    //end $ namespace
    })(jQuery);
}

(function($){
    $(document).ready(function(){
        setup_events();//fire it up!
    });
})(jQuery);
