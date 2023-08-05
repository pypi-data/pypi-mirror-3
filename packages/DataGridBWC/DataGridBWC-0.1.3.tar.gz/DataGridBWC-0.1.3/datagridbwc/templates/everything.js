$(document).ready(function(){
    $("form.datagrid-form").each(function(){
        datagrid_hide_filter_controls(this)
    });
});

function datagrid_hide_filter_controls(formref) {
    $form = $(formref)
    $show_link = $('<p class="dg-show-controls">Filtering, sorting, and paging: <span class="js-action-link">show controls</span></p>');
    $show_link.click(function(){
        $form.show();
        $show_link.remove();
        $form.find('h2').each(function(){
            $hide_link = $('<span class="dg-hide-controls js-action-link">Hide Controls</span>');
            $hide_link.click(function() {
                datagrid_hide_filter_controls(formref);
                $hide_link.remove();
            });
            $(this).after($hide_link);
        });
    })
    $form.before($show_link);
    $form.hide();
}
