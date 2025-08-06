// Fix stange file names or spelling mistakes
name_overrides = {
  '/audio_clips/af07-77b16e16ecf1.wav': 'MacGyver',
  '/audio_clips/unsceduald offworld activation.wav': 'Unscheduled Offworld Activation',
  '/audio_clips/we thought we compenstated but aparently not.wav': 'We Thought We Compensated But Apparently Not'
}

function update_audio_clips(){
  $.ajax({
      dataType: "json",
      url: "/stargate/get/audio_clips",
      success: function( json ) {
          audio_clips = json
          load_audio_clips()
      },
      error: function (xhr, textStatus, errorThrown){
          console.log("Failed to load Sound Board from Stargate")
          $("<div>Failed to load Sound Board from Stargate</div>").dialog();
      }
  });
}
function load_audio_clips(){
    $("#sound_board_summary").html("<span class='sound-board-row-summary'><span class='clip-count' style='padding:0px;'>" + audio_clips.length + "</span> Audio Clips</span>")

    group = '';

    $.each(audio_clips, function( index, value ) {
        
        curr_group = value.split('/').at(-2) ?? 'Stargate';
        curr_group = format_text(curr_group);

        if (curr_group !== group) {
          group = curr_group;
          $("#presets").append('<div class="sound-board-row-header col-sm"><div class="sound-board-col-header">' + group + '</div></div>')
        }

        title = name_overrides[value] ?? format_text(value.split('/').at(-1).split('.')[0]);

        $("#presets").append('<div class="sound-board-row sound-board-row-'+index+' col-sm"><div class="sound-board-col-names">' + title + '</div></div>');
        $('.sound-board-row-'+index).click(() => play_audio_clip(value));
    });
}

function format_text(text) {
  text = text.replaceAll('_', ' ');
  words = text.split(' ').filter(x => x !== undefined && x !== '');
  words = words.map(word => word[0].toUpperCase() + word.slice(1));
  return words.join(' ');
}

function play_audio_clip(audio_clip) {
  $.post({
      url: "/stargate/do/audio_play",
      data: JSON.stringify({
        clip: audio_clip
      }),
      error: function (xhr, textStatus, errorThrown){
          console.log("Failed to play audio clip from Stargate")
          $("<div>Failed to play audio clip from Stargate</div>").dialog();
      }
  });
}

function poll_success(singleShot, data){
  // If we're coming back from being offline, update the address book

  if (!is_online){
    update_audio_clips()
  }

  // Hide the offline modal
  hideOfflineModal()

  poll_delay = poll_delay_default
  // Schedule the next polling
  if ( !singleShot ){
      setTimeout(function(){doPoll( false ); }, poll_delay);
  }
}
