$(document).ready(function() {
    names = {
    }

    function addRow(event) {
        console.log(event.currentTarget.id);
        dpos = event.currentTarget.id.replace('button-', '');
        if (!names[dpos]) { names[dpos] = 0 }
        $('#data-' + dpos).after('<li><input type="text" size="3" name="type-' + dpos + '.' + names[dpos] + '> <input type="text" size="16"> <button><strong>+</strong></button></li>');
        console.log("Adding a row after d.pos " + dpos + " ...");
    }

    $('.addRow').click(function(event) {
        event.preventDefault();
        addRow(event);
    });
});
