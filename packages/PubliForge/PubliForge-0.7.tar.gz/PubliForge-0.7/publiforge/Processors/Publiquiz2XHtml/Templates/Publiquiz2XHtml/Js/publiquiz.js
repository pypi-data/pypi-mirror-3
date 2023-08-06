/***************************************************************************
 **                             exercise.js
 ** ------------------------------------------------------------------------
 ** 2012, January
 ** Tien Hai NGUYEN <tienhai.nguyen@prismallia.fr>
 ** $Id: publiquiz.js cb4098c5a1f2 2012/08/29 07:52:40 tienhai $
 ** ------------------------------------------------------------------------
 ** Moteur Javascript pour les tests basé sur la librairie 'mootools'
 ** mootools-core : 1.4.2 
 ***************************************************************************/

/***************************************************************************
 **
 ** Copyright (C) Prismallia, Paris, 2012. All rights reserved.
 **
 ** This program is free software. You can redistribute it and/or modify
 ** it under the terms of the GNU General Public License version 2 as
 ** published by the Free Software Foundation.
 **
 ** This file is provided AS IS with NO WARRANTY OF ANY KIND, INCLUDING THE
 ** WARRANTY OF DESIGN, MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.
 **
 ***************************************************************************/


// =========================================================================
//                              Variable global
// =========================================================================
// -------------------------------------------------------------------------
//! \brief Variable global du score obtenu.
// -------------------------------------------------------------------------
score = 0;
// -------------------------------------------------------------------------
//! \brief Variable global du total de l'exercice.
// -------------------------------------------------------------------------
total = 0;
// -------------------------------------------------------------------------
//! \brief Variable de la position de souris.
// -------------------------------------------------------------------------
mouse_left = '';
// -------------------------------------------------------------------------
//! \brief Variable de la position de souris.
// -------------------------------------------------------------------------
mouse_top = '';
// -------------------------------------------------------------------------
//! \brief Variable pour l'aide.
//
//! Indiqe quelle aide est ouverte.
// -------------------------------------------------------------------------
current_exo_help_id = '';
// -------------------------------------------------------------------------
//! \brief Variable pour l'aide.
//
//! Indiqe si l'aide est ouverte.
// -------------------------------------------------------------------------
help_slides = new Hash({}); 
help_slides_ref = new Array(); 
help_open = false;

answer_slides = new Hash({}); 
answer_slides_ref = new Array(); 

// -------------------------------------------------------------------------
//! \brief Test du navigateur.
// -------------------------------------------------------------------------
ie = false;


// =========================================================================
//                                  Init
// =========================================================================
// -------------------------------------------------------------------------
//! \brief Init.
//
//! Mise en place des éléments, on cache les réponses, on vide les inputs,
//! on met les selections de type input 'radio'/'check' a vide, on met 
//! en place les events
// -------------------------------------------------------------------------
window.addEvent('domready', function(){
    //----------------------------------------------------------------------
    // Définition du navigateur
    //----------------------------------------------------------------------
    if(Browser.name == 'ie')
        ie = true;

    //----------------------------------------------------------------------
    // Configuration de l'exercice lors du chargement de la page
    //----------------------------------------------------------------------
    
    // On cache l'aide
    closeHelpCorpus();

    // On cache les propositions de réponse pour les exercices de production
    closeAnswerCorpus();

    // Exercice avec des input
    // On deselectionne tous les 'input' pour les exercice de type 
    // 'radio' et 'checkbox'
    // On vide tous les 'input' texte
    $$('input').each( function(elem){
        if(elem.type == 'radio' || elem.type == 'checkbox'){
            elem.set('checked', false);
            elem.disabled = false;
        }
        else if (elem.type == 'text'){
            elem.value = '';
            elem.disabled = false;
        }

    });

    // Exercice de type 'blank_select'
    configureExerciseBlankSelect();

    // Exercice de type 'blank_fill'
    configureExerciseBlankFill();

    // Exercice de type 'blank_fill'
    configureExerciseCategories();

    // Exercice de type 'point'
    //configureExercisePoint();

    //----------------------------------------------------------------------
    // Exercice Events
    //----------------------------------------------------------------------

    // Ajout de l'evenement 'click' sur les choix pour les exercices 
    // de type 'radio'
    $$('.choices-radio .pquizChoice').addEvent('click', function(e){
        var target = $(e.target);
        if (target.nodeName == 'input' || target.nodeName == 'INPUT')
            onRadio(target.parentNode);
        else
            onRadio(target);
    });

    // Ajout de l'evenement 'click' sur les choix pour les exercices
    // de type 'check'
    $$('.choices-check .pquizChoice').addEvent('click', function(e){
        var target = $(e.target);
        if (target.nodeName == 'input' || target.nodeName == 'INPUT')
            onCheck(target.parentNode);
        else
            onCheck(target);
    });

    // Ajout de l'evenement 'click' sur les choix pour les exercices 
    // de type 'point'
    $$('.point .pquizChoice').addEvent('click', function(e){
        var target = $(e.target);
        var tid = target.id;
        var exo_id = tid.substring(0, tid.length-3);
        if($(exo_id+'_engine').hasClass('radio'))
            onPointRadio(target);
        else
            onPointCheck(target);
    });

    // Ajout de l'evenement 'mousedown' sur les 'item' utiliser pour
    // les exercices de type 'blank_select'
    $$('.pquizItem').addEvent('mousedown', function(event){
        setDraggableItem(event, this);
    });

    // Ajout de l'evenement 'mousemove', permet d'ajuster les coordonnées de
    // l'item a déplacer lors d'un drag and drop.
    $(document.body).addEvent('mousemove',function(event){
        mouse_left = event.page.x;
        mouse_top = event.page.y;
    });

    // Ajout de l'evenement 'click' sur les groups pour les exercices
    // de categories
    $$('.categories .pquizCategory').addEvent('click', function(e){
        var target = $(e.target);
        var classList = target.className.clean().split(" ");
        if (! classList.contains('pquizCategory'))
           target = target.parentNode;
        onSelectCategory(target);
    });

    // Ajout de l'evenement 'click' sur les choix pour les exercices 
    // de type 'point'
    $$('.categories .pquizChoice').addEvent('click', function(e){
        var target = $(e.target);
        onSelectCategoryChoice(target);
    });

    //----------------------------------------------------------------------
    // Boutton Events
    //----------------------------------------------------------------------
    
    // Ajout de l'evenement 'click' sur le bouton 'help'
    $$('.pquizButton').addEvent('click', function(event){
        event.stop();
        var button_id = this.id;
        if (button_id.contains('_help-link'))
            onHelp('', this);
        if(button_id.contains('submit')){
            onValidate();
        }
    });

});

// -------------------------------------------------------------------------
//! \brief DEBUG Helper affiche les propriété d'un obj.
//! \param obj (Object) : l'objet à affiché
// -------------------------------------------------------------------------
function alertObj(obj){
    var str = '';
    for (prop in obj)
        if (prop.charAt(0)){
            str += prop + ' : ' + obj[prop];
            str += ',';
        }
    alert(str);
}

// -------------------------------------------------------------------------
//! \brief Helper méthode pour tirer aléatoirement une valeur borné.
//! \param min (int) : valeur mini
//! \param max (int) : valeur maxi
//! \return int : valeur
// -------------------------------------------------------------------------
function random(min, max)
{
    return Math.round(min + Math.random()*(max - min));
}


