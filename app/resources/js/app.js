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
}

const clearFlashes = () => {
  $(".flashes").html("");
}


window.makeFlash = makeFlash;
window.clearFlashes = clearFlashes;
