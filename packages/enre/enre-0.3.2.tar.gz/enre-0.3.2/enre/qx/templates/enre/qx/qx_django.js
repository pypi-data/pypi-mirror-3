{% load url from future %}
{% load csrf_token from qooxdoo %}
{% load i18n %}

qx.Class.define('enre.utils.Django', {

    statics: {
        staticUrl: '{{ STATIC_URL }}',
        resourceUrl: '{{ STATIC_URL }}enre/qx/resource',
        sourceUrl: '{{ STATIC_URL }}enre/qx',
        csrfToken: '{% csrf_token %}',
        rpcUrl: '{% url 'enre_qx_rpc' %}',
        storeUrl: '{% url 'enre_qx_store' '' %}',
        ajaxUrl: '{% url 'enre_qx_ajax' '' %}',

        _correctStatic: function() {
            qx.$$libraries.__out__.sourceUri = enre.utils.Django.sourceUrl;
            qx.$$libraries.enre.resourceUri = enre.utils.Django.resourceUrl;
            qx.$$libraries.enre.sourceUri = enre.utils.Django.sourceUrl;
            qx.$$libraries.qx.resourceUri = enre.utils.Django.resourceUrl;
            qx.$$libraries.qx.sourceUri = enre.utils.Django.sourceUrl;
        },

        _setLocale: function() {
            {% get_current_language as LANGUAGE_CODE %}
            qx.locale.Manager.getInstance().setLocale('{{ LANGUAGE_CODE }}');
        }
    }

});

enre.utils.Django._correctStatic();
enre.utils.Django._setLocale();