// =========================================================================
//                          Configure Form
//
//                      configureExerciseBlankSelect
//                      configureExerciseBlankFill
//                      configureExerciseCategories
//                      configureExercisePoint
// =========================================================================
// -------------------------------------------------------------------------
//! \brief Configuration des exercices de type blank_select
//
//! Permet de mélanger les 'item'.
// -------------------------------------------------------------------------
function configureExerciseBlankSelect(){
    $$('.pquizItems').each( function(elem){
        var is_shuffle = elem.hasClass('shuffle');
        var childs = elem.getElements('.pquizItem');
        if (! is_shuffle){
            childs.shuffle().each( function(el){
                el.inject(elem);
            });
        }
    });
}

// -------------------------------------------------------------------------
//! \brief Configuration des exercices de type blank_fill.
//
//! Permet de redimensionner les input a la taille de la réponse.
// -------------------------------------------------------------------------
function configureExerciseBlankFill(){
    if ($$('.blanks-fill .pquizChoice').length == 0)
        return;

    $$('.blanks-fill .pquizChoice').each(function(elem){
        if (elem.parentNode.nodeName == 'TD' || 
            elem.parentNode.parentNode.nodeName == 'TD')
                return;
        var key = elem.id.substring(elem.id.length - 2, elem.id.length);
        var exo_id = elem.id.substring(0, elem.id.length - 3);
        var answers = getCorrection($(exo_id+'_correct')); 
        var value = answers.get(key);
        
        var answer = '';
        value.split('|').each(function(txt){
            if (txt.length > answer.length )
                answer = txt;
        });
        
        var w = answer.length * 2;
        if(w < 20)
            w = 20;
        if(elem.getProperty('style') == null)
            elem.setStyle('width', w+'ex');
    });
}

// -------------------------------------------------------------------------
//! \brief Configuration des exercices de type categories
//
//! Permet de mettre une couleur pour chaque categorie.
// -------------------------------------------------------------------------
function configureExerciseCategories(){
    // Ajout des couleurs des catégories
    $$('.pquizCategories').each( function(elem){
        var childs = elem.getElements('.pquizCategory');
        childs[0].addClass('selected');
        var count = 1; 
        childs.each( function(el){
            var color = el.getElements('.pquizCategoryColor')[0];
            color.addClass('pquizCategoryColor_' + count)
            count ++;
        });
    });

    // Mélange des choix
    $$('.categories .pquizChoices').each( function(elem){
        var childs = elem.getElements('.pquizChoice');
        childs.shuffle().each( function(el){
            $(el.parentNode).inject(elem);
        });
    });
}

// -------------------------------------------------------------------------
//! \brief Configuration des exercices de type point.
//
//! Permet de redimensionner les réponse possible a une taille minimum.
// -------------------------------------------------------------------------
function configureExercisePoint(){
    var width_mini = 60;
    $$('.point .pquizChoice').each( function(elem){
        if(elem.getProperty('style') == null && 
                elem.clientWidth < width_mini){
            var p_left = elem.getStyle('padding-left').toInt() ;
            var p_right = elem.getStyle('padding-right').toInt() ;
            elem.setStyle('width', width_mini - p_left - p_right);
        }
    });
}

// =========================================================================
//                          Help Manage
//
//                          closeHelpCorpus
//                          closeAnswerCorpus
//                          onHelp
//                          updateHelp
// =========================================================================
// -------------------------------------------------------------------------
//! \brief Helper permet de fermer tous les aides.
// -------------------------------------------------------------------------
function closeHelpCorpus(){
    $$('.pquizEngine').each( function(elem) {
        var _id = elem.getAttribute('id');
        var exo_id = _id.substring(0, _id.length - 7);
        var help = $(exo_id+'_help-slot');
        var count = 0; 
        if (help){
            var slide = new Fx.Slide(help);
            help.setStyle('display', 'block');
            slide.hide();
            help_slides.set(count, help);
            help_slides_ref[count] = slide;
            count ++;
        }
    });
}

// -------------------------------------------------------------------------
//! \brief Helper permet de fermer tous les propositions de correction.
// -------------------------------------------------------------------------
function closeAnswerCorpus(){
    var count = 0;
    $$('.pquizAnswerText').each( function(elem) {
        var slide = new Fx.Slide(elem);
        elem.setStyle('display', 'block');
        slide.hide();
        answer_slides.set(count, elem);
        answer_slides_ref[count] = slide;
        count ++;

    });
}

// -------------------------------------------------------------------------
//! \brief Méthode pour afficher/faire disparaitre l'aide de l'exercice.
//
//! Par défaut le texte est vide et on charge l'aide depuis un 
//! fichier externe.
//! Il est nécessaire de surcharger cette méthode pour les supports
//! spécifique tel que les smartphones ou produit CD-Rom.
//! \param text (String) : le texte de l'aide
//! \param target (Object) : object qui a recu le click
// -------------------------------------------------------------------------
function onHelp(text, target){
    // Si il y a une aide ouverte on la ferme
    var help = $(current_exo_help_id + '_help-slot')
    if (help_open){
        help_open = false;
        help_slides_ref[help_slides.keyOf(help)].slideOut();
    }

    var exo_id = target.id.substring(0, target.id.length-10);
    var help_id = exo_id+'-hlp';

    if (current_exo_help_id == exo_id){
        current_exo_help_id = '';
        return;
    }

    current_exo_help_id = exo_id;
    help = $(current_exo_help_id + '_help-slot');
    help_slides_ref[help_slides.keyOf(help)].slideIn();
    help_open = true;
}


// =========================================================================
//                      Exercice 'categories'
//
//                         onSelectCategory
//                         onSelectCategoryChoice
// =========================================================================
// -------------------------------------------------------------------------
//! \brief Sélectionne une categorie pour un exercice de type 'categories'.
//! \param target (Object) : Object 'class=pquizCategories'
// -------------------------------------------------------------------------
function onSelectCategory(target){
    if (target.hasClass('selected'))
        return;
    var classList = target.className.clean().split(" ");
    var exo_id = classList[0];

    // On enleve la class 'selected' des autres categorie du même exercice
    $(exo_id+'_categories').getElements('.pquizCategory').removeClass('selected');

    target.addClass('selected');
}

// -------------------------------------------------------------------------
//! \brief Sélectionne un choix pour un exercice de type 'categories'.
//! \param target (Object) : Object 'class=pquizChoice'
// -------------------------------------------------------------------------
function onSelectCategoryChoice(target){
    //On enleve l'ancienne appartenance de categorie
    var classList = target.className.clean().split(" ");
    classList.each( function(cl){
        if (cl != 'pquizChoice')
            target.removeClass(cl);
    });

    // On place la categorie et la class couleur correspondante
    var tid = target.id;
    var exo_id = tid.substring(0, tid.length-3);
    $(exo_id+'_categories').getElements('.pquizCategory').each( function(elem){
        if (elem.hasClass('selected')){
            var color_category = elem.getElements('.pquizCategoryColor')[0]
            var classColorList = color_category.className.clean().split(" ");
            var classCategoryList = elem.className.clean().split(" ");
            var color = classColorList[1];
            var category = classCategoryList[2];
            target.addClass(color);
            target.addClass(category);
        }
    });
}


