var articleItemCount;
var lastLemma;

function addToken() {
    // Add token that confirms login to AJAX request.
    var csrfToken;

    csrfToken = jQuery("[name=csrfmiddlewaretoken]").val();
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            xhr.setRequestHeader("X-CSRFToken", csrfToken);
        }
    });
}

function copySelectedArticleItems() {
    var copyString;
    var copyStringObject;
    var selectedRows;

    selectedRows = $(".lemma-list input:checked").parent();
    if (selectedRows.length == 0) {
        alert("Inga rader har markerats!");
    }
    else {
        copyString = '';
        $(".lemma-list input:checked").parent().each(
            function() {
                var type = $(this).children('.d-type');
                var lemma = $(this).children('.d-value');
                if (lemma.length == 0) {
                    lemma = '';
                }
                else {
                    lemma = lemma[0].value;
                }
                if (copyString != '') {
                    copyString = copyString + '@';
                }
                copyString = copyString + type[0].value + '@' + lemma;
            }
        )
        copyStringObject = { clipboard: copyString };

        // Send clipboard to server.
        addToken();
        $.post(
            getWebAddress() + "update_clipboard",
            copyStringObject
        );
    }
}

function getWebAddress(){
    // Get web address that can be used as base address in AJAX requests.
    // This function only works in the edit article page.
    var webAddress;

    webAddress = $('.edit-article').attr('action');
    webAddress = webAddress.substring(0, webAddress.indexOf("edit"));
    return webAddress;
}

function isEmpty(val){
    return (val === undefined || val == null || val.length <= 0);
}

function isNotEmpty(val){
    return !isEmpty(val);
}

function moveArticleItemDown(event) {
    var articleItem;
    var articleItemNext;

    event.preventDefault();
    articleItem = $(event.currentTarget).parent();
    articleItemNext = articleItem.next();
    articleItemNext.first().after(articleItem.first());
}

function moveArticleItemUp(event) {
    var articleItem;
    var articleItemPrevious;

    event.preventDefault();
    articleItem = $(event.currentTarget).parent();
    articleItemPrevious = articleItem.prev();
    articleItemPrevious.first().before(articleItem.first());
}

function pasteArticleItems(event) {
    var articleItems;
    var selectedArticleItems;

    event.preventDefault();
    selectedArticleItems = $(".lemma-list input:checked").parent();
    if (isEmpty(selectedArticleItems)) {
        alert("Markera var raderna ska klistras in!");
    }
    else {
        // Get clipboard from server.
        addToken();
        $.post(
            getWebAddress() + "get_clipboard",
            null,
            function(result) {
                articleItems = result.clipboard.split("@");
                // alert(JSON.stringify(articleItems));

                if (isEmpty(articleItems)) {
                    alert("Finns inga rader att klistra in!");
                }
                else {
                    index = 0;
                    row = $(".lemma-list input:checked").first().parent();
                    $(row).children('.d-type').val(articleItems[index]);
                    index = index + 1;
                    $(row).children('.d-value').val(articleItems[index]);
                    index = index + 1;
                    $(row).children('.d-type').trigger('change');
                    while (index < articleItems.length){
                        $(row).children('.add-row').trigger('click');
                        row = $(row).next();
                        $(row).children('.d-type').val(articleItems[index]);
                        index = index + 1;
                        $(row).children('.d-value').val(articleItems[index]);
                        index = index + 1;
                        $(row).children('.d-type').trigger('change');
                    }
                }
                $(".lemma-list input:checked").prop( "checked", false );
            }
        );
   }
}

function removeArticle(event) {
    articleName = $('.article-name').attr('value')
    action = $('.edit-article').attr('action')
    articleId = action.substring(action.lastIndexOf("/") + 1, 100)
    action = action.replace("edit", "delete")
    if (confirm("Är du säker på att du vill ta bort artikel " + articleName + " (id = " + articleId + ")?")) {
        $('.edit-article').attr('action', action);
    }
    else {
        event.preventDefault();
    }
}

function removeArticleItem(event) {
    var articleItemId;

    event.preventDefault();
    articleItemId = event.currentTarget.id.replace(/^remove-row-/, '')
    if ($('#type-' + articleItemId)[0].value.trim() == '' &&
        $('#value-' + articleItemId)[0].value.trim() == '') {
        $(event.currentTarget).parent().remove();
    }
    else if (confirm("Är du säker?")) {
        $(event.currentTarget).parent().remove();
    }
}

