/**
 * Javascript code for adding accessible controlsbar to flowplayers in the page.
 * Also add WAI-ARIA support for many controls.
 */

jQuery.flowplayer_toolbar = {
    /**
     * Some other script can put this to true to enable also the native controlsbar plugin
     * This is the only way to get features like the fullscreen.
     */
    show_flash_controlsbar: false,
    slider_guide: {
        en: {
            intro:             'How to control the slider',
            left_arrow_label:  'Left arrow',
            left_arrow_help:   'backward 5 seconds',
            right_arrow_label: 'Right arrow',
            right_arrow_help:  'forward 5 seconds',
            page_up_label:     'Page up',
            page_up_help:      'backward 1 minute',
            page_down_label:   'Page down',
            page_down_help:    'forward 1 minute',
            home_label:        'Home key',
            home_help:         'go to beginning of clip',
            end_label:         'End key',
            end_help:          'go to end of clip'
        },

        it: {
            intro:             'Come controllare l\'avanzamento',
            left_arrow_label:  'Freccia sinistra',
            left_arrow_help:   'indietro 5 secondi',
            right_arrow_label: 'Freccia destra',
            right_arrow_help:  'avanti 5 secondi',
            page_up_label:     'Pagina su',
            page_up_help:      'indietro 1 minuto',
            page_down_label:   'Pagina giù',
            page_down_help:    'Avanti 1 minuto',
            home_label:        'Tasto HOME',
            home_help:         'vai all\'inizio del filmato',
            end_label:         'Tasto FINE',
            end_help:          'vai alla fine del filmato'
        },

        da: {
            intro:             'Sådan spoler du',
            left_arrow_label:  'venstre pil',
            left_arrow_help:   'spol 5 sekunder tilbage',
            right_arrow_label: 'højre pil',
            right_arrow_help:  'spol 5 sekunder frem',
            page_up_label:     'Side op',
            page_up_help:      'spol 1 minut tilbage',
            page_down_label:   'Side ned',
            page_down_help:    'spol 1 minut frem',
            home_label:        'Tasten Home',
            home_help:         'gå til klippets start',
            end_label:         'Tasten End',
            end_help:          'gå til klippets slutning'
        }
    }
};