// =========================================================================
//                      Exercice 'check' et 'radio'
//
//                              onRadio
//                              onCheck
// =========================================================================
// -------------------------------------------------------------------------
//! \brief Sélectionne le choix pour un exercice de type 'radio'.
//! \param target (Object) : Object 'class=choice_radio'
// -------------------------------------------------------------------------
function onRadio(target){
    var tid = target.id;
    var exo_id = tid.substring(0, tid.length-3);
    $(exo_id+'_engine').getElements('.pquizChoice').removeClass('selected');
    target.addClass('selected');
    target.getChildren('input').set('checked', true);
}

// -------------------------------------------------------------------------
//! \brief Sélectionne le choix pour un exercice de type 'check'
//! \param target (Object) : Object 'class=choice_check'
// -------------------------------------------------------------------------
function onCheck(target){
    if (target.hasClass('selected')){
        target.removeClass('selected');
        target.getChildren('input').set('checked', false);
    }
    else{
        target.addClass('selected');
        target.getChildren('input').set('checked', true);
    }
}


// =========================================================================
//                      Exercice 'blank_select'
//
//                          setDraggableItem
//                          newDropClone
//                          cancelMoveItem
// =========================================================================
// -------------------------------------------------------------------------
//! \brief Permet le 'drag and drop' sur un item
//! \param event (Object) : Object 'event'
//! \param item (Object) : l'élément a drag and drop
// -------------------------------------------------------------------------
function setDraggableItem(event, item){
    event.stop();

    var classList = item.className.clean().split(" ");
    var is_multiple = $(classList[0]+'_engine').hasClass('multiple');

    var clone = newDropClone(item);

    var margin_top = 20;
    var margin_left = 10;
    clone.setStyle('left', mouse_left - margin_left);
    clone.setStyle('top', mouse_top - margin_top);
    var drag = new Drag.Move(clone,{

        droppables: $$('.pquizDrop'),

        onDrop: function(dragging, elem){
            if (elem != null) {
                var exo_id = classList[0];
                var elem_id = elem.id;
                var drop_exo_id = elem_id.substring(0, elem_id.length-3);
                
                // On a dropper dans un block d'un autre exercice
                if(exo_id != drop_exo_id){
                    dragging.destroy();
                    item.setStyle('opacity', '1');
                    item.removeAttribute('style');
                    return;
                }

                // Si le block a déjà un element, on enlève celui en place
                if(elem.childNodes[0].nodeType == 1){
                    cancelMoveItem(elem.firstChild);
                }
                
                // On récupere l'ancien emplacement de l'item
                var drop = false;
                if (item.parentNode.hasClass('pquizDrop') ) {
                    drop = item.parentNode;
                }

                // On place l'item dans le block
                if (ie)
                    elem.innerText = '';
                else
                    elem.textContent = '';

                if(is_multiple){
                    var item2 = item.clone();
                    item2.inject(item, 'before');
                    item2.setStyle('opacity', '1');
                    item2.removeAttribute('style');
                    item2.addEvent('mousedown', function(event){
                        setDraggableItem(event, item2);
                    });
                }

                item.inject(elem);
                elem.highlight('#7389AE', '#FFF');
                item.setStyle('opacity', '1');
                item.removeAttribute('style');
                item.addClass('pquizItem_dropped');

                // Si l'ancien emplacement etait une boite de drop
                if (drop){
                    if (ie)
                        drop.innerText = '.................';
                    else
                        drop.textContent = '.................';
                }

            }
            else{
                if (item.parentNode.hasClass('pquizDrop') ){
                    var items = $(classList[0] + '_items' );
                    var drop = item.parentNode;
                    if (is_multiple){
                        item.destroy();
                    }
                    else{
                        item.inject(items);
                        item.setStyle('opacity', '1');
                        item.removeAttribute('style');
                        item.removeClass('pquizItem_dropped');
                    }

                    if (ie)
                        drop.innerText = '.................';
                    else
                        drop.textContent = '.................';
                }
                else{
                    item.setStyle('opacity', '1');
                    item.removeAttribute('style');
                    item.removeClass('pquizItem_dropped');
                }
            }
            dragging.destroy();
        },

        onCancel: function(dragging){
            item.setStyle('opacity', '1');
            item.removeAttribute('style');
            dragging.destroy();
        },

        onEnter: function(dragging, elem){
            // On test si on entre dans un block d'un autre exercice
            var exo_id = classList[0];
            var elem_id = elem.id;
            var drop_exo_id = elem_id.substring(0, elem_id.length-3);
            if(exo_id == drop_exo_id){
                if (ie)
                    elem.setStyle('background-color', '#98B5C1');
                else
                    elem.tween('background-color', '#98B5C1');
            }
        },

        onLeave: function(dragging, elem){
            if (ie)
                elem.setStyle('background-color', '#FFF');
            else
                elem.tween('background-color', '#FFF');
        },

        onDrag: function(elem){
            elem.setStyle('left',mouse_left - margin_left);
            elem.setStyle('top',mouse_top - margin_top);
        }
    });
    drag.start(event);
}

// -------------------------------------------------------------------------
//! \brief Helper pour le drag and drop , creer un clone.
//! \param item (Object) : l'element droppable
//! \return clone (Object)
// -------------------------------------------------------------------------
function newDropClone(item){
    var classList = item.className.clean().split(" ");
    var clone = null;

    clone = item.clone();
    clone.inject(item.parentNode.parentNode);
    item.setStyle('opacity', '0.5');
    return clone;
}

// -------------------------------------------------------------------------
//! \brief Remet un item dans la liste des items a drag and drop
//! \param item (Object) : l'element a remettre
// -------------------------------------------------------------------------
function cancelMoveItem(item){
    var classList = item.className.clean().split(" ");
    var exo_id = classList[0];

    // Mode multiple
    var is_multiple = $(exo_id+'_engine').hasClass('multiple');
    if (is_multiple){
        item.destroy();
        return;
    }

    item.inject($(exo_id + '_items' ));
    item.setStyle('opacity', '1');
    item.removeAttribute('style');
    item.removeClass('pquizItem_dropped');
}


// =========================================================================
//                      Exercice 'point_radio'
//
//                          onPointRadio
// =========================================================================
// -------------------------------------------------------------------------
//! \brief Sélectionne le choix pour un exercice de type 'point_radio'
//! \param target (Object) : Object 'class=choice_point'
// -------------------------------------------------------------------------
function onPointRadio(target){
    var tid = target.id;
    var exo_id = tid.substring(0, tid.length-3);
    $(exo_id+'_engine').getElements('.pquizChoice').removeClass('selected');
    target.addClass('selected');
}

// -------------------------------------------------------------------------
//! \brief Sélectionne le choix pour un exercice de type 'point_check'
//! \param target (Object) : Object 'class=choice_point'
// -------------------------------------------------------------------------
function onPointCheck(target){
    if (target.hasClass('selected'))
        target.removeClass('selected');
    else
        target.addClass('selected');
}


