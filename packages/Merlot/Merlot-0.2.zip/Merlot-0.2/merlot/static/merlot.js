var dateFormat = "yy-mm-dd";

$(document).ready(function() {

    // focus in login page
    $('#form\\.username').focus();


    function dateTranslatorSetup(input) {
        input.before('<div class="hint date-translated">'+merlot.i18n.TYPE_DATE_BELOW_I18N+'</div>');
    };    
    
    $("#form\\.date").datepicker({"dateFormat": dateFormat});

    //PROJECT SELECTION
    var only_ranged_star_end = $("#form\\.start_date, #form\\.end_date");
    var preset_ranges_from_to = $("#form\\.from_date, #form\\.to_date");
    if (preset_ranges_from_to.length){
        //we have to create the little calendar icon on the right
        preset_ranges_from_to.each(function(){
            icon = '<img class="calendar-icon ui-datepicker-trigger" src="/fanstatic/merlot/images/calendar.gif"/>';
            $(this).after(icon);
        });
        preset_ranges_from_to.daterangepicker({
            presetRanges: [
                {text: merlot.i18n.TODAY_I18N, dateStart: 'today', dateEnd: 'today' },
                {text: merlot.i18n.LAST_7_DAYS_I18N, dateStart: 'today-7days', dateEnd: 'today' },
                {text: merlot.i18n.MONTH_TO_DATE_I18N, dateStart: function(){ return Date.parse('today').moveToFirstDayOfMonth(); }, dateEnd: 'today' },
                {text: merlot.i18n.PREVIOUS_MONTH_I18N, dateStart: function(){ return Date.parse('1 month ago').moveToFirstDayOfMonth(); }, dateEnd:function(){ return Date.parse('1 month ago').moveToLastDayOfMonth(); } } 
            ],
            presets: {dateRange: merlot.i18n.DATE_RANGE_I18N}, 
            dateFormat: dateFormat
        });

        //we copy the events from the daterangpicker to the calendar icon launcher
        preset_ranges_from_to.each(function(){
            calendar_launcher = $(this).next('.calendar-icon');
            $(this).copyEventsTo(calendar_launcher);
            $(this).unbind();
        });
        preset_ranges_from_to.each(function(){  
            dateTranslatorSetup($(this));
            var date_translated = $(this).siblings('.date-translated');
            dateTranslator($(this), date_translated);          
        });            
    }
    if (only_ranged_star_end.length) {
        //we have to create the little calendar icon on the right
        only_ranged_star_end.each(function(){
            icon = '<img class="calendar-icon ui-datepicker-trigger" src="/fanstatic/merlot/images/calendar.gif"/>';
            $(this).after(icon);
        });
        only_ranged_star_end.daterangepicker({
            presetRanges:[],
            presets: {specificDate:merlot.i18n.SPECIFIC_DATE_I18N, dateRange: merlot.i18n.DATE_RANGE_I18N}, 
            dateFormat: dateFormat
        });

        //we copy the events from the daterangpicker to the calendar icon launcher
        only_ranged_star_end.each(function(){
            calendar_launcher = $(this).next('.calendar-icon');
            $(this).copyEventsTo(calendar_launcher);
            $(this).unbind();
        });  
        only_ranged_star_end.each(function(){  
            dateTranslatorSetup($(this));
            var date_translated = $(this).siblings('.date-translated');
            dateTranslator($(this), date_translated);          
        });               
    }


    //projects container
    $('#project-container .filters select').change(function() {
        $('.ajax-load').css('display', 'block');
        $.ajax({
          url: 'projects_listing',
          data:({status : this.value}),
          success: function(data) {
            $('.results').html(data);
            $('.ajax-load').css('display', 'none');
          }
        });
    });
    listingFilter(context='#project-container',
                  listing_table_id='#listing-table',
                  values_to_filter='.searchable',
                  selectable=true);

    //project container
    listingFilter(context='#project',
                  listing_table_id='#listing-table',
                  values_to_filter='.searchable',
                  selectable=true,
                  trigger_event='click');


    //clients container
    listingFilter(context='#clients-container',
                  listing_table_id='#listing-table',
                  values_to_filter='.searchable',
                  selectable=true);


    //Users container
    listingFilter(context='#users-container',
                  listing_table_id='#listing-table',
                  values_to_filter='.searchable');

    //dashboard
    listingFilter(context='#dashboard',
                  listing_table_id='#listing-table',
                  values_to_filter='.searchable',
                  selectable=true,
                  trigger_event='click');




    //LOG VIEW
    work_hours = $('#form\\.hours');
    remaing_hours = $('#form\\.remaining');
    calculateRemaingHours(work_hours, remaing_hours);


    manageFlashMessages();

    //collapsable content
    $(".colapsable").collapse({
                group:'table',
                head:'h2',
                show: function() {
                    this.animate({opacity: 'toggle', height: 'toggle'}, 200);
                },
                hide : function() {
                    this.animate({opacity: 'toggle', height: 'toggle'}, 200);
                }
            });

    //tooltips
    $('.actions .action').each(function(){
        var title = $(this).attr('title');
        $(this).removeAttr('title');
        $(this).attr('my-attr', title);
    });
    $('.actions .action').tipsy({gravity: $.fn.tipsy.autoNS, title: 'my-attr'});
    
    //graph for listing tasks
    listingGraphs();

});

