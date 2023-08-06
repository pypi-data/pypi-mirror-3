var dateFormat = "yy-mm-dd";
$(document).ready(function() {

    //lets create a basic structure for the tooltip in the loglinks
    var log_tooltip = $('<div class="tooltip log-row">'+
                            '<a class="delete"><img alt="'+merlot.i18n.DELETE_I18N+'"src="/fanstatic/merlot/images/close.png"></a>'+
                            '<div class="ajax-load">'+
                                '<img alt="ajax-load" src="/fanstatic/merlot/images/ajax-load.gif">'+
                            '</div>'+
                            '<div class="log-form-container"></div>'+
                        '</div>');
    $('.log-link').after(log_tooltip);
    
    //tooltip config
    $('.log-link').tooltip({
        effect: 'slide',
        tipClass:'log-row',
        position: ['center', 'left'],
        relative: true,
        cancelDefault: false,
        events: {
            def:"click, mouseup",
            tooltip: "mouseenter"
        },
        onShow: function() {
		            var action = this.getTrigger().attr('href') + '/@@add-log-ajax';
		            var action_link = this.getTrigger();
		            var tip_layout = this.getTip();
                    $('.log-form-container', tip_layout).empty();
                    $.ajax({
                        url:action,
                        dataType:'html',
                        async: true,
                        data:{'ajax':true},
                        success: function(data) {
                            $('.log-row .ajax-load').css('display', 'none');
                            form = $(data);                           
                            logFormDataHanddler(form, tip_layout, action_link);                             
                        }
                    });
                },
        api: true                
    });
    //the close button inside the tooltip is going to work hide it
    $('.log-row .delete').click(function(){
        $(this).closest('tr').removeClass('selected');    
        $(this).parents('.actions').find('.log-link').tooltip().hide();
    });
    $('.log-link').click(function(e){
        $(this).closest('tr').addClass('selected');
        e.preventDefault(); 
    });       

    function logFormDataHanddler(form, log_row, log_link) {
        row = $('.log-form-container',log_row).append(form);
        form_obj = $('form', row);
        form_hours = $('#form\\.hours', log_row);
        form_remaing = $('#form\\.remaining', log_row);
        
        //focus in the first input
        $('input:first',log_row).focus();
        calculateRemaingHours(form_hours, form_remaing);

        //bind the calendar
        dateTranslator($("#form\\.date", log_row), $(".date-translated", log_row));       
        $("#form\\.date", log_row).datepicker({
            "dateFormat": dateFormat,
            "showOn": "button",
            "buttonImage": "/fanstatic/merlot/images/calendar.gif",
            "buttonImageOnly": true,
            "constrainInput": false
        });
        //we bind the submit and we generate our own submit
        var button = $('.actionButtonsLog .button');
        button.click(function(e){
            var values = {};
            $.each(form_obj.serializeArray(), function (i, field) {
                values[field.name] = field.value;
            });
            values[button.attr('name')] = button.attr('value');
            var form_action = form_obj.attr('action');
            $.ajax({
                url: form_action,
                data: values,
                dataType:'json',
                success: function(data){
                    row.empty();                
                    row.append('<div class="success">'+
                                   '<h3><img alt="success" class="success" src="/fanstatic/merlot/images/check.png">'+merlot.i18n.SUCCESS_I18N+'</h3>'+
                                   '<a class="more-logs" href="#">'+merlot.i18n.MORE_I18N+'</a>'+
                                '</div>');
                    $('.success', row).hide().fadeIn('slow');
                    more_logs_link = $('.more-logs', row);
                    more_logs_link.focus();
                    more_logs_link.click(function(e){
                        $('.log-row .delete').trigger('click');
                        log_link.trigger('click');
                        return false;
                    });
                },
                error: function(XMLHttpRequest, textStatus, errorThrown) {
                        console.log(errorThrown);
                    }
            });

            e.preventDefault();
            return false;
        });
    }
});