// =========================================================================
//                      Validation de l'exercice
//
//                          onValidate
//                          getCorrection
//                          validateExerciseRadio
//                          validateExerciseCheck
//                          validateExerciceMatching
//                          validateExerciceBlankSelect
//                          validateExerciceBlankFill
//                          validateExercisePoint
//                          validateExercisePointRadio
//                          validateExercisePointCheck
//                          validateExerciseSort
//                          validateExerciseCategories
// =========================================================================
// -------------------------------------------------------------------------
//! \brief Méthode appeler pour valider un exercice
// -------------------------------------------------------------------------
function onValidate() {
    score = 0;
    total = 0;

    $$('.pquizEngine').each( function(elem) {
        var _id = elem.getAttribute('id');
        var exo_id = _id.substring(0, _id.length - 7);

        if (elem.hasClass('choices-radio'))
            validateExerciseRadio(exo_id, elem);
        if (elem.hasClass('choices-check'))
            validateExerciseCheck(exo_id, elem);
        if (elem.hasClass('matching'))
            validateExerciceMatching(exo_id, elem);
        if (elem.hasClass('blanks-select'))
            validateExerciceBlankSelect(exo_id, elem);
        if (elem.hasClass('blanks-fill'))
            validateExerciceBlankFill(exo_id, elem);
        if (elem.hasClass('point'))
            validateExercisePoint(exo_id, elem);
        if (elem.hasClass('sort'))
            validateExerciseSort(exo_id, elem);
        if (elem.hasClass('categories'))
            validateExerciseCategories(exo_id, elem);

    });
    
    onScore(score, total);
}

// -------------------------------------------------------------------------
//! \brief Helper permet de récupérer les réponses dans un dico
//! \param elem (Object) : l'element 'result'
//! \return: Hash
// -------------------------------------------------------------------------
function getCorrection(elem){
    var responses = new Hash({}); 
    if (!elem)
        return responses;
    var data;
    if (ie)
        data = elem.innerText;
    else
        data = elem.textContent;

    data.split('::').each(function(response) {
        var key = response.substring(0,2);
        var value = response.substring(2, response.length);
        responses.set(key, value);
    });

    return responses;
}

// -------------------------------------------------------------------------
//! \brief validation d'un exercice de type 'radio'
//! \param exercise_id (String) : id de l'exercice
//! \param engine (Object) : corps du test
// -------------------------------------------------------------------------
function validateExerciseRadio(exercise_id, engine){
    total ++;
    var responses = getCorrection(
            engine.getElementById(exercise_id+'_correct'));
    var key = responses.keyOf('x');
    if(engine.getElementById(exercise_id+'_'+key).hasClass('selected'))
        score ++;
}

// -------------------------------------------------------------------------
//! \brief validation d'un exercice de type 'check'
//! \param exercise_id (String) : id de l'exercice
//! \param engine (Object) : corps du test
// -------------------------------------------------------------------------
function validateExerciseCheck(exercise_id, engine){
    var exo_total = engine.getElements('.pquizChoice').length;
    total += exo_total;
    computeExerciseCheck(exercise_id, engine, exo_total);
}

// -------------------------------------------------------------------------
//! \brief validation d'un exercice de type 'matching'
//! \param exercise_id (String) : id de l'exercice
//! \param engine (Object) : corps du test
// -------------------------------------------------------------------------
function validateExerciceMatching(exercise_id, engine){
    total += engine.getElements('.pquizDrop').length;
    var responses = getCorrection(
        engine.getElementById(exercise_id+'_correct'));
    responses.each(function(value, key){
        var container = engine.getElementById(exercise_id+'_'+key);
        if(container.childNodes[0].nodeType == 1){
            var item = container.firstChild;
    	    var classList = item.className.clean().split(" ");
            var item_value = classList[2].replace("item","");
            if (item_value == value)
                score ++;
        }
    });
}

// -------------------------------------------------------------------------
//! \brief validation d'un exercice de type 'blanks-select'
//! \param exercise_id (String) : id de l'exercice
//! \param engine (Object) : corps du test
// -------------------------------------------------------------------------
function validateExerciceBlankSelect(exercise_id, engine){
    total += engine.getElements('.pquizDrop').length;
    var responses = getCorrection(
            engine.getElementById(exercise_id+'_correct')); 
    responses.each(function(value, key){
        var container = engine.getElementById(exercise_id+'_'+key);
        var data;
        if (ie)
            data = container.firstChild.innerText;
        else
            data = container.firstChild.textContent;
        if (container.childNodes[0].nodeType == 1 && data == value){
            score ++;
        }
    });
}

