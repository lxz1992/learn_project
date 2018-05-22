import 'jquery';

const jq = jQuery.noConflict();

jq(document).on('click', '.cr-review-content-home .search-filter-keyword .add-keyword', (e) => {
    let keywordElement = "<span class='label-key'>AND</span><div class='search-keyword-input'><input type='text' class='form-control'></div>";
    jq(document)
        .find('.search-filter-keyword .search-keyword-input')
        .last()
        .after(keywordElement);

    let inputNumber = jq(document).find('.search-filter-keyword .search-keyword-input').length;
    if (inputNumber === 3) {
        jq(e.currentTarget)
            .slideToggle()
            .siblings()
            .hide('show');
    }
});

jq(document).on('click', '.cr-review-content-home .search-filter-keyword .label-key', (e) => {
    let oldText = jq(e.currentTarget).text();
    let newText = oldText === "OR" ? "AND" : "OR";
    jq(e.currentTarget)
        .parent()
        .find('.label-key')
        .text(newText);
});