function resetArticleSearchCriteria() {
    addToken();
    $.post(
        getWebAddress() + "reset_article_search_criteria",
        null,
        function(result) {
            $(".search-select-field").val('Lemma');
            $(".search-compare-type").val('StartsWith');
            $(".search-string").val('');
        }
    );

    return false;
}

function searchArticlesAutocomplete() {
    var element;
    var foundArticleCount;
    var regexp;
    var searchString;

    searchString = this.value
    if (searchString == "") {
        $(".ordlistelement").each(function(i, childElement) {
            $(childElement).parent().hide();
        });
        return;
    }

    $('#sökstrang').html(searchString);
    regexp = new RegExp('^' + searchString.replace(/[-?,()]/g, "").toLowerCase());
    foundArticleCount = 0;
    $(".ordlistelement").each(function(i, childElement) {
        element = $(childElement).parent();
        if ($(childElement).attr("value").match(regexp)) { element.show(); foundArticleCount++; }
        else element.hide();
    });
    if (foundArticleCount == 0) {
        $('#searching-feedback').show();
    }
    else {
        $('#searching-feedback').hide();
    }
}

function searchArticlesBySearchCriteria(event) {
    let compareType;
    let searchText;
    let searchType;

    event.preventDefault();

    // Get data from html page.
    var searchCriteriaArray = [];
    compareType = $("#search-compare-type1").val();
    searchString = $("#search-string1").val();
    searchType = $("#search-type1").val();
    var searchCriteria = { compare_type: compareType,
                           search_string: searchString,
                           search_type: searchType
                         };
    searchCriteriaArray.push(searchCriteria);
    compareType = $("#search-compare-type2").val();
    searchString = $("#search-string2").val();
    searchType = $("#search-type2").val();
    searchCriteria = { compare_type: compareType,
                           search_string: searchString,
                           search_type: searchType
                         };
    searchCriteriaArray.push(searchCriteria);
    compareType = $("#search-compare-type3").val();
    searchString = $("#search-string3").val();
    searchType = $("#search-type3").val();
    searchCriteria = { compare_type: compareType,
                           search_string: searchString,
                           search_type: searchType
                         };
    searchCriteriaArray.push(searchCriteria);
    var articleSearchCriteria = { searchCriteriaArray : searchCriteriaArray }
    // alert(compareType + ' ' + searchString + ' ' + searchType);

    // Get articles from server.
    addToken();
    $.post(
        getWebAddress() + "get_articles_by_search_criteria",
        articleSearchCriteria,
        function(result) {
            var appendTo = $('.search-article-result');
            var articleCount = $('#number-of-found-articles');
            webAddress = $('.edit-article').attr('action');
            webAddress = webAddress.substring(0, webAddress.indexOf("edit"));
            appendTo.empty();
            articleCount.empty();

            // Show articles.
            if (isNotEmpty(result) && isNotEmpty(result.articles)) {
                var articleIndex;
                articleCount.append('Antal artiklar = ' + result.articles.length);
                for (articleIndex = 0; articleIndex < result.articles.length; articleIndex++) {
                    var rankString;
                    if (result.articles[articleIndex].rank > 0) {
                        rankString = '<sup>' + result.articles[articleIndex].rank + '</sup>'
                    }
                    else {
                        rankString = '';
                    }

                    var onClick = ' onclick="showArticle(' +
                                   result.articles[articleIndex].id +
                                   ')"';
                    appendTo.append('<li class="nobullet search-article-result-row">' +
                                   '<a href="'+
                                   webAddress +
                                   'edit/' +
                                   result.articles[articleIndex].id +
                                   '" value="' +
                                   result.articles[articleIndex].id +
                                   '"' +
                                   onClick +
                                   '>' +
                                   rankString +
                                   result.articles[articleIndex].lemma +
                                   '</a>' +
                                   '<button type="button" class="show-article"' +
                                   onClick +
                                   '>Visa</button>' +
                                   '<input type="checkbox" class="select-article" ' +
                                   'onClick="showArticleCheckedChange(' +
                                   result.articles[articleIndex].id + ')">' +
                                   '</li>');
                }

                // $('.show-article').click(showArticle);
                // alert(JSON.stringify(result));
            }
            else {
                articleCount.append('Antal artiklar = 0');
            }
        }
    );
}

