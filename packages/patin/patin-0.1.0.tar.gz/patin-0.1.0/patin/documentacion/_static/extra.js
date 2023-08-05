$('document').ready(function() {

    $('pre').click(function () {
            var codigo = this.innerHTML.replace(/<(?:.|\n)*?>/gm, '');
            c.crear_programa_temporal(codigo);
        });
});