function listingFilter(context, listing_table_id, values_to_filter, selectable, trigger_event){
    if ($(context).length !== 0){
        var selectable = selectable | false;
        $("#filter-search").focus();
        $("#filter-search").keyup(function() {
            var table = $(listing_table_id);
            var values = [];
            $(values_to_filter, listing_table_id).each(function(i){
                values[i] = $(this).html();
            });
            $.uiTableFilter( table, this.value, values );
            if (selectable) {
                if (this.value === ''){
                    table.find("tbody > tr:visible").removeClass('selected');
                }
                else {
                    table.find("tbody > tr:visible").removeClass('selected');
                    var tr = table.find("tbody > tr:visible")[0];
                    $(tr).addClass('selected');
                }
            }
        });

        $('#filter-form').submit(function(){
            var table = $(listing_table_id);
            if (selectable) {
                var tr = table.find("tbody > tr:visible")[0];
                if(tr !== undefined){
                    $(tr).addClass('selected');
                    link_to_go = table.find("tbody > tr:visible .linkeable")[0];
                    if(trigger_event){
                        $(link_to_go).trigger(trigger_event);
                    }
                    else {
                        document.location = $(link_to_go).attr('href');
                    }
                }
            }
            return false;
        }).focus();
    }
}

function calculateRemaingHours(work_hours, remaing_hours) {
    if (work_hours && remaing_hours) {
        var remaing_value = remaing_hours.val();
        work_hours.blur(function(e) {
            total = 0;
            if (work_hours.val().length > 0) {
                if (remaing_value) {
                    total = remaing_value - work_hours.val();
                    if (total < 0) {
                        total = 0;
                    }
                }
                else {
                    total = '';
                }
            }
            remaing_hours.attr('value', total);
        });
    }
}

function manageFlashMessages() {
    $('#flash-messages > ul').each(function() {
        var count = 0;
        var messages_container = $(this);

        messages_container.find('li').each(function() {
            var close_message = $("<span>&nbsp;</span>")
                .attr('title','Close message')
                .addClass('close_message ui-icon ui-icon-close')
                .click(function() {
                    count--;
                    if (count > 0) {
                        $(this).parent().slideUp("slow");
                    }
                    else {
                        messages_container.slideUp("slow");
                    }
                });
            $(this).append(close_message);
            count++;
        });

    });
}
function dateTranslator(date_input, date_translated) {
    // code from http://www.datejs.com/ demos
    var messages = "No match";
    var input = date_input, date_string = date_translated, date = null;
    var input_empty = (date_input.val() === '') ? '' : date_input.val(), empty_string = merlot.i18n.TYPE_DATE_BELOW_I18N;
    input.val(input_empty);
    date_string.text(empty_string);
    input.keyup(
        function (e) {
            date_string.removeClass();
            date_string.addClass('hint');
            date_string.addClass('date-translated');
            if (input.val().length > 0) {
                date = Date.parse(input.val());
                if (date !== null) {
                    input.removeClass();
                    date_string.addClass("accept").text(date.toString("dddd, MMM dd, yyyy"));
                } else {
                    input.addClass("validate_error");
                    date_string.addClass("error").text(messages+"...");
                }
            } else {
                date_string.text(empty_string).addClass("empty");
            }
        }
    );
    input.focus(
        function (e) {
            if (input.val() === input_empty) {
                input.val("");
            }
        }
    );
    input.blur(
        function (e) {
            if (input.val() !== "") {
                input.attr('value', date.toString("yyyy-MM-dd"));
            }
            if (input.val() === "") {
                input.val(input_empty).removeClass();
            }
        }
    );    
}