function showAllArticles(event) {
    var articleIds;

    event.preventDefault();
    // alert(JSON.stringify(idArray));
    articleIds = $(".search-article-result a").map(function(){
        var webAddress = this.href;
        var indexOf = webAddress.lastIndexOf('/');
        return webAddress.substring(indexOf + 1);
    }).get();
    showArticlesByIds(articleIds)
    return false;
}

function showArticle(articleId) {
    var articleIds;

    articleIds = [];
    articleIds.push(articleId);
    showArticlesByIds(articleIds)
    return false;
}

function showArticleCheckedChange(articleId) {
    var checkedArticleIdsArray = $(".select-article:checked").parent().children("a").map(function(){
        var webAddress = this.href;
        var indexOf = webAddress.lastIndexOf('/');
        return webAddress.substring(indexOf + 1);
    }).get();
    var checkedArticles = { checkedArticleIds : checkedArticleIdsArray };

    addToken();
    $.post(
        getWebAddress() + "update_checked_articles",
        checkedArticles
    );
    // alert(JSON.stringify(articleId));
    return false;
}

function showArticlesByIds(articleIds) {
    var showArticleIds;

    // Get articles as html.
    showArticleIds = { showArticleIds : articleIds }
    addToken();
    $.post(
        getWebAddress() + "get_articles_html",
        showArticleIds,
            function(result) {
            var appendTo = $('#artikel');
            appendTo.empty();
            appendTo.append(result.articlesHtml);
            getPdfFile = $('#get-pdf-file').attr('target', '_blank')
        }
    );

    return false;
}

function showSelectedArticles(event) {
    var articleIds;

    event.preventDefault();
    articleIds = $(".select-article:checked").parent().children("a").map(function(){
        var webAddress = this.href;
        var indexOf = webAddress.lastIndexOf('/');
        return webAddress.substring(indexOf + 1);
    }).get();
    showArticlesByIds(articleIds)
    return false;
}

function updateArticle(event) {
    var articleItemIds;

    articleItemIds = [];
    $('.add-row').each(function(event, data) {
        articleItemIds.push(data.id.replace('add-row-', ''));
    });
    $(this).after('<input type="hidden" name="order" value="' + articleItemIds.join() + '">');
}

