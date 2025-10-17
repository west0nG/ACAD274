$(document).ready(function() {

    $(".page").hide();
    $("#page-1").show();
    
    $("#page-1 .next-btn").on("click", function(){
        $("#page-1").animate({
            "left": "-100%"
        }, 600);
        
        $("#page-2").show().css("left", "100%").animate({
            "left": "0%"
        }, 600, function(){
            $("#page-1").hide().css("left", "0%");
        });
    });
    
    $("#page-2 .next-btn").on("click", function(){
        $("#page-2").animate({
            "top": "-100%"
        }, 600);
        
        $("#page-3").show().css("top", "100%").animate({
            "top": "0%"
        }, 600, function(){
            $("#page-2").hide().css("top", "0%");
        });
    });
    
    $("#page-3 .next-btn").on("click", function(){
        $("#page-3").animate({
            "opacity": "0"
        }, 600);
        
        $("#page-4").show().css("opacity", "0").delay(600).animate({
            "opacity": "1"
        }, 600, function(){
            $("#page-3").hide().css("opacity", "1");
        });
    });
    
    $("#page-4 .next-btn").on("click", function(){
        $("#page-4").animate({
            "opacity": "0"
        }, 500);
        
        $("#page-5").show().css("opacity", "0").delay(500).animate({
            "opacity": "1"
        }, 500, function(){
            $("#page-4").hide().css("opacity", "1");
        });
    });
    
    $("#page-5 .restart-btn").on("click", function(){
        $("#page-5").animate({
            "left": "100%"
        }, 600);
        
        $("#page-1").show().css("left", "-100%").animate({
            "left": "0%"
        }, 600, function(){
            $("#page-5").hide().css("left", "0%");
        });
    });
});