function listingGraphs() {
    var today_date = $('.today-date').html();
    var table = $('#listing-table');
    var table_rows = $('tr', table);
    var th = $('<th class="days-status-header">'+merlot.i18n.DUE_IN_I18N+'</th>');
    var start_date_header = $('.start-date-header', table);
    var end_date_header = $('.end-date-header', table);
    var estimate_header = $('.estimate-header', table);
    var remaining_header = $('.remaining-header', table);
    var hours_header = $('.hours-header', table);    
        
    var hoursGraph = function(row) {
        //layout setup
        var canvas_elem = '<canvas width="230" height="32"></canvas>';
        var woh_el = $('.worked-hours', row);
        var rem_el = $('.remaining', row);
        var est_el = $('.estimate', row);
        
        var th_hoursusage = $('<th class="hours-usage-header">'+merlot.i18n.HOURS_USAGE_I18N+'</th>');
        estimate_header.before(th_hoursusage);
        estimate_header.remove();
        remaining_header.remove();
        hours_header.remove();
        
        var estimation = est_el.length ? est_el.html()*1 : 0;
        var worked_hours = woh_el.html() ? woh_el.html()*1 : 0;
        var remaining_hours = rem_el.html() ? rem_el.html()*1 : 0;
        if (estimation) {
            est_el.before('<td class="hours-graph">'+canvas_elem+'</td>');

            //bounding box(worked_hours / estimation) * 100;
            var box = 230;
            var lmargin = 15;
            var rmargin = 15; 
            var tmargin = 30;
            var bmargin = 30;
            var bb_start = lmargin; 
            var bb_end = box - rmargin;
            
            //set scale
            canvas = $('.hours-graph canvas', row)[0];
            var ctx = canvas.getContext('2d');
            
            var porcentage = (worked_hours / estimation) * 100;
            var proportion = porcentage * 2 

            if (remaining_hours) {
                var remaing = (remaining_hours / estimation) * 100;
            } else {
                var remaing = 0;
            }
            
            var porcentage_100 = 100;
            var exceded = 0;
            if (porcentage > 100) {
                porcentage_100 = Math.round(porcentage + remaing);
                //we have to calculate the new proportion and exceded value
                proportion = Math.round((200 / (proportion + remaing*2)) * 200);
                exceded = Math.round(200 -(proportion + remaing*2)); 
                remaing = remaing*2               
            } else {
                // we have to check if the remaining hours are exceding the total
                if (porcentage + remaing > 100) {
                    porcentage_100 = Math.round(porcentage + remaing);
                    proportion = (((worked_hours + remaining_hours) / estimation) * 100)*2;
                    proportion = Math.round((200 / (proportion)) * 200);
                    remaing = Math.round(200 -(proportion));
                } else {
                    remaing = remaing*2
                }
            }
            
            var box_height = 15;
            //border box
            ctx.fillStyle = "#CCC";
            ctx.strokeRect((0 + bb_start), 0, 200, box_height);
            
            //background box
            ctx.fillStyle = "#EEE";
            ctx.fillRect(1 + bb_start, 1, 200, box_height);          

            //used time
            ctx.fillStyle = "#6AB42D";
            ctx.fillRect(1 + bb_start, 1, proportion, box_height);      
           
            //exceded time
            if (exceded) {
                ctx.fillStyle = "#D61313";
                ctx.fillRect((1+proportion + bb_start), 1, exceded, box_height);
            }
            
            if (remaing) {
                ctx.fillStyle = "#BED4EB";
                ctx.fillRect((1+(exceded ? exceded+proportion : proportion )+ bb_start), 1, remaing, box_height);
            }
            
            //text 0%
            ctx.fillStyle = "#000";            
            ctx.textBaseline = "top";
            ctx.fillText("0%", 0, 20);
            //text 100 %
            ctx.textAlign = "center";
            ctx.fillText(porcentage_100 + "%", 200, 20);

            //text not exceded %
            if (porcentage > 0 ) {
                ctx.textAlign = "left";
                ctx.fillText((porcentage < 100 ? Math.round(porcentage) : '100') + "%", proportion+3, 5);
            }
        } else {
            if (est_el.length) {
                est_el.before('<td class="worked-hours">'+worked_hours +' '+merlot.i18n.HOURS_I18N+'</td>');
            }
        }
        
        //lets remove the unused columns
        woh_el.remove();
        rem_el.remove();
        est_el.remove();
    };
    table_rows.each(function(){
        hoursGraph($(this));
        var td = $('<td class="days-remaining"></td>');
        var start_date_dom  = $('.start-date', $(this));
        var end_date_dom = $('.end-date', $(this));               
        var start_date  = start_date_dom.html();
        var end_date = end_date_dom.html();   
        var completed = $('.status .completed', $(this));
        if (completed.length == 0) {
            if (start_date && end_date) {
                var s = Date.parse(today_date);
                var e = Date.parse(end_date);
                var diff = e-s;
                var days = Math.floor(diff / (1000*60*60*24));
                if (days < 0) {
                    days = -days;
                    if (days == 1) {
                        var days_status = days + ' ' + merlot.i18n.DAY_BEHIND_I18N;
                    } else {
                        var days_status = days + ' ' + merlot.i18n.DAYS_BEHIND_I18N;
                    }
                } else {
                    if (days == 1) {
                        var days_status = days + ' ' + merlot.i18n.DAY_I18N;
                    } else {
                        var days_status = days + ' ' + merlot.i18n.DAYS_I18N;
                    }
                }
                td.html(days_status);
            } else {
                if (!end_date) {
                    td.html(merlot.i18n.NO_DEADLINE_I18N);
                }
            }
        } else {
            td.html(merlot.i18n.COMPLETED_I18N);
        }
        start_date_dom.before(td);
        start_date_dom.remove();
        end_date_dom.remove();
        
        start_date_header.before(th);
        start_date_header.remove();
        end_date_header.remove();
    });
}
