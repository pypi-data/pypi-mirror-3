function monthTickFormatter(format, val) {
    if (val < 100) { return ''; } // XXX coordinate box sent erroneous value
    year = Math.floor(val / 12);
    month = (val % 12) + 1;
    return year + '/' + month;
}

function dateTickFormatter(format, val) {
    return $.jsDate.strftime(val, format);
};