$(document).ready(function() {
    var articleItemLastId;

    if ($('.add-row').length > 0) {
        articleItemLastId = $('.add-row').last()[0].id;
        articleItemCount = Number(articleItemLastId.replace('add-row-', ''))
    } else {
        articleItemCount = 0;
    }

    // Start of code copied from https://www.brainbell.com/javascript/making-resizable-table-js.html
    // The code is used to create resizable tables.
    var tables = document.getElementsByTagName('table');
    for (var i=0; i<tables.length;i++){
     resizableGrid(tables[i]);
    }

    function resizableGrid(table) {
     var row = table.getElementsByTagName('tr')[0],
     cols = row ? row.children : undefined;
     if (!cols) return;

     table.style.overflow = 'hidden';

     var tableHeight = table.offsetHeight;

     for (var i=0;i<cols.length;i++){
      var div = createDiv(tableHeight);
      cols[i].appendChild(div);
      cols[i].style.position = 'relative';
      setListeners(div);
     }

     function setListeners(div){
      var pageX,curCol,nxtCol,curColWidth,nxtColWidth;

      div.addEventListener('mousedown', function (e) {
       curCol = e.target.parentElement;
       nxtCol = curCol.nextElementSibling;
       pageX = e.pageX;

       var padding = paddingDiff(curCol);

       curColWidth = curCol.offsetWidth - padding;
       if (nxtCol)
        nxtColWidth = nxtCol.offsetWidth - padding;
      });

      div.addEventListener('mouseover', function (e) {
       e.target.style.borderRight = '2px solid #0000ff';
      })

      div.addEventListener('mouseout', function (e) {
       e.target.style.borderRight = '';
      })

      document.addEventListener('mousemove', function (e) {
       if (curCol) {
        var diffX = e.pageX - pageX;

        if (nxtCol)
         nxtCol.style.width = (nxtColWidth - (diffX))+'px';

        curCol.style.width = (curColWidth + diffX)+'px';
       }
      });

      document.addEventListener('mouseup', function (e) {
       curCol = undefined;
       nxtCol = undefined;
       pageX = undefined;
       nxtColWidth = undefined;
       curColWidth = undefined
      });
     }

     function createDiv(height){
         var div = document.createElement('div');
         div.style.top = 0;
         div.style.right = 0;
         div.style.width = '5px';
         div.style.position = 'absolute';
         div.style.cursor = 'col-resize';
         div.style.userSelect = 'none';
         div.style.height = height + 'px';
         return div;
     }

     function paddingDiff(col){

          if (getStyleVal(col,'box-sizing') == 'border-box'){
           return 0;
          }

          var padLeft = getStyleVal(col,'padding-left');
          var padRight = getStyleVal(col,'padding-right');
          return (parseInt(padLeft) + parseInt(padRight));

         }

         function getStyleVal(elm,css){
          return (window.getComputedStyle(elm, null).getPropertyValue(css))
         }
    };
    // End of code copied from https://www.brainbell.com/javascript/making-resizable-table-js.html

    $('.add-first-row').click(addFirstArticleItem);
    $('.add-row').click(addArticleItem);
    $('.copy-rows').click(copyArticleItems);
    $('.cut-rows').click(cutArticleItems);
    $('.d-type').change(checkType);
    $('.move-row-up').click(moveArticleItemUp);
    $('.move-row-down').click(moveArticleItemDown);
    $('.move-moment-up').click(moveArticleItemMomentUp);
    $('.move-moment-down').click(moveArticleItemMomentDown);
    $('.paste-rows').click(pasteArticleItems);
    $('.remove-article').click(removeArticle);
    $('.remove-row').click(removeArticleItem);
    $('.reset-search-criteria-button').click(resetArticleSearchCriteria);
    $('.search-article-button').click(searchArticlesBySearchCriteria);
    $('.show-all-articles-button').click(showAllArticles);
    $('.show-selected-articles-button').click(showSelectedArticles);
    $(".ta-bort").click(removeLemma);

    function addArticleItem(event) {
        var articleItemPosition;

        event.preventDefault();
        articleItemPosition = event.currentTarget.id.replace('add-row-', '');
        articleItemCount++
        newArticleItemId = articleItemCount
        $('#data-' + articleItemPosition).after('<li id="data-' + newArticleItemId + '"><input type="text" size="3" name="type-' + newArticleItemId + '" id="type-' + newArticleItemId + '" class="d-type"><textarea rows="1" style="width: 55%" name="value-' + newArticleItemId + '" id="value-' + newArticleItemId + '" class="d-value" /><button class="add-row" id="add-row-' + newArticleItemId + '" tabindex="-1"><strong>+</strong></button><button class="remove-row" id="remove-row-' + newArticleItemId + '" tabindex="-1"><strong>-</strong></button><button class="move-row-up" id="row-up-' + newArticleItemId + '" tabindex="-1"><strong>↑</strong></button><button class="move-row-down" id="row-down-' + newArticleItemId + '" tabindex="-1"><strong>↓</strong></button><input type="checkbox" class="select-field" tabindex="-1" /></li>');
        $('#add-row-' + newArticleItemId).click(addArticleItem);
        $('#remove-row-' + newArticleItemId).click(removeArticleItem);
        $('#type-' + newArticleItemId).change(checkType);
        $('#value-' + newArticleItemId).change(checkValue);
        $('#value-' + newArticleItemId).keydown(hanteraTangent);
        $('#row-up-' + newArticleItemId).click(moveArticleItemUp);
        $('#row-down-' + newArticleItemId).click(moveArticleItemDown);
        $('#spara-och-ladda-om-' + newArticleItemId).click(updateArticle);
    }

    function addFirstArticleItem(event) {
        var articleItemPosition;

        event.preventDefault();
        articleItemCount++
        newArticleItemId = articleItemCount
        $('.lemma-list').prepend('<li id="data-' + newArticleItemId + '"><input type="text" size="3" name="type-' + newArticleItemId + '" id="type-' + newArticleItemId + '" class="d-type"><textarea rows="1" style="width: 55%" name="value-' + newArticleItemId + '" id="value-' + newArticleItemId + '" class="d-value" /><button class="add-row" id="add-row-' + newArticleItemId + '" tabindex="-1"><strong>+</strong></button><button class="remove-row" id="remove-row-' + newArticleItemId + '" tabindex="-1"><strong>-</strong></button><button class="move-row-up" id="row-up-' + newArticleItemId + '" tabindex="-1"><strong>↑</strong></button><button class="move-row-down" id="row-down-' + newArticleItemId + '" tabindex="-1"><strong>↓</strong></button><input type="checkbox" class="select-field" tabindex="-1" /></li>');
        $('#add-row-' + newArticleItemId).click(addArticleItem);
        $('#remove-row-' + newArticleItemId).click(removeArticleItem);
        $('#type-' + newArticleItemId).change(checkType);
        $('#value-' + newArticleItemId).change(checkValue);
        $('#value-' + newArticleItemId).keydown(hanteraTangent);
        $('#row-up-' + newArticleItemId).click(moveArticleItemUp);
        $('#row-down-' + newArticleItemId).click(moveArticleItemDown);
        $('#spara-och-ladda-om-' + newArticleItemId).click(updateArticle);
    }

    function copyArticleItems(event) {
        event.preventDefault();
        copySelectedArticleItems();
        $(".lemma-list input:checked").prop( "checked", false );
    }

    function cutArticleItems(event) {
        event.preventDefault();
        copySelectedArticleItems();
        $(".lemma-list input:checked").parent().remove();
    }

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
              $('#moment-up-' + radNummer).click(moveArticleItemMomentUp);
              $('#moment-down-' + radNummer).click(moveMomentDown);
            }
            $(this).removeClass("red");
        } else {
            $(this).addClass("red");
        }
    }

    function moveArticleItemMomentUp(event) {
        moveArticleItemMoment(event, 'up');
    }

    function moveArticleItemMomentDown(event) {
        moveArticleItemMoment(event, 'down');
    }

    function moveArticleItemMoment(event, dir) {
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
            if (!moment[0].id) {
                alert("Cannot flytta momentet upp, det är det första i artikeln.");
                return;
            }
        }

        // ids.unshift(moment[0].id);
        nextMoment = element.next();
        var i = 1;
        while (nextMoment.length > 0 && nextMoment[0].id && !isRightMomentType(nextMoment)) {
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
        if (dir == 'up'){
             ids.unshift(element[0].id);
        }
        else {
            ids.push(element[0].id);
            ids.unshift(nextMoment[0].id);
        }
        for (i in ids) {
            var id = ids[i];
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
        return $(row[0].id.replace(/^data-/, '#type-'))[0].value.trim().toUpperCase();
    }

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

    $('.spara-och-ladda-om').click(updateArticle);

    $('#sok-artikel').on('keyup', searchArticlesAutocomplete);

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
        var artUrl = window.location.href.replace(/\/talgoxe.*$/, '/talgoxe/get_article_html/');
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
        $(element).html("Förbereder&nbsp;PDF...");
        articles = collectArticles();
        url = printableEndpoint('pdf', articles);
        $.get(url).done(function(data) {
            $(element).off('click');
            $(element).attr("href", data.trim());
            $(element).attr("target", "_blank");
            $(element).html("Ladda&nbsp;ner&nbsp;PDF");
        });
    }

    function collectArticles() {
        articles = [];
        $('.träff').each(function(i, article) {
            articles.push(article.id.replace(/^lemma-/, ''));
        });

        return articles;
    }

    function printableEndpoint(format, articles) {
        return window.location.href.replace(/\/talgoxe.*/, '/talgoxe/get_file') + '/' + format + '?ids=' + new String(articles);
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

        name = $(event.currentTarget).attr("name").replace(/^select/, 'selected');
        var id = name.replace(/^selected-/, '');
        lemma = $($('[name="select-' + id + '"]').parent().children()[1]).html().trim();
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

    function removeLemma(event) {
        lemma = $(event.currentTarget).parent();
        var name = $(event.currentTarget).attr("name");
        if (name && name.match(/^selected-bokstav/)) {
            bokstav = name.replace(/^selected-bokstav-/, '');
            $('[name="selected-bokstav-' + bokstav + '"]').parent().remove();
            selector = '[name="bokstav-' + bokstav + '"]'
        } else  {
            var id = lemma.attr("id").replace(/^li-select-/, '');
            lemma.remove();
            $('[name="selected-' + id + '"]').remove();
            selector = '[name="select-' + id + '"]';
        }
        lemmaLeft = $(selector);
        lemmaLeft.click();
    }

    $("#selectalla").click(selectAll);

    function selectAll(event) {
        event.preventDefault();
        $('[style="display: list-item;"]').each(function(i, element) {
            if (!element.id.match(/^li-selected-/)) {
                var id = $(element).children().first().attr("name").replace(/^select-/, '')
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
        var text = element.value;
        textFöre = text.substring(0, element.selectionStart);
        var cursor = element.selectionStart;
        textEfter = text.substring(cursor, text.length);
        element.value = textFöre + tecken + textEfter;
        element.selectionStart = element.selectionEnd = cursor + 1;
    }

    function hanteraTangent(event) {
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
    }
});