// -------------------------------------------------------------------------
//! \brief validation d'un exercice de type 'blanks-fill'
//! \param exercise_id (String) : id de l'exercice
//! \param engine (Object) : corps du test
// -------------------------------------------------------------------------
function validateExerciceBlankFill(exercise_id, engine){
    total += engine.getElements('.pquizChoice').length;
    var is_strict = engine.hasClass('strict');
    var responses = getCorrection(
            engine.getElementById(exercise_id+'_correct'));
    responses.each(function(value, key){
        var container = engine.getElementById(exercise_id+'_'+key);
        var result = container.value.clean();
        if(!is_strict){
            result = result.toLowerCase();
            result = result.replace(/[\.,-\/#!?$%\^&\*;:{}=\-_`~()]/g," ");
            result = result.replace(/\s{2,}/g," ");
            result = result.clean();
        }
        //alert("'" + result + "'");
        
        var answer = [];
        value.split('|').each(function(txt){
            if(!is_strict)
            {
                txt = txt.toLowerCase();
                txt = txt.replace(/[\.,-\/#!?$%\^&\*;:{}=\-_`~()]/g," ");
                txt = txt.replace(/\s{2,}/g," ");
                txt = txt.clean();
            }
            answer.include(txt);
        });
        
        if (answer.contains(result))
            score ++;
    });
}

// -------------------------------------------------------------------------
//! \brief validation d'un exercice de type 'point'
//! \param exercise_id (String) : id de l'exercice
//! \param engine (Object) : corps du test
// -------------------------------------------------------------------------
function validateExercisePoint(exercise_id, engine){
    if (engine.hasClass('radio'))
        validateExercisePointRadio(exercise_id, engine);
    else
        validateExercisePointCheck(exercise_id, engine);
}

// -------------------------------------------------------------------------
//! \brief validation d'un exercice de type point 'radio'
//! \param exercise_id (String) : id de l'exercice
//! \param engine (Object) : corps du test
// -------------------------------------------------------------------------
function validateExercisePointRadio(exercise_id, engine){
    total ++;
    var responses = getCorrection(
        engine.getElementById(exercise_id+'_correct'));
    var key = responses.keyOf('x');
    if(engine.getElementById(exercise_id+'_'+key).hasClass('selected'))
        score ++;
}

// -------------------------------------------------------------------------
//! \brief validation d'un exercice de type 'point_check'.
//! \param exercise_id (String) : id de l'exercice
//! \param engine (Object) : corps du test
// -------------------------------------------------------------------------
function validateExercisePointCheck(exercise_id, engine){
    var exo_total = engine.getElements('.pquizChoice').length;
    total += exo_total;
    computeExerciseCheck(exercise_id, engine, exo_total);
}

// -------------------------------------------------------------------------
//! \brief validation d'un exercice de type 'sort'.
//! \param exercise_id (String) : id de l'exercice
//! \param engine (Object) : corps du test
// -------------------------------------------------------------------------
function validateExerciseSort(exercise_id, engine){
    total ++;
    var responses = getCorrection(
            engine.getElementById(exercise_id+'_correct'));
    var is_correct = true;
    responses.each(function(value, key){
        var container = engine.getElementById(exercise_id+'_'+key);
        var data;
        if (ie)
            data = container.firstChild.innerText;
        else
            data = container.firstChild.textContent;
        if (container.childNodes[0].nodeType != 1 || data != value ){
            is_correct = false;
            return; 
        }
    });

    if (is_correct)
        score ++;
}

// -------------------------------------------------------------------------
//! \brief validation d'un exercice de type 'sort'.
//! \param exercise_id (String) : id de l'exercice
//! \param engine (Object) : corps du test
// -------------------------------------------------------------------------
function validateExerciseCategories(exercise_id, engine){
    var exo_total = engine.getElements('.pquizChoice').length;
    total += exo_total;

    var responses = getCorrection(
            engine.getElementById(exercise_id+'_correct'));

    // On compte les points
    responses.each(function(value, key){
        var container = engine.getElementById(exercise_id+'_'+key);
        var classList = container.className.clean().split(" ");
        if (classList.length == 3){
            var grp_id = classList[2].substring(
                classList[2].length -2, classList[2].length);
            
            if (value == grp_id)
                score ++;
        }
    });
}

// -------------------------------------------------------------------------
//! \brief Helper pour le calcul des scores des exercices de type check.
//
//! Le score se calcule par rapport au poids de la réponse, la réponse
//! fausse vaut toujours '-1' point.
//! \param exo_id (String) : id de l'exercice
//! \param engine (Object) : corps du test
//! \param exo_total (Int) : total de point de l'exercice
// -------------------------------------------------------------------------
function computeExerciseCheck(exo_id, engine, exo_total){
    var exo_score = 0;
    var responses = getCorrection(engine.getElementById(exo_id+'_correct')); 
    
    // On compte les reponses corrects
    var correct = responses.getLength();

    // On determine le poids d'une reponse correcte
    var weight_correct = exo_total / correct;

    engine.getElements('.pquizChoice').each( function(elem){
        var id = elem.id;
        var key = id.substring(id.length-2, id.length);
        if(elem.hasClass('selected') && responses.has(key))
            exo_score += weight_correct;
        else if (elem.hasClass('selected') && !responses.has(key))
            exo_score -= 1;
    });
    
    exo_score = exo_score.round();
    
    if (exo_score < 0)
        exo_score = 0;
    score += exo_score;
}


// =========================================================================
//                              Score
//
//                          onScore
//                          writeAnswer
//                          constructUserAnswers
//                          getAnswerSelected
//                          getAnswerExerciseRadio
//                          getAnswerExerciseCheck
//                          getAnswerExerciseBlankSelect
//                          getAnswerExerciseBlankFill
//                          getAnswerExercisePoint
//                          getAnswerExerciseSort
//                          getAnswerExerciseCategories
// =========================================================================
// -------------------------------------------------------------------------
//! \brief Méthode pour obtenir le score de l'exercice.
//
//! Il est nécessaire de surcharger cette méthode pour les supports
//! spécifique tel que les smartphones ou produit CD-Rom.
//! \param score (int) : score obtenu
//! \param total (int) : total possible de l'exercice
// -------------------------------------------------------------------------
function onScore(score, total){
    // Production ?
    $$('.pquizAnswerText').each( function(elem) {
        answer_slides_ref[answer_slides.keyOf(elem)].slideIn();
    });

    // On récupère les reponses du joueur
    var user_answer = constructUserAnswers();

    // On cache le bouton submit
    if ($('submit'))
        $('submit').setStyle('display', 'none');

    // On enleve les events
    $$('.pquizEngine').each( function(engine) {
        var _id = engine.getAttribute('id');
        var exo_id = _id.substring(0, _id.length - 7);

        if (engine.hasClass('choices-radio')){
            engine.getElements('.pquizChoice').each(function(el){
                el.removeEvents('click');
                el.removeClass('selected');
            });
        }
        if (engine.hasClass('blanks-select') || 
                engine.hasClass('matching') || 
                engine.hasClass('sort') ){
            engine.getElements('.pquizItem').removeEvents('mousedown');
        }
        if (engine.hasClass('blanks-fill')){
            engine.getElements('.pquizChoice').each(function(el){
                el.disabled = true;
                el.addClass('disabled');
            });
        }
        if (engine.hasClass('point')){
            engine.getElements('.pquizChoice').each(function(el){
                el.removeEvents('click');
                el.removeClass('selected');
            });
        }
        if (engine.hasClass('categories')){
            engine.getElements('.pquizCategory').each(function(el){
                el.removeEvents('click');
                el.removeClass('selected');
            });
            engine.getElements('.pquizChoice').each(function(el){
                el.removeEvents('click');
                var classList = el.className.clean().split(" ");
                classList.each( function(cl){
                    if (cl != 'pquizChoice')
                        el.removeClass(cl);
                });
            });
        }
    });

    // On affiche la correction
    onCorrection();

    // On affiche le score
    var elem = new Element('div', { 
        'text': 'score:' + score + '/' + total
        });
    elem.setStyle('text-align', 'center');
    elem.inject($('submit'), 'before');
}

// -------------------------------------------------------------------------
//! \brief Méthode pour ajouter dans le DOM la réponse du joueur.
//
//! Il est nécessaire de surcharger cette méthode pour les supports
//! spécifique tel que les smartphones ou produit CD-Rom pour ne pas écrire
//! la réponse dans le DOM.
//! \param exo_id (String) : id de l'exercice
//! \param engine (Object) : corps du test
//! \param answer (string) : réponses du joueur.
// -------------------------------------------------------------------------
function writeAnswer(exo_id, engine, answer){
    var result = engine.getElementById(exo_id+'_correct');
    var elem =  engine.getElementById(exo_id+'_user');
    if (elem == null){
        elem = new Element('div', { html: answer });
        elem.id = exo_id+'_user';
        elem.addClass('hidden');
        elem.inject(result, 'after');
        return;
    }
    if (ie)
        elem.innerText = answer;
    else
        elem.textContent = answer;
}

// -------------------------------------------------------------------------
//! \brief Méthode pour construire la chaine des réponses du joueur.
//! \return result (string) : réponses du joueur.
// -------------------------------------------------------------------------
function constructUserAnswers(){
    var result = '';
    
    var prod = $$('.pquizProduction')[0];
    if(prod){
        return prod.value.replace(/\n/g, '#R#');
    }
    
    $$('.pquizEngine').each( function(engine) {
        var _id = engine.getAttribute('id');
        var exo_id = _id.substring(0, _id.length - 7);
        var r = '';

        if (engine.hasClass('choices-radio'))
            r = getAnswerExerciseRadio(exo_id, engine);
        if (engine.hasClass('choices-check'))
            r = getAnswerExerciseCheck(exo_id, engine);
        if (engine.hasClass('matching'))
            r = getAnswerExerciseMatching(exo_id, engine);
        if (engine.hasClass('blanks-select'))
            r = getAnswerExerciseBlankSelect(exo_id, engine);
        if (engine.hasClass('blanks-fill'))
            r = getAnswerExerciseBlankFill(exo_id, engine);
        if (engine.hasClass('point'))
            r = getAnswerExercisePoint(exo_id, engine);
        if (engine.hasClass('sort'))
            r = getAnswerExerciseSort(exo_id, engine);
        if (engine.hasClass('categories'))
            r = getAnswerExerciseCategories(exo_id, engine);
        
        if (r != '' && result == '')
            result = r;
        else if (r != '' && result != '')
            result += '##' + r;
    });
    
    return result;
}

// -------------------------------------------------------------------------
//! \brief Helper construit la chaine 'reponse' à base d'élément 'selected'.
//! \param exo_id (String) : id de l'exercice
//! \param engine (Object) : corps du test
//! \return result (string) : réponses du joueur.
// -------------------------------------------------------------------------
function getAnswerSelected(exo_id, engine){
    var result = '';
    var selected = engine.getElements('.selected');
    selected.each( function(elem){
        var id = elem.id;
        if (result != '')
            result += '::';
        result += id.substring(id.length -2, id.length) + 'x';
    });
    writeAnswer(exo_id, engine, result);
    if (result != '')
        result = exo_id + '||' + result;        
    return result;
}

// -------------------------------------------------------------------------
//! \brief Récupère les réponses d'un exercice de type 'choices-radio'.
//! \param exo_id (String) : id de l'exercice
//! \param engine (Object) : corps du test
//! \return result (string) : réponses du joueur.
// -------------------------------------------------------------------------
function getAnswerExerciseRadio(exo_id, engine){
    return getAnswerSelected(exo_id, engine);
}

// -------------------------------------------------------------------------
//! \brief Récupère les réponses d'un exercice de type 'choices-check'.
//! \param exo_id (String) : id de l'exercice
//! \param engine (Object) : corps du test
//! \return result (string) : réponses du joueur.
// -------------------------------------------------------------------------
function getAnswerExerciseCheck(exo_id, engine){
    return getAnswerSelected(exo_id, engine);
}

// -------------------------------------------------------------------------
//! \brief Récupère les réponses d'un exercice de type 'matching'.
//! \param exo_id (String) : id de l'exercice
//! \param engine (Object) : corps du test
//! \return result (string) : réponses du joueur.
// -------------------------------------------------------------------------
function getAnswerExerciseMatching(exo_id, engine){
    var result = '';
    var choices = engine.getElements('.pquizDrop');
    choices.each( function(container){
        if (container.childNodes[0].nodeType == 1){
            var id = container.id;
	        var classList = container.firstChild.className.clean().split(" "); 
            var value = classList[2].replace('item','');
            if (result != '')
                result += '::';
            result += id.substring(id.length -2, id.length) + value;
        }
    });
    writeAnswer(exo_id, engine, result);

    // On garde une référence aux valeurs des items  
    var items_values = '';
    engine.getElements('.pquizItem').each(function(elem){
        var value;
        if (ie)
            value = elem.innerText;
        else
            value = elem.textContent;
	    var classList = elem.className.clean().split(" ");
        var key = classList[2].replace('item', '');
        if (items_values != '')
            items_values += '::';
        items_values += key + value;
    });
    
    var correct = engine.getElementById(exo_id+'_correct');
    var elem =  engine.getElementById(exo_id+'_items_values');
    if (elem == null){
        elem = new Element('div', { html: items_values });
        elem.id = exo_id+'_items_values';
        elem.addClass('hidden');
        elem.inject(correct, 'after');
    }
    else
    {
        if (ie)
            elem.innerText = items_values;
        else
            elem.textContent = items_values;
    }
    
    if (result != '')
        result = exo_id + '||' + result;
    return result;
}

// -------------------------------------------------------------------------
//! \brief Récupère les réponses d'un exercice de type 'blanks-select'.
//! \param exo_id (String) : id de l'exercice
//! \param engine (Object) : corps du test
//! \return result (string) : réponses du joueur.
// -------------------------------------------------------------------------
function getAnswerExerciseBlankSelect(exo_id, engine){
    var result = '';
    var choices = engine.getElements('.pquizDrop');
    choices.each( function(container){
        if (container.childNodes[0].nodeType == 1){
            var id = container.id;
            var value;
            if (ie)
                value = container.firstChild.innerText;
            else
                value = container.firstChild.textContent;
            if (result != '')
                result += '::';
            result += id.substring(id.length -2, id.length) + value;
        }
    });
    writeAnswer(exo_id, engine, result);
    if (result != '')
        result = exo_id + '||' + result;
    return result;
}

// -------------------------------------------------------------------------
//! \brief Récupère les réponses d'un exercice de type 'blanks-fill'.
//! \param exo_id (String) : id de l'exercice
//! \param engine (Object) : corps du test
//! \return result (string) : réponses du joueur.
// -------------------------------------------------------------------------
function getAnswerExerciseBlankFill(exo_id, engine){
    var result = '';
    var choices = engine.getElements('.pquizChoice');
    choices.each( function(container){
        var id = container.id;
        var value = container.value.clean();
        if (value != ''){
            if (result != '')
                result += '::';
            result += id.substring(id.length -2, id.length) + value;
        }
    });
    writeAnswer(exo_id, engine, result);
    if (result != '')
        result = exo_id + '||' + result;
    return result;
}

// -------------------------------------------------------------------------
//! \brief Récupère les réponses d'un exercice de type 'point'.
//! \param exo_id (String) : id de l'exercice
//! \param engine (Object) : corps du test
//! \return result (string) : réponses du joueur.
// -------------------------------------------------------------------------
function getAnswerExercisePoint(exo_id, engine){
    return getAnswerSelected(exo_id, engine);
}

// -------------------------------------------------------------------------
//! \brief Récupère les réponses d'un exercice de type 'blanks-fill'.
//! \param exo_id (String) : id de l'exercice
//! \param engine (Object) : corps du test
//! \return result (string) : réponses du joueur.
// -------------------------------------------------------------------------
function getAnswerExerciseSort(exo_id, engine){
    var result = '';
    var choices = engine.getElements('.pquizDrop');
    choices.each( function(container){
        if (container.childNodes[0].nodeType == 1){
            var id = container.id;
            var value;
            if (ie)
                value = container.firstChild.innerText;
            else
                value = container.firstChild.textContent;
            if (value != ''){
                if (result != '')
                    result += '::';
                result += id.substring(id.length -2, id.length) + value;
            }
        }
    });
    writeAnswer(exo_id, engine, result);
    if (result != '')
        result = exo_id + '||' + result;
    return result;
}

// -------------------------------------------------------------------------
//! \brief Récupère les réponses d'un exercice de type 'categories'.
//! \param exo_id (String) : id de l'exercice
//! \param engine (Object) : corps du test
//! \return result (string) : réponses du joueur.
// -------------------------------------------------------------------------
function getAnswerExerciseCategories(exo_id, engine){
    var result = '';
    var choices = engine.getElements('.pquizChoice');
    choices.each( function(choice){
        var id = choice.id;
        var classList =choice.className.clean().split(" ");
        if (classList.length == 3){
            var grp_id = classList[2].substring(
                classList[2].length -2, classList[2].length);
             
            if (result != '')
                result += '::';
            result += id.substring(id.length -2, id.length) + grp_id;
        }
    });

    writeAnswer(exo_id, engine, result);
    if (result != '')
        result = exo_id + '||' + result;
    return result;
}


// =========================================================================
//                              Correction
//
//                          onCorrection
//                          onUserAnswer
//                          displayCorrectAnswer
//                          displayUserAnswer
//                          displayAnswerExerciseBlankSelect
//                          displayUserAnswerExerciseBlankSelect
//                          displayAnswerExerciseBlankFill
//                          displayUserAnswerExerciseBlankFill
//                          displayAnswerExercisePoint
//                          displayUserAnswerExercisePoint
//                          displayAnswerExerciseRadio
//                          displayUserAnswerExerciseRadio
//                          displayAnswerExerciseCategories
//                          displayUserAnswerExerciseCategories
// =========================================================================
// -------------------------------------------------------------------------
//! \brief Méthode pour afficher la correction.
// -------------------------------------------------------------------------
function onCorrection(){
    // On supprime le bouton UserAnswer
    if($('pquizCorrection'))
        $('pquizCorrection').destroy();

    // On ajoute le bouton bascule vers les reponse de l'user
    if ($('submit')){
        var elem = new Element('a', { 
            'class': 'pquizButton',
            'text': 'Réponses',
            'id': 'pquizUserAnswer'});
        elem.inject($('submit'), 'after');
        
        $('pquizUserAnswer').addEvent('click', function(event){
            onUserAnswer();
        });
    }

    displayCorrectAnswer();
}

// -------------------------------------------------------------------------
//! \brief Méthode pour afficher les réponses du joueur.
// -------------------------------------------------------------------------
function onUserAnswer(){
    // On supprime le bouton UserAnswer
    if($('pquizUserAnswer'))
        $('pquizUserAnswer').destroy();

    // On ajoute le bouton bascule vers la correction
    if ($('submit')){
        var elem = new Element('a', { 
            'class': 'pquizButton',
            'text': 'Correction',
            'id': 'pquizCorrection'});
        elem.inject($('submit'), 'after');
                
        $('pquizCorrection').addEvent('click', function(event){
            onCorrection();
        });
    }

   displayUserAnswer();
}

// -------------------------------------------------------------------------
//! \brief Helper parcour les engines pour afficher la correction.
// -------------------------------------------------------------------------
function displayCorrectAnswer(){
    $$('.pquizEngine').each( function(engine) {
        var _id = engine.getAttribute('id');
        var exo_id = _id.substring(0, _id.length - 7);

        if (engine.hasClass('choices-radio') || engine.hasClass('choices-check'))
            displayAnswerExerciseRadio(exo_id, engine);
        if (engine.hasClass('matching'))
            displayAnswerExerciseMatching(exo_id, engine);
        if (engine.hasClass('blanks-select') || 
                engine.hasClass('sort') )
            displayAnswerExerciseBlankSelect(exo_id, engine);
        if (engine.hasClass('blanks-fill'))
            displayAnswerExerciseBlankFill(exo_id, engine);
        if (engine.hasClass('point'))
            displayAnswerExercisePoint(exo_id, engine);
        if (engine.hasClass('categories'))
            displayAnswerExerciseCategories(exo_id, engine);
    });
}

// -------------------------------------------------------------------------
//! \brief Helper parcour les engines pour afficher les réponses du joueur.
// -------------------------------------------------------------------------
function displayUserAnswer(){
    $$('.pquizEngine').each( function(engine) {
        var _id = engine.getAttribute('id');
        var exo_id = _id.substring(0, _id.length - 7);

        if (engine.hasClass('choices-radio') || engine.hasClass('choices-check'))
            displayUserAnswerExerciseRadio(exo_id, engine);
        if (engine.hasClass('matching'))
            displayUserAnswerExerciseMatching(exo_id, engine);
        if (engine.hasClass('blanks-select') || 
                engine.hasClass('sort') )
            displayUserAnswerExerciseBlankSelect(exo_id, engine);
        if (engine.hasClass('blanks-fill'))
            displayUserAnswerExerciseBlankFill(exo_id, engine);
        if (engine.hasClass('point'))
            displayUserAnswerExercisePoint(exo_id, engine);
        if (engine.hasClass('categories'))
            displayUserAnswerExerciseCategories(exo_id, engine);
    });
}

// -------------------------------------------------------------------------
//! \brief Affiche la correction d'un exercice de type 'matching'.
//
//! \param exo_id (String) : id de l'exercice
//! \param engine (Object) : corps du test
// -------------------------------------------------------------------------
function displayAnswerExerciseMatching(exo_id, engine){
    // On cache les items
    engine.getElements('.pquizItem').addClass('hidden');

    // On place la correction
    var answers = getCorrection(
            engine.getElementById(exo_id+'_correct'));
    var items_values = getCorrection(
            engine.getElementById(exo_id+'_items_values'));
    answers.each(function(value, key){
        var container = engine.getElementById(exo_id+'_'+key);
        if (container){
            if (ie)
                container.innerText = items_values.get(value);
            else
                container.textContent = items_values.get(value);
            container.addClass('mode_answer');
        }
    });
}

// -------------------------------------------------------------------------
//! \brief Affiche la correction d'un exercice de type 'blanks-select'.
//
//! \param exo_id (String) : id de l'exercice
//! \param engine (Object) : corps du test
// -------------------------------------------------------------------------
function displayAnswerExerciseBlankSelect(exo_id, engine){
    // On cache les items
    engine.getElements('.pquizItem').addClass('hidden');

    // On place la correction
    var answers = getCorrection(
            engine.getElementById(exo_id+'_correct'));
    answers.each(function(value, key){
        var container = engine.getElementById(exo_id+'_'+key);
        if (container){
            if (ie)
                container.innerText = value;
            else
                container.textContent = value;
            container.addClass('mode_answer');
        }
    });
}

// -------------------------------------------------------------------------
//! \brief Affiche les réponses d'un exercice de type 'matching'.
//
//! \param exo_id (String) : id de l'exercice
//! \param engine (Object) : corps du test
// -------------------------------------------------------------------------
function displayUserAnswerExerciseMatching(exo_id, engine){
    // On affiche les items
    engine.getElements('.pquizItem').removeClass('hidden');

    // On enleve la correction
    var answers = getCorrection(
            engine.getElementById(exo_id+'_correct'));
    answers.each(function(value, key){
        var container = engine.getElementById(exo_id+'_'+key);
        if (container){
            if (ie)
                container.innerText = '.................';
            else
                container.textContent = '.................';
            container.removeClass('mode_answer');
        }
    });

    // On place les réponses de l'user
    var answers = getCorrection(
            engine.getElementById(exo_id+'_user'));
    var items_values = getCorrection(
            engine.getElementById(exo_id+'_items_values'));
    answers.each(function(value, key){
        var container = engine.getElementById(exo_id+'_'+key);
        if(container){
            if (ie)
                container.innerText = items_values.get(value);
            else
                container.textContent = items_values.get(value);
        }
    });
}

// -------------------------------------------------------------------------
//! \brief Affiche les réponses d'un exercice de type 'blanks-select'.
//
//! \param exo_id (String) : id de l'exercice
//! \param engine (Object) : corps du test
// -------------------------------------------------------------------------
function displayUserAnswerExerciseBlankSelect(exo_id, engine){
    // On affiche les items
    engine.getElements('.pquizItem').removeClass('hidden');

    // On enleve la correction
    var answers = getCorrection(
            engine.getElementById(exo_id+'_correct'));
    answers.each(function(value, key){
        var container = engine.getElementById(exo_id+'_'+key);
        if (container){
            if (ie)
                container.innerText = '.................';
            else
                container.textContent = '.................';
            container.removeClass('mode_answer');
        }
    });

    // On place les réponses de l'user
    var answers = getCorrection(
            engine.getElementById(exo_id+'_user'));
    answers.each(function(value, key){
        var container = engine.getElementById(exo_id+'_'+key);
        if(container){
            if (ie)
                container.innerText = value;
            else
                container.textContent = value;
        }
    });
}

// -------------------------------------------------------------------------
//! \brief Affiche la correction d'un exercice de type 'blanks-fill'.
//
//! \param exo_id (String) : id de l'exercice
//! \param engine (Object) : corps du test
// -------------------------------------------------------------------------
function displayAnswerExerciseBlankFill(exo_id, engine){
    var answers = getCorrection(
            engine.getElementById(exo_id+'_correct'));
    answers.each(function(value, key){
        var container = engine.getElementById(exo_id+'_'+key);
        if (container){
            container.value = value;
            container.addClass('mode_answer');
        }
    });
}

// -------------------------------------------------------------------------
//! \brief Affiche les réponses d'un exercice de type 'blanks-fill'.
//
//! \param exo_id (String) : id de l'exercice
//! \param engine (Object) : corps du test
// -------------------------------------------------------------------------
function displayUserAnswerExerciseBlankFill(exo_id, engine){
    var answers = getCorrection(
            engine.getElementById(exo_id+'_correct'));
    answers.each(function(value, key){
        var container = engine.getElementById(exo_id+'_'+key);
        if (container){
            container.value = '';
            container.removeClass('mode_answer');
        }
    });

    var answers = getCorrection(
            engine.getElementById(exo_id+'_user'));
    answers.each(function(value, key){
        var container = engine.getElementById(exo_id+'_'+key);
        if(container)
            container.value = value;
    });
}

// -------------------------------------------------------------------------
//! \brief Affiche la correction d'un exercice de type 'point'.
//
//! \param exo_id (String) : id de l'exercice
//! \param engine (Object) : corps du test
// -------------------------------------------------------------------------
function displayAnswerExercisePoint(exo_id, engine){
    // On enleve les réponses du joueur
    var answers = getCorrection(
            engine.getElementById(exo_id+'_user'));
    
    answers.each(function(value, key){
        var container = engine.getElementById(exo_id+'_'+key);
        if (container)
            container.removeClass('selected');
    });    

    var answers = getCorrection(
            engine.getElementById(exo_id+'_correct'));
    answers.each(function(value, key){
        var container = engine.getElementById(exo_id+'_'+key);
        if (container){
            container.addClass('selected');
            container.addClass('mode_answer');
        }
    });
}

// -------------------------------------------------------------------------
//! \brief Affiche les réponses d'un exercice de type 'point'.
//
//! \param exo_id (String) : id de l'exercice
//! \param engine (Object) : corps du test
// -------------------------------------------------------------------------
function displayUserAnswerExercisePoint(exo_id, engine){
    // On enleve les correction
    var answers = getCorrection(
            engine.getElementById(exo_id+'_correct'));
    answers.each(function(value, key){
        var container = engine.getElementById(exo_id+'_'+key);
        if (container){
            container.removeClass('selected');
            container.removeClass('mode_answer');
        }
    });

    var answers = getCorrection(
            engine.getElementById(exo_id+'_user'));
    answers.each(function(value, key){
        var container = engine.getElementById(exo_id+'_'+key);
        if (container)
            container.addClass('selected');
    });
}

// -------------------------------------------------------------------------
//! \brief Affiche la correction d'un exercice de type 'choices-radio'.
//
//! \param exo_id (String) : id de l'exercice
//! \param engine (Object) : corps du test
// -------------------------------------------------------------------------
function displayAnswerExerciseRadio(exo_id, engine){
    engine.getElements('.pquizChoice input').each(function(el){
        el.disabled = true;
        el.set('checked', false);
    });

    engine.getElements('.pquizChoice').removeClass('selected');

    var answers = getCorrection(
            engine.getElementById(exo_id+'_correct'));
    answers.each(function(value, key){
        var container = engine.getElementById(exo_id+'_'+key);
        if (container){
            container.addClass('selected');
            container.addClass('mode_answer');

            container.getElements('input').each(function(i){
                i.set('checked', true);
            });
        }
    });
}

// -------------------------------------------------------------------------
//! \brief Affiche les réponses d'un exercice de type 'choices-radio'.
//
//! \param exo_id (String) : id de l'exercice
//! \param engine (Object) : corps du test
// -------------------------------------------------------------------------
function displayUserAnswerExerciseRadio(exo_id, engine){
    engine.getElements('.pquizChoice input').each(function(el){
        el.disabled = true;
        el.set('checked', false);
    });

    engine.getElements('.pquizChoice').removeClass('selected');
    engine.getElements('.pquizChoice').removeClass('mode_answer');

    var answers = getCorrection(
            engine.getElementById(exo_id+'_user'));
    answers.each(function(value, key){
        var container = engine.getElementById(exo_id+'_'+key);
        if (container)
        {
            container.addClass('selected');
            container.getElements('input').each(function(i){
                i.set('checked', true);
            });
        }
    });
}

// -------------------------------------------------------------------------
//! \brief Affiche la correction d'un exercice de type 'categories'.
//
//! \param exo_id (String) : id de l'exercice
//! \param engine (Object) : corps du test
// -------------------------------------------------------------------------
function displayAnswerExerciseCategories(exo_id, engine){
    // On enleve les réponses du joueur
    engine.getElements('.pquizChoice').each(function(el){
        var classList = el.className.clean().split(" ");
        classList.each( function(cl){
            if (cl != 'pquizChoice')
                el.removeClass(cl);
        });
    });

    var answers = getCorrection(
            engine.getElementById(exo_id+'_correct'));
    
    // On place les responses
    answers.each(function(value, key){
        var category = engine.getElements('.category'+value)[0];
        var color_category = category.getElements('.pquizCategoryColor')[0];
        var classColorList = color_category.className.clean().split(" ");
        var color = classColorList[1];
        var choice = engine.getElementById(exo_id+'_'+key);
        choice.addClass(color);
        choice.addClass('category'+value);
    });    
}

// -------------------------------------------------------------------------
//! \brief Affiche les réponses d'un exercice de type 'categories'.
//
//! \param exo_id (String) : id de l'exercice
//! \param engine (Object) : corps du test
// -------------------------------------------------------------------------
function displayUserAnswerExerciseCategories(exo_id, engine){
    // On enleve les correction
    engine.getElements('.pquizChoice').each(function(el){
        var classList = el.className.clean().split(" ");
        classList.each( function(cl){
            if (cl != 'pquizChoice')
                el.removeClass(cl);
        });
    });

    var answers = getCorrection(
            engine.getElementById(exo_id+'_user'));

    // On place les responses
    answers.each(function(value, key){
        var category = engine.getElements('.category'+value)[0];
        var color_category = category.getElements('.pquizCategoryColor')[0];
        var classColorList = color_category.className.clean().split(" ");
        var color = classColorList[1];
        var choice = engine.getElementById(exo_id+'_'+key);
        choice.addClass(color);
        choice.addClass('category'+value);
    });
}
