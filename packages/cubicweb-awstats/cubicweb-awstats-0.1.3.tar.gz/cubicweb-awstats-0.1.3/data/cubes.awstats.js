// TODO - customize by adding yaxis : {tickFormatter : suffixFormatter}, (when flot will be customizable)
function suffixFormatter(val, axis) {
    if (val > 1e12)
	return (val / 1e12).toFixed(axis.tickDecimals) + " T";
    else if (val > 1e9)
	return (val / 1e9).toFixed(axis.tickDecimals) + " G";
    else if (val > 1e6)
	return (val / 1e6).toFixed(axis.tickDecimals) + " M";
    else if (val > 1000)
	return (val / 1000).toFixed(axis.tickDecimals) + " k";
    else
	return val.toFixed(axis.tickDecimals);
}