jq(document).ready(function (event) {
    /**
     * Prefix integer with zero when nessessary 
     * @param {Integer} val the value to fill with padding
     */
    function pad(val) {
        val = parseInt(val, 10);
        return val >= 10 ? val : "0" + val;
    }

    /**
     * Display seconds in hh:mm:ss format
     * @param {Integer} sec the value to convert
     */
    var toTime = function (sec) {
        var h = Math.floor(sec / 3600);
        var min = Math.floor(sec / 60);
        sec = sec - (min * 60);
        
        if (h >= 1) {
            min -= h * 60;
            return pad(h) + ":" + pad(min) + ":" + pad(sec);
        }
        
        return pad(min) + ":" + pad(sec);
    };

    // Generate HELP for slider
    var lang = jq("html").attr('lang') || 'en';
    var help_info = jq.flowplayer_toolbar.slider_guide[lang] || jq.flowplayer_toolbar.slider_guide['en'];
    var help = jq('<div></div>').text(help_info.intro);
    var help_instr = jq('<dl></dl>')
            .append('<dt>' + help_info.left_arrow_label + '</dt>\n')
            .append('<dd>' + help_info.left_arrow_help + '</dd>\n')
            .append('<dt>' + help_info.right_arrow_label + '</dt>\n')
            .append('<dd>' + help_info.right_arrow_help + '</dd>\n')
            .append('<dt>' + help_info.page_up_label + '</dt>\n')
            .append('<dd>' + help_info.page_up_help + '</dd>\n')
            .append('<dt>' + help_info.page_down_label + '</dt>\n')
            .append('<dd>' + help_info.page_down_help + '</dd>\n')
            .append('<dt>' + help_info.home_label + '</dt>\n')
            .append('<dd>' + help_info.home_help + '</dd>\n')    
            .append('<dt>' + help_info.end_label + '</dt>\n')
            .append('<dd>' + help_info.end_help + '</dd>\n');
    help.append(help_instr);

    $f("*").each(function (index) {
        var player_index = index;
        this.onLoad(function (event) {
            // Do nothing if the player is "minimal"
            if (!this.getPlugin("controls")) {
                return;
            }
            // ***
            var intervalID = null;
            var hulu_id = null;
            // WAI-ARIA progressbar support
            this.getCommonClip().onBegin(function (event) {
                var player = this;
                intervalID = setInterval(function () {
                    var playingTime = Math.floor(player.getTime());
                    var fullTime = Math.floor(player.getClip().fullDuration);
                    jq('#' + hulu_id + ' div[role=progressbar]')
                        .attr('aria-valuenow', playingTime)
                        .attr('aria-valuemin', 0)
                        .attr('aria-valuemax', fullTime)
                        .attr('aria-valuetext', Math.round(playingTime * 100 / fullTime) + "%");
                    jq('#' + hulu_id + ' .slider')
                        .attr('aria-valuenow', playingTime)
                        .attr('aria-valuemin', 0)
                        .attr('aria-valuemax', fullTime)
                        .attr('aria-valuetext', toTime(playingTime));
                }, 500);
            }).onFinish(function (event) {
                clearInterval(intervalID);
                jq('#' + hulu_id + ' div[role=progressbar]').removeAttr('aria-valuenow')
                    .removeAttr('aria-valuemin').removeAttr('aria-valuemax').removeAttr('aria-valuetext');
                jq('#' + hulu_id + ' .slider').removeAttr('aria-valuenow')
                    .removeAttr('aria-valuemin').removeAttr('aria-valuemax').removeAttr('aria-valuetext');
            });
            // ***

            var p = jq(this.getParent());

            if (!jq.flowplayer_toolbar.show_flash_controlsbar) {
                var flashControls = this.getPlugin("controls");
                flashControls.hide();
                // Better audio support
                if (p.hasClass('audio')) {
                    p.css('height', '0px');
                }
            }

            var p_width = p.width();
            var time_width = (p_width < 400 ? 99 : 129);
            hulu_id = "hulu-" + player_index;
            p.after('<div id="' + hulu_id + '" style="width:' + p_width + 'px" class="hulu">\n'
                + '<a class="play" href="javascript:;" role="button">Play</a>\n'
                + '<div class="track" role="progressbar" style="width:' + (p_width - 46 - 46 - time_width) + 'px">\n'
                + '    <div class="buffer"></div>\n'
                + '    <div class="progress"></div>\n'
                + '    <div class="playhead"><button role="slider" class="slider">&nbsp;</button></div>\n'
                + '</div>\n'
                + '<div class="time" style="width:' + time_width + 'px"></div>\n'
                + '<a class="mute" href="javascript:;" role="button">Mute</a>\n'
                + '</div>\n');
            this.controls(hulu_id);

            // Fix all other positions of the new toolbar
            jq("#" + hulu_id + " a.mute").css('left', p_width - 46);
            jq("#" + hulu_id + " div.time").css('left', p_width - 46 - time_width);

            // Help for slider commands
            var slider = jq(".slider", jq('#'+hulu_id));
            slider.append(help.clone().addClass("hiddenStructure")).focus(function () {
                slider.parent().addClass('focus').find("div").addClass("sliderHelp");
            }).blur(function() {
                slider.parent().removeClass('focus').find("div").removeClass("sliderHelp");
            });

            // Some CSS sugar for play lists
            if (p.hasClass('playListFlowPlayer')) {
                p.removeClass('playListFlowPlayer').addClass('playListFlowPlayerWithControls');
                jq("#"+hulu_id).addClass("forPlayList");
                p.nextAll('.playlist_wrap').addClass('playlistSpace');
            }
        });
    });
});

