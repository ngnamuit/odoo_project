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

    _onSubmit: function (event) {
        console.log("Jump into _onSubmit ===== "); // need to print this log for debugging
        this._super.apply(this, arguments);
        event.preventDefault();
        var $target = $(event.currentTarget);
        if ($target.val() === 'review') {
            this.isReview = true;
//            var options = {};
//            this._submitForm(options);
        }

    },
    _onNextScreenDone: function (result, options) {
        console.log("Jump into _onNextScreenDone ======= "); // need to print this log for debugging
        var self = this;
        var review_url = '';
        if (options && this.isReview && result && !result.error){
            var surveyToken = self.options.surveyToken;
            var answerToken = self.options.answerToken;
            review_url = '/survey/print/' + surveyToken + '?answer_token=' + answerToken + '&review=True';
            window.location.href = review_url
            utils.set_cookie('survey_' + surveyToken, '', -1); // delete survey cookie
            return
        } else {
            this._super.apply(this, arguments);
        }
    }

});

return SurveyForm;
});


