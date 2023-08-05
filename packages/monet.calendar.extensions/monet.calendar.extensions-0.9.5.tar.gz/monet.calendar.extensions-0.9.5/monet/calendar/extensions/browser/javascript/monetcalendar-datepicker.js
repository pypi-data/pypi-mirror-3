/**
 * Calendar viewlet controls
 */

jQuery.plonesimplemessage = function(title, message, element) {
    element.empty().append('<dt>'+title+'</dt>').append('<dd>'+message+'</dd>').slideDown('fast');
};

jq(document).ready(function() {
    
    if (!jq.datepicker) {
        return;
    };
    
    jq("head").append('<style type="text/css">#ui-datepicker-div {z-index: 10}</style>');
    
    /**
     * Context URL to be used for all AJAX call
     */
    var call_context = jq("head base").attr('href');
    if (call_context.charAt(call_context.length-1)!='/') call_context=call_context+'/';

    /*
     * Don't want to call the context when is in the portal factory. See the Ale's blog post:
     * http://blog.redturtle.it/redturtle-blog/2010/03/11/careful-with-that-ajax-eugene
     */
    if (call_context.indexOf('/portal_factory')>-1) {
        call_context=call_context.substring(0,call_context.indexOf('/portal_factory')+1);
    };
    
    var lang = jq("html").attr("lang") || 'en';
    if (lang !== 'en') {
        jq("head").append('<script type="text/javascript" src="jquery.ui.datepicker-' + lang + '.js"></script>');
    };
    
    /**
     * Perform an AJAX call to validate the date fields
     */
    var paramsRemoteValidation = function() {
        jq.getJSON(call_context+ '/@@monetsearchevents_validation',
                   {
                       fromDay: jq("#fromDay").val(), fromMonth: jq("#fromMonth").val(), fromYear: jq("#fromYear").val(),
                       toDay: jq("#toDay").val(), toMonth: jq("#toMonth").val(), toYear: jq("#toYear").val()
                   },
                   function(data, textStatus) {
                           if (data.error) {
                               if (jq.plonesimplemessage) {
                                jq.plonesimplemessage(data.title, data.error, jq("#dateErrors"));
                            }
                            else {
                                alert(data.error);
                            }
                            jq("#searchEvents").addClass("searchDisabled");                                                
                        }
                        else {
                            jq("#dateErrors").slideUp('fast');
                            jq("#searchEvents").removeClass('searchDisabled');
                        }
                   }
        );
    };
    
    var messages = jq('<dl id="dateErrors" class="portalMessage error" style="display:none"></dl>');
    jq("#searchBar").prepend(messages);
    
    // Controls over the calendars
    var suffixes = ['from', 'to'];
    jq(".searchBarFrom,.searchBarTo").each(function(index, elem) {
        // from searchBarXXX get XXX
        var suffix = suffixes[index];
        var dateField = jq('<input type="hidden" value="" />');
        jq(elem).append(dateField);
        dateField.datepicker({showOn: 'button', 
                              buttonImage: call_context+'/popup_calendar.gif', 
                              buttonImageOnly: true,
                              showAnim: '',    
                              dateFormat: 'yy-mm-dd',
                              beforeShow: function(input, inst) {
                                jq(this).val(jq("#"+suffix+"Year").val()+"-"+jq("#"+suffix+"Month").val()+'-'+parseInt(jq("#"+suffix+"Day").val()));
                                return {}
                              },
                              onSelect: function(dateText, inst) {
                                    var ds = dateText.split("-");
                                    jq("#"+suffix+"Year").val(ds[0]);
                                    jq("#"+suffix+"Month").val(ds[1]);
                                    jq("#"+suffix+"Day").val(ds[2]);
                                    // Now the AJAX validation
                                    paramsRemoteValidation();
                              },
                            }, jq.datepicker.regional[lang]
        );
        
        jq("#searchEvents").click(function(e) {
            if (jq(this).hasClass("searchDisabled")) e.preventDefault();
        });
    });
    
    // Controls over combos
    jq(".searchBarFrom select,.searchBarTo select").change(function(e) {
        // Now the AJAX validation
        paramsRemoteValidation();
    });
    
});
