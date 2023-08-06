

function set_fuzzy_link(d) {
    var base_url = $("base").attr('href');
    $('#search-field').after('<div id="fuzzySuggestion" style="display: none"><span>Did you mean? : </span><span id="fuzzy-search-suggestion"></span></div>')
    var suggestion_obj = $("#fuzzy-search-suggestion");
    var result_list = d['s'];
    for (i = 0; i < result_list.length; i++){
        var result = result_list[i];
        var search_url = base_url + "/@@search?SearchableText=" + result;
        suggestion_obj.append(
            $("<a>").html(result).attr("href", search_url));
        suggestion_obj.append(
            $("<span>").html("&nbsp;&nbsp;"));
    }
    if (result_list.length != 0){
        $("#fuzzySuggestion").css({display:"block"});
    }
}
function get_suggestion() {
    var base_url = $("base").attr('href');
    var search_text = $('#search-field input[name="SearchableText"]').val();
    var url = base_url + "fuzzy-search";
    if (search_text){
        var data = {r_type : 'json', search_text : search_text};
        $.getJSON(url, data, set_fuzzy_link );
    }
}

$(document).ready(function () {get_suggestion()});
