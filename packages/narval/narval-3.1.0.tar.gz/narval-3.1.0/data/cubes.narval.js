// This contains template-specific javascript

function filter_log(domid, threshold_level) {
    var log_levels = ["Debug", "Info", "Warning", "Error", "Fatal"]
    var action = "hide";
    for (var idx = 0; idx < log_levels.length; idx++){
        var level = log_levels[idx];
        if (level === threshold_level){
            action = "show";
        }
        $('#'+domid+' .log' + level)[action]();
    }
}
