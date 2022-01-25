odoo.define('survey_custom.form', function (require) {
'use strict';

var SurveyForm = require('survey.form');
var utils = require('web.utils');

var SurveyForm = SurveyForm.include({

    _prepareSubmitValues: function (formData, params) {
        this._super.apply(this, arguments);
        var self = this;
        // Get all question answers by question type
        this.$('[data-question-type]').each(function () {
            switch ($(this).data('questionType')) {
                case 'percentage':
                case 'currency':
                    params[this.name] = this.value;
                    break;
            }
        });
    },

});

return SurveyForm;
});