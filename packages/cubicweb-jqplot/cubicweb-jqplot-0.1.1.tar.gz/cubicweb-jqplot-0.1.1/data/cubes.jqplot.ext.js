
FLOAT_PRECISION = 1;

function floatTickFormatter(format, val) {
    var power = Math.pow(10, FLOAT_PRECISION || 0);
    return String(Math.round(val * power) / power);
}

function hoursTickFormatter(format, val) {
    hours = Math.floor(val)
    minutes = Math.round((val - hours) * 60)
    if (hours < 0)
        hours = '-' + (-(hours + 1))
    if (minutes != 0) {
	return String(hours + 'h' + minutes + 'm')
    }
    return String(hours + 'h')
}


function dateTickFormatter(format, val) {
    return $.jsDate.strftime(val, format);
};


function monthTickFormatter(format, val) {
    if (val < 100) { return ''; } // XXX coordinate box sent erroneous value
    year = Math.floor(val / 12);
    month = (val % 12) + 1;
    return year + '/' + month;
}
