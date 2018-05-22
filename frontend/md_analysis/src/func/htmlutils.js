let HtmlUtil = {
    genOptionString: (val, txt = null, selected = false) => {
        return `<option value="${val}" ${ ((selected)
            ? 'selected'
            : '')}>${ ((txt)
            ? txt
            : val)}</option>`;
    }

};

export default HtmlUtil;