import 'bootstrap';
import $ from 'jquery';
window.jQuery = $;
window.$ = $;


const makeFlash = (message, category) => {
  category = (typeof category === 'undefined') ? 'secondary' : category;
  $(".flashes").append(`<div class="alert alert-${category} alert-dismissible fade show" role="alert">
    ${message}
    <button type="button" class="close" data-dismiss="alert" aria-label="Close">
    <span aria-hidden="true">&times;</span>
    </button>
    </div>`);
};


const clearFlashes = () => {
  $(".flashes").html("");
};


const trackProfile = (steamid, note) => {
  return $.post('/track',
    {steamid: steamid,
     note: note});
};


const untrackProfile = (steamid) => {
  return $.post('/untrack',
   {steamid: steamid});
};


const trackProfileButton = (e) => {
  const button = $(e.target);
  const steamid = button.data('steamid');
  const note = $('#profile-tracking-note').val();
  trackProfile(steamid, note).then(() => {
    window.location.reload();
  });
};


const untrackProfileButton = (e) => {
  const button = $(e.target);
  const steamid = button.data('steamid');
  untrackProfile(steamid).then(() => {
    window.location.reload();
  });
};


const trackProfileModal = (e) => {
  const data_div = $(e.target).parent();
  const personaname = data_div.data('personaname');
  const steamid = data_div.data('steamid');
  $('#track-note').val('');
  const getNote = () => $('#track-note').val();

  $('#trackModalTitle').text('Track ' + personaname);
  const modal = $('#trackModal');

  $('#track-modal-btn').unbind('click');
  $('#track-modal-btn').click(() => {
    modal.modal('hide');
    const note = getNote();
    trackProfile(steamid, note).then((data) => {
      if (data.code === 200){
        data_div.data('note', note);
        data_div.children('.track-button').addClass('d-none');
        data_div.children('.untrack-button').removeClass('d-none');
      }
      else {
        makeFlash('Something went wrong', 'danger');
      }
    });
  });
  modal.modal();
};


const untrackProfileModal = (e) => {
  const data_div = $(e.target).parent();
  const personaname = data_div.data('personaname');
  const steamid = data_div.data('steamid');
  let note = data_div.data('note');
  note = note === '' ? 'None' : note;
  $('#untrack-note').text(note);
  $('#untrackModalTitle').text('Stop tracking ' + personaname + '?');
  const modal = $('#untrackModal');

  $('#untrack-modal-btn').unbind('click');
  $('#untrack-modal-btn').click(() => {
    modal.modal('hide');
    untrackProfile(steamid).then((data) => {
      if (data.code === 200){
        data_div.data('note', '');
        data_div.children('.track-button').removeClass('d-none');
        data_div.children('.untrack-button').addClass('d-none');
      }
      else {
        makeFlash('Something went wrong', 'danger');
      }
    });
  });
  modal.modal()
};


$('.track-button').bind("click", trackProfileModal);
$('.untrack-button').bind("click", untrackProfileModal);
$('.track-button-profile').bind("click", (e) => trackProfileButton(e));
$('.untrack-button-profile').bind("click", untrackProfileButton);

window.makeFlash = makeFlash;
window.clearFlashes = clearFlashes;
