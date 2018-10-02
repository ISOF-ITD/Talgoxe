var lastLemma;
var copyString;

function isEmpty(val){
    return (val === undefined || val == null || val.length <= 0);
}
$(document).ready(function() {
    if ($('.add-row').length > 0) {
        lastId = $('.add-row').last()[0].id;
        counter = Number(lastId.replace('add-row-', ''))
    } else {
        counter = 0;
    }

    function addRow(event) {
        event.preventDefault();
        dpos = event.currentTarget.id.replace('add-row-', '');
        counter++
        newRowId = counter
        $('#data-' + dpos).after('<li id="data-' + counter + '"><input type="text" size="3" name="type-' + counter + '" id="type-' + counter + '" class="d-type"><textarea rows="1" style="width: 55%" name="value-' + counter + '" id="value-' + counter + '" class="d-value" /><button class="add-row" id="add-row-' + counter + '" tabindex="-1"><strong>+</strong></button><button class="remove-row" id="remove-row-' + counter + '" tabindex="-1"><strong>-</strong></button><button class="move-row-up" id="row-up-' + counter + '" tabindex="-1"><strong>↑</strong></button><button class="move-row-down" id="row-down-' + counter + '" tabindex="-1"><strong>↓</strong></button><input type="submit" id="spara-och-ladda-om-' + counter + '" class="spara-och-ladda-om" value="💾" tabindex="-1" /></li>');
        $('#add-row-' + counter).click(addRow);
        $('#remove-row-' + counter).click(removeRow);
        $('#type-' + counter).change(checkType);
        $('#value-' + counter).change(checkValue);
        $('#value-' + counter).keydown(hanteraTangent);
        $('#row-up-' + counter).click(moveUp);
        $('#row-down-' + counter).click(moveDown);
        $('#spara-och-ladda-om-' + counter).click(submitOrder);
    }

    function submitOrder(event) {
        ids = [];
        $('.add-row').each(function(event, data) {
            ids.push(data.id.replace('add-row-', ''));
        });
        $(this).after('<input type="hidden" name="order" value="' + ids.join() + '">');
    }

    function removeArticle(event) {
        articleName = $('.article-name').attr('value')
        action = $('.handle-article').attr('action')
        articleId = action.substring(action.lastIndexOf("/") + 1, 100)
        action = action.replace("redigera", "delete")
        if (confirm("Är du säker på att du vill ta bort artikel " + articleName + " (id = " + articleId + ")?")) {
            $('.handle-article').attr('action', action);
        }
        else {
            event.preventDefault();
        }
    }

    $('.add-row').click(addRow);

    $('.copy-rows').click(copyRows);

    $('.remove-row').click(removeRow);

    $('.remove-article').click(removeArticle);

    function removeRow(event) {
        event.preventDefault();
        var id = event.currentTarget.id.replace(/^remove-row-/, '')
        if ($('#type-' + id)[0].value.trim() == '' && $('#value-' + id)[0].value.trim() == '') $(event.currentTarget).parent().remove();
        else if (confirm("Är du säker?")) {
            $(event.currentTarget).parent().remove();
        }
    }

    $('.move-row-up').click(moveUp);

    $('.move-row-down').click(moveDown);

    $('.move-moment-up').click(moveMomentUp);

    $('.move-moment-down').click(moveMomentDown);

    function moveUp(event) {
        event.preventDefault();
        element = $(event.currentTarget).parent();
        prev = element.prev();
        prev.first().before(element.first());
    }

    function copyRows(event) {
        if (!isEmpty(event)) {
            event.preventDefault();
        }
        selectedRows = $(".lemma-list input:checked").parent();
        if (selectedRows.length == 0) {
            alert("Inga rader har markerats!");
        }
        else {
            copyString = '';
            $(".lemma-list input:checked").parent().each(
                function() {
                    type = $(this).children('.d-type');
                    lemma = $(this).children('.d-value');
                    if (copyString != '') {
                        copyString = copyString + '@';
                    }
                    copyString = copyString + type[0].value + '@' + lemma[0].value;
                }
            )
            alert("copyString = " + copyString);
            $(".clipboard")[0].value = copyString;
            // confirm("Är du säker på att du vill kopiera " + selectedRows.length + " rader?");
            // confirm("Är du säker på att du vill kopiera " + JSON.stringify(selectedRows) + " rader?");
        }
    }

    function moveDown(event) {
        event.preventDefault();
        element = $(event.currentTarget).parent();
        next = element.next();
        next.first().after(element.first());
    }

    $('.d-type').change(checkType);

    /* TODO Hämsta listor (typer och landskap) från någon ändepunkt på servern */
    types = [
        'srt', 'sov', 'fo', 'vk', 'vb', 'ssv', 'vr', 'ok', 'ust', 'm1',
        'm2', 'g', 'gp', 'be', 'rbe', 'us', 'sp', 'ssg', 'hr', 'foa',
        'm3', 'm0', 'vh', 'hh', 'okt', 'pcp', 'öv', 'hv', 'övp', 'ref',
        'int', 'obj', 'ip', 'ko', 'kl', 'nyr', 'ti', 'dsp', 'vs', 'gt',
        'gtp', 'bea', 'äv', 'ävk', 'fot', 'tip', 'tik', 'flv', 'lhv', 'gö',
        'göp'
    ];

    /* TODO Check type before! Need to re-add textarea if changing from M1 or M2 to sth. else */
    function checkType(event) {
        var radNummer = this.id.replace(/^type-/, '');
        var type = this.value.trim().toLowerCase();
        if (type == 'm1' || type == 'm2') {
          var valueRuta = $('#value-' + radNummer);
          valueRuta.hide();
          var addAfter = $('#row-down-' + radNummer);
          addAfter.after('<button class="move-moment-down" id="moment-down-' + radNummer + '" tabindex="-1"><strong>⇓</strong></button>');
          addAfter.after('<button class="move-moment-up" id="moment-up-' + radNummer + '" tabindex="-1"><strong>⇑</strong></button>');
        } else if (types.indexOf(type, types) >= 0) {
            var momentUp = $('#moment-up-' + radNummer);
            if (momentUp.attr("id")) {
              momentUp.remove();
              $('#moment-down-' + radNummer).remove();
              $('#value-' + radNummer).show();
              $('#moment-up-' + radNummer).click(moveMomentUp);
              $('#moment-down-' + radNummer).click(moveMomentDown);
            }
            $(this).removeClass("red");
        } else {
            $(this).addClass("red");
        }
    }

    function moveMomentUp(event) {
        moveMoment(event, 'up');
    }

    function moveMomentDown(event) {
        moveMoment(event, 'down');
    }

    function moveMoment(event, dir) {
        event.preventDefault();
        element = $(event.currentTarget).parent();
        if (isM1(element)) {
            isRightMomentType = isM1;
        } else if (isM2(element)) {
            isRightMomentType = isM1OrM2;
        }
        /* TODO A separate function */
        moment = element.prev();
        ids = [];
        if (dir == 'up') {
            while (moment[0].id && !isRightMomentType(moment)) {
                // ids.push(moment[0].id);
                moment = moment.prev();
            }
            console.log(moment);
            console.log(moment.length);
            console.log(moment[0].id);
            console.log(ids);
            if (!moment[0].id) {
                alert("Cannot flytta momentet upp, det är det första i artikeln.");
                return;
            }
        }

        // ids.unshift(moment[0].id);
        nextMoment = element.next();
        var i = 1;
        while (nextMoment.length > 0 && nextMoment[0].id && !isRightMomentType(nextMoment)) {
            console.log(i);
            /*
            if (dir == 'up') ids.unshift(nextMoment[0].id);
            else ids.push(nextMoment[0].id);
            */
            ids.unshift(nextMoment[0].id);
            nextMoment = nextMoment.next();
            if (!nextMoment[0]) {
                if(dir == 'up') {
                    break;
                } else {
                    alert("Kan inte flytta momentet ner, det är det sista i artikeln.");
                    return;
                }
            }
            i++;
        }
        if (dir == 'down') {
            ids = []
            momentAfter = nextMoment.next();
            while (momentAfter.length > 0 && momentAfter[0].id && !isRightMomentType(momentAfter)) {
                ids.unshift(momentAfter[0].id);
                momentAfter = momentAfter.next();
                if (!momentAfter[0]) break;
            }
        }
        if (dir == 'up') ids.unshift(element[0].id);
        /* else ids.unshift(nextMoment[0].id); */
        // else ids.push(moment[0].id);
        /* else ids.push(element[0].id); */
        else {
            /* ids.unshift(element[0].id); */
            /* ids.push(momentAfter[0].id); */
            /* ids.push(moment.next()[0].id); */ // Samma som två rader högre!
            ids.push(element[0].id);
            ids.unshift(nextMoment[0].id);
        }
        console.log(nextMoment);
        console.log(ids);
        console.log("Moving stuff after:");
        console.log(moment);
        for (i in ids) {
            var id = ids[i];
            console.log(id);
            moment.after($('#' + id));
        }
    }

    function isM1(element) {
        return rowType(element) == 'M1';
    }

    function isM2(element) {
        return rowType(element) == 'M2';
    }

    function isM1OrM2(element) {
        return isM1(element) || isM2(element);
    }

    function rowType(row) {
        console.log(row);
        console.log(row.length);
        return $(row[0].id.replace(/^data-/, '#type-'))[0].value.trim().toUpperCase();
    }

    /*
    function moveMomentDown(element) {
        console.log("Starting to move moment down.");
    }
    */

    $('.d-value').change(checkValue); // TODO Klura ut varför .focusout har precis samma effekt (avfyras inte om ingen ändring)

    landskap = {
        'Sk' : 'Skåne', 'Bl' : 'Blek', 'Öl' : 'Öland', 'Sm' : 'Smål', 'Ha' : 'Hall',
        'Vg' : 'Västg', 'Bo' : 'Boh', 'Dsl' : 'Dalsl', 'Gl' : 'Gotl', 'Ög' : 'Östg',
        'Götal' : 'Götal', 'Sdm' : 'Sörml', 'Nk' : 'Närke', 'Vrm' : 'Värml', 'Ul' : 'Uppl',
        'Vstm' : 'Västm', 'Dal' : 'Dal', 'Sveal' : 'Sveal', 'Gst' : 'Gästr', 'Hsl' : 'Häls',
        'Hrj' : 'Härj' , 'Mp' : 'Med', 'Jl' : 'Jämtl', 'Åm' : 'Ång', 'Vb' : 'Västb',
        'Lpl' : 'Lappl', 'Nb' : 'Norrb', 'Norrl' : 'Norrl'
    };
    longLandskap = [];
    for (key in landskap) longLandskap.push(landskap[key]);

    String.prototype.toTitleCase = function() {
        return this.substring(0, 1).toUpperCase() + this.substring(1).toLowerCase();
    }

    function checkValue(event) {
        var type = rowType($(this).parent());
        if (type == 'G') {
            var namn = this.value.trim().toTitleCase();
            if (namn in landskap) {
                this.value = landskap[namn];
                $(this).removeClass("red");
            } else if (longLandskap.indexOf(namn) >= 0) {
                $(this).removeClass("red");
            } else {
                $(this).addClass("red");
            }
        }
    }

    $('.spara-och-ladda-om').click(submitOrder);

    $('#sok-artikel').on('keyup', searchArticles);

    function searchArticles() {
        string = this.value
        if (string == "") {
            hideEverything();
            return;
        }

        $('#sökstrang').html(string);
        regexp = new RegExp('^' + string.replace(/[-?,()]/g, "").toLowerCase());
        var nbhits = 0;
        $(".ordlistelement").each(function(i, childElement) {
            element = $(childElement).parent();
            if ($(childElement).attr("value").match(regexp)) { element.show(); nbhits++; }
            else element.hide();
        });
        if (nbhits == 0) $('#searching-feedback').show();
        else $('#searching-feedback').hide();
    }

    function hideEverything() {
        $(".ordlistelement").each(function(i, childElement) {
            $(childElement).parent().hide();
        });
    }

    $('.träff .träffelement').click(function(event) { toggleArticle($(event.currentTarget).parent()) });
    $('.virgin').click(function(event) { fetchArticle(event.currentTarget); });

    function showArticle(parent) {
        $(parent.children()[4]).removeClass("hidden");
        $(parent.children()[2]).html('▾');
        $(parent.children()[3]).hide();
        $(parent.children()[4]).show();
        parent.children().last().show();
    }

    function hideArticle(parent) {
        $(parent.children()[4]).addClass("hidden");
        $(parent.children()[2]).html('▸');
        $(parent.children()[3]).show();
        $(parent.children()[4]).hide();
        parent.children().last().hide();
    }

    function toggleArticle(element) {
        console.log(element);
        var artId = element[0].id.replace(/^lemma-/, 'artikel-');
        article = $('#' + artId);
        if (article.hasClass("hidden")) {
            showArticle(article.parent());
        } else {
            hideArticle(article.parent());
        }
    }

    function fetchArticle(element) {
        var artId = element.id.replace(/^lemma-/, '');
        var artUrl = window.location.href.replace(/\/talgoxe.*$/, '/talgoxe/artikel/');
        $.get(artUrl + artId).done(function(data) {
            $('#artikel-' + artId).html(data);
            $(element).off("click");
            $(element).removeClass("virgin");
        });
    }

    $('#visa-alla, #visa-alla-text').click(function() {
        if ($('#visa-alla-text').html() == "Visa alla") {

            $('.träff').each(function(i, lemma) {
                showArticle($(lemma));
            });

            $('.virgin').each(function(i, element) {
                fetchArticle(element);
            });

            $('#visa-alla').html('▾'); /* Inte ⚾! */
            $('#visa-alla-text').html('Dölja alla');
        } else {
            $('#visa-alla').html('▸');
            $('#visa-alla-text').html('Visa alla');

            $('.träff').each(function(i, lemma) {
                hideArticle($(lemma));
            });
        }
    });

    $('#skapa-pdf').click(function(event) { createPDF(event.currentTarget); });

    function createPDF(element) {
        console.log(element);
        $(element).html("Förbereder&nbsp;PDF...");
        articles = collectArticles();
        console.log("Article IDs:");
        console.log(articles);
        url = printableEndpoint('pdf', articles);
        console.log("Getting " + url);
        $.get(url).done(function(data) {
            console.log("GET completed!  Data:");
            console.log(data);
            $(element).off('click');
            $(element).attr("href", data.trim());
            $(element).html("Ladda&nbsp;ner&nbsp;PDF");
        });
    }

    function collectArticles() {
        articles = [];
        $('.träff').each(function(i, article) {
            articles.push(article.id.replace(/^lemma-/, ''));
        });

        console.log("Samlat in artiklar:");
        console.log(articles);
        return articles;
    }

    function printableEndpoint(format, articles) {
        return window.location.href.replace(/\/talgoxe.*/, '/talgoxe/print-on-demand') + '/' + format + '?ids=' + new String(articles);
    }

    $('#skapa-odf').click(function(event) { createODF(event.currentTarget); });

    function createODF(element) {
      $(element).html("Förbereder&nbsp;ODF...");
      articles = collectArticles();
      url = printableEndpoint('odt', articles);
      $.get(url).done(function(link) {
        $(element).off('click');
        $(element).attr("href", link.trim());
        $(element).html("Ladda&nbsp;ner&nbsp;ODF");
      });
    }

    $('.toselect').click(selectLemma);

    function selectLemma(event) {
        if (!lastLemma) lastLemma = $('#lemma-0');

        console.log(event.currentTarget);
        name = $(event.currentTarget).attr("name").replace(/^select/, 'selected');
        console.log(name);
        /* lemma = $('[name="' + name + '"]'); */
        /*
        lemma = $('#li-' + name);
        console.log(lemma);
        */
        var id = name.replace(/^selected-/, '');
        console.log(id);
        lemma = $($('[name="select-' + id + '"]').parent().children()[1]).html().trim();
        console.log(lemma);
        if ($(event.currentTarget).is(':checked')) {
            /* lemma.show(); */
            lastLemma.before('<li id="li-select-' + id + '" class="nobullet">' + lemma + ' <input type="checkbox" id="ta-bort-' + id + '" class="ta-bort" /> Ta bort <input type="hidden" name="selected-' + id + '" /></li>');
            tickBox = $('#ta-bort-' + id);
            tickBox.click(removeLemma);
            if (tickBox.is(':checked')) tickBox.click()
            /* lemma.after('<input type="hidden" name="selected-' + id + '" />'); */
        } else {
            $('#li-select-' + id).remove();
            /*
            lemma.hide();
            $('[name="selected-' + id + '"]').remove();
            */
        }
    }

    $(".ta-bort").click(removeLemma);

    function removeLemma(event) {
        console.log("Hej hej hej!");
        lemma = $(event.currentTarget).parent();
        var name = $(event.currentTarget).attr("name");
        if (name && name.match(/^selected-bokstav/)) {
            bokstav = name.replace(/^selected-bokstav-/, '');
            $('[name="selected-bokstav-' + bokstav + '"]').parent().remove();
            selector = '[name="bokstav-' + bokstav + '"]'
        } else  {
            var id = lemma.attr("id").replace(/^li-select-/, '');
            console.log(lemma);
            lemma.remove();
            $('[name="selected-' + id + '"]').remove();
            selector = '[name="select-' + id + '"]';
        }
        console.log(selector);
        lemmaLeft = $(selector);
        console.log(lemmaLeft);
        lemmaLeft.click();
    }

    $("#selectalla").click(selectAll);

    function selectAll(event) {
        event.preventDefault();
        $('[style="display: list-item;"]').each(function(i, element) {
            if (!element.id.match(/^li-selected-/)) {
                console.log($(element).children().first());
                var id = $(element).children().first().attr("name").replace(/^select-/, '')
                console.log(id);
                $('[name="select-' + id + '"]').each(function(i, element) {
                    if (!$(element).is(':checked')) $(element).click();
                });
                rightHandSide = $('#ta-bort-' + id);
                if (rightHandSide.is(':checked')) rightHandSide.click();
            }
        });
    }

    $('#ta-bort-alla').click(removeAll);

    function removeAll(event) {
        event.preventDefault();
        $('.ta-bort').each(function(i, element) {
            console.log(element);
            /* var id = $(element).attr("id").replace(/^ta-bort-/, ''); */
            $(element).click();
        });
    }

    $('.bokstav [type="checkbox"]').click(addBokstav);

    function addBokstav(event) {
        if (!lastLemma) lastLemma = $('#lemma-0');
        box = $(event.currentTarget);
        bokstav = box.attr("name").replace(/^bokstav-/, '');
        if (box.is(':checked')) {
            lastLemma.before('<li class="nobullet">' + bokstav + ' – hela bokstaven <input type="checkbox" name="selected-bokstav-' + bokstav + '" class="ta-bort" /> Ta bort</li>');
            removeBox = $('[name="selected-bokstav-' + bokstav + '"]');
            removeBox.click(removeLemma);
        } else {
            $('[name="selected-bokstav-' + bokstav + '"]').parent().remove();
        }
    }

    $('.bokstav .ta-bort').click(removeBokstav);

    function removeBokstav(event) {
        box = $(event.currentTarget);
        bokstav = box.attr("name").replace(/^selected-bokstav-/, '');
        $('[name="selected-bokstav-' + bokstav + '"]').parent().remove();
        $('[name="bokstav-' + bokstav + '"]').click();
    }

    $('#skapa-docx').click(createDOCX);

    function createDOCX(event) {
        element = $(event.currentTarget);
        element.html("Förbereder&nbsp;Word‑dokument...");
        articles = collectArticles();
        url = printableEndpoint('docx', articles);
        $.get(url).done(function(link) {
            element.off("click");
            element.attr("href", link.trim());
            element.html("Ladda&nbsp;ner&nbsp;Wordfilen");
        });
    }

    $('#omordna').click(omordna);

    function omordna() {
        console.log(this);
        if ($('.flytta-upp').hasClass("hidden")) {
            $('.flytta-upp, .flytta-ner, #spara-ordning').show();
            $('.flytta-upp, .flytta-ner, #spara-ordning').removeClass("hidden");
        } else {
            $('.flytta-upp, .flytta-ner, #spara-ordning').hide();
            $('.flytta-upp, .flytta-ner, #spara-ordning').addClass("hidden");
        }
    }

    $('.flytta-upp').click(flyttaUpp);

    function flyttaUpp(event) {
        event.preventDefault();
        rad = $(this).parent();
        upp = rad.prev();
        upp.before(rad);
    }

    $('.flytta-ner').click(flyttaNer);

    function flyttaNer(event) {
        event.preventDefault();
        rad = $(this).parent();
        ner = rad.next();
        ner.after(rad);
    }

    $('.d-value').keydown(hanteraTangent);

    var speciellaTecken = {
        'initial' : {
            123 : '¶',
            119 : '~'
        },
        'control' : {
            65 : 'â',
            79 : 'ô',
            85 : 'û',
            59 : 'ô',
            68 : 'ð',
            76 : '£',
            222 : 'â'
        }
    }

    function speciellTecken(element, tecken) {
        console.log("foo");
        console.log(element);
        var text = element.value;
        textFöre = text.substring(0, element.selectionStart);
        var cursor = element.selectionStart;
        textEfter = text.substring(cursor, text.length);
        element.value = textFöre + tecken + textEfter;
        element.selectionStart = element.selectionEnd = cursor + 1;
    }

    function hanteraTangent(event) {
        console.log(event.keyCode);
        console.log(event.which);
        if (event.ctrlKey) {
            if (event.keyCode in speciellaTecken.control) {
                event.preventDefault();
                speciellTecken(this, speciellaTecken.control[event.keyCode]);
            }
        } else {
            if (event.keyCode in speciellaTecken.initial) {
                event.preventDefault();
                speciellTecken(this, speciellaTecken.initial[event.keyCode]);
            }
        }
        console.log('--- igen ---');
        console.log(event.charCode);
        console.log(event.ctrlKey);
        console.log('--- ---');
    }
});
