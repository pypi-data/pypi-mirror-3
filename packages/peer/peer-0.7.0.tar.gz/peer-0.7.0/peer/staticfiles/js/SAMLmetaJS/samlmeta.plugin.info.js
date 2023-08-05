(function($) {
	var UI = {
		"clearInfoname": function() {
			$("div#info div#infoname").empty();
		},
		"clearInfodescr": function() {
			$("div#info div#infodescr").empty();
		},
		"clearInfokws": function() {
			$("div#info div#infokws").empty();
		},
		"addInfoname": function(lang, name) {
			var randID = 'infoname' + Math.floor(Math.random() * 10000 + 1000);
			var infoHTML = '<div class="infonamediv">' +
				'<select name="' + randID + '-lang-name" id="' + randID + '-lang">';
			var languageFound = false;
			var language, checked;
			for (language in SAMLmetaJS.Constants.languages) {
				if (SAMLmetaJS.Constants.languages.hasOwnProperty(language)) {
					checked = '';
					if (lang === language) {
						checked = ' selected="selected" ';
						languageFound = true;
					}
					infoHTML += '<option value="' + language + '" ' + checked + '>' +
						SAMLmetaJS.Constants.languages[language] +
						'</option>';
				}
			}
			if (!languageFound) {
				infoHTML += '<option value="' + lang + '" selected="selected">Unknown language (' + lang + ')</option>';
			}

			infoHTML += '</select>' +
				'<input type="text" name="' + randID + '-name-name" id="' + randID + '-name" value="' + (name || '') + '" />' +
				'<button style="" class="removename">Remove</button>' +
				'</div>';

			$(infoHTML).appendTo("div#info div#infoname").find('button.removename').click(function (e) {
				e.preventDefault();
				$(e.target).closest('div.infonamediv').remove();
			});
		},
		"addInfodescr": function(lang, descr) {
			var randID = 'infodescr' + Math.floor(Math.random() * 10000 + 1000);
			var infoHTML = '<div class="infodescrdiv"><div>' +
				'<select name="' + randID + '-lang-name" id="' + randID + '-lang">';
			var languageFound = false;
			var language, checked;

			for (language in SAMLmetaJS.Constants.languages) {
				if (SAMLmetaJS.Constants.languages.hasOwnProperty(language)) {
					checked = '';
					if (lang === language) {
						checked = ' selected="selected" ';
						languageFound = true;
					}
					infoHTML += '<option value="' + language + '" ' + checked + '>' +
						SAMLmetaJS.Constants.languages[language] +
						'</option>';
				}
			}
			if (!languageFound) {
				infoHTML += '<option value="' + lang + '" selected="selected">Unknown language (' + lang + ')</option>';
			}

			infoHTML += '</select>' +
				'<button style="" class="removedescr">Remove</button>' +
				'</div><div>' +
				'<textarea name="' + randID + '-name-name" id="' + randID + '-name">' + (descr || '') + '</textarea>' +

			'</div></div>';

			$(infoHTML).appendTo("div#info div#infodescr").find('button.removedescr').click(function (e) {
				e.preventDefault();
				$(e.target).closest('div.infodescrdiv').remove();
			});
		},
		"addInfokws": function(lang, kws) {
			var randID = 'infokws' + Math.floor(Math.random() * 10000 + 1000);
			var infoHTML = '<div class="infokwsdiv">' +
				'<select name="' + randID + '-lang-name" id="' + randID + '-lang">';
			var languageFound = false;
			var language, checked;

			for (language in SAMLmetaJS.Constants.languages) {
				if (SAMLmetaJS.Constants.languages.hasOwnProperty(language)) {
					checked = '';
					if (lang === language) {
						checked = ' selected="selected" ';
						languageFound = true;
					}
					infoHTML += '<option value="' + language + '" ' + checked + '>' +
						SAMLmetaJS.Constants.languages[language] +
						'</option>';
				}
			}
			if (!languageFound) {
				infoHTML += '<option value="' + lang + '" selected="selected">Unknown language (' + lang + ')</option>';
			}

			infoHTML += '</select>' +
				'<input type="text" name="' + randID + '-name-name" id="' + randID + '-name" value="' + (kws || '') + '" />' +
				'<button style="" class="removekws">Remove</button>' +
				'</div>';

			$(infoHTML).appendTo("div#info div#infokws").find('button.removekws').click(function (e) {
				e.preventDefault();
				$(e.target).closest('div.infokwsdiv').remove();
			});
		}
	};

	SAMLmetaJS.plugins.info = {
		tabClick: function (handler) {
			handler($("a[href='#info']"));
		},

		addTab: function (pluginTabs) {
			pluginTabs.list.push('<li><a href="#info">Information</a></li>');
			pluginTabs.content.push(
				'<div id="info">' +
					'<fieldset class="entityid"><legend>Entity ID</legend>' +
						'<div id="div-entityid">' +
							'<input style="width: 600px" type="text" name="entityid" id="entityid" value="" />' +
							'<p style="margin: 0px">The format MUST be an URI.</p>' +
						'</div>' +
					'</fieldset>' +

					'<fieldset class="name"><legend>Name of Service</legend>' +
						'<div id="infoname"></div>' +
						'<div>' +
							'<button class="addname">Add name in one more languages</button>' +
						'</div>' +
					'</fieldset>' +

					'<fieldset class="description"><legend>Description of Service</legend>' +
						'<div id="infodescr"></div>' +
						'<div>' +
							'<button class="adddescr">Add description in one more languages</button>' +
						'</div>' +
					'</fieldset>' +

					'<fieldset class="kws"><legend>Keywords (space separated)</legend>' +
						'<div id="infokws"></div>' +
						'<div>' +
							'<button class="addkws">Add keywords in one more languages</button>' +
						'</div>' +
					'</fieldset>' +

				'</div>'
			);
		},

		setUp: function () {
			$("div#info button.addname").click(function(e) {
				e.preventDefault();
				UI.addInfoname('en', '');
			});
			$("div#info button.adddescr").click(function(e) {
				e.preventDefault();
				UI.addInfodescr('en', '');
			});
			$("div#info button.addkws").click(function(e) {
				e.preventDefault();
				UI.addInfokws('en', '');
			});
		},

		fromXML: function (entitydescriptor) {
			var l;

			// Add name, description and kws
			UI.clearInfoname();
			if (entitydescriptor.name) {
				for (l in entitydescriptor.name) {
					if (entitydescriptor.name.hasOwnProperty(l)) {
						UI.addInfoname(l, entitydescriptor.name[l]);
					}
				}
			}

			UI.clearInfodescr();
			if (entitydescriptor.descr) {
				for (l in entitydescriptor.descr) {
					if (entitydescriptor.descr.hasOwnProperty(l)) {
						UI.addInfodescr(l, entitydescriptor.descr[l]);
					}
				}
			}
			UI.clearInfokws();
			if (entitydescriptor.kws) {
				for (l in entitydescriptor.kws) {
					if (entitydescriptor.kws.hasOwnProperty(l)) {
						UI.addInfokws(l, entitydescriptor.kws[l]);
					}
				}
			}
		},

		toXML: function (entitydescriptor) {
			$('div#infoname > div').each(function (index, element) {
				var value = $(element).children('input').attr('value');
				if (!value) {
					return;
				}
				if (!entitydescriptor.name) entitydescriptor.name = {};
				entitydescriptor.name[$(element).children('select').val()] = value;
			});
			$('div#infodescr > div').each(function (index, element) {
				var value = $(element).find('div > textarea').val();
				if (!value) {
					return;
				}
				if (!entitydescriptor.descr) entitydescriptor.descr = {};
				entitydescriptor.descr[$(element).find('div > select').val()] = value;
			});
			$('div#infokws > div').each(function (index, element) {
				var value = $(element).children('input').attr('value');
				if (!value) {
					return;
				}
				if (!entitydescriptor.kws) entitydescriptor.kws = {};
				entitydescriptor.kws[$(element).children('select').val()] = value;
			});
		}
	};

}(jQuery));
