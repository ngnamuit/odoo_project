odoo.define('survey_file_upload_field.form', function (require) {
'use strict';

var SuveryForm = require('survey.form');
var utils = require('web.utils');
var core = require('web.core');
var _t = core._t;

var SuveryForm = SuveryForm.include({
     events: _.extend({}, SuveryForm.prototype.events, {
        'change .o_survey_question_upload_file': 'on_file_change',
    }),

    start: function () {
        var self = this;
        return this._super.apply(this, arguments).then(function () {
            self.useFileAPI = !!window.FileReader;
            self.max_upload_size = 100 * 1024 * 1024; // 64Mo
            self.file_value = {};
            if (!self.useFileAPI) {
                self.fileupload_id = _.uniqueId('o_fileupload');
                $(window).on(self.fileupload_id, function () {
                    var args = [].slice.call(arguments).slice(1);
                    self.on_file_uploaded.apply(self, args);
                });
            }
        });
    },

    on_file_change: function (e) {
        var self = this;
        var file_node = e.target;
        var files_list = [];
        var children = "";
        var output = document.getElementById('fileList');
        if ((this.useFileAPI && file_node.files.length) || (!this.useFileAPI && $(file_node).val() !== '')) {
            if (this.useFileAPI) {
                var files = file_node.files;
                for (const file of files) {
                    if (file.size > this.max_upload_size) {
                        var msg = _t("The selected file exceed the maximum file size of %s.");
                        this.do_warn(_t("File upload"), _.str.sprintf(msg, utils.human_size(this.max_upload_size)));
                        return false;
                    }
                    utils.getDataURLFromFile(file).then(function (data) {
                        data = data.split(',')[1];
                        files_list.push({"file_name": file.name, "data": data});
                    });
                    self.file_value[$(file_node).data('name')] = files_list;
                    self.file_value[$(file_node).data('name')]['is_answer_update'] = true;
                    children += '<li>' + file.name + '</li>';
                }

                output.innerHTML = '<ul>'+children+'</ul>';

            }
        }
    },

    _prepareSubmitValues: function (formData, params) {
        this._super.apply(this, arguments);
        var self = this;
        // Get all question answers by question type
        this.$('.o_survey_question_upload_file[data-question-type]').each(function () {
            switch ($(this).data('questionType')) {
                case 'upload_file':
                    params = self._prepareSubmitFiles(params, $(this), $(this).data('name'));
                    try {
                        self.file_value[$(this).data('name')]['is_answer_update'] = false;
                    } catch(err) {
                        console.log(err);
                    }

                    break;
            }
        });
    },

    _prepareSubmitFiles: function (params, $parent, questionId) {
        try {
            params[questionId] = {'values': this.file_value[questionId], 'is_answer_update': this.file_value[questionId]['is_answer_update']};
        } catch(err) {
            console.log(err);
        }
        return params;
    },
});

return SuveryForm;
});