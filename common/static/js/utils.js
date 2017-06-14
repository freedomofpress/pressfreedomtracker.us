// https://remysharp.com/2010/07/21/throttling-function-calls
export function throttle(fn, threshhold, scope) {
	threshhold || (threshhold = 250)
	var last;
	var deferTimer;
	return function () {
		var context = scope || this

		var now = +new Date,
		args = arguments;
		if (last && now < last + threshhold) {
			// hold on to it
			clearTimeout(deferTimer);
			deferTimer = setTimeout(function () {
				last = now;
				fn.apply(context, args);
			}, threshhold);
		} else {
			last = now;
			fn.apply(context, args);
		}
	};
}


export function isElementVisible(elm) {
	const height = window.innerHeight
	const rect = elm.getBoundingClientRect()
	const threshold = (rect.top + rect.bottom) * 0.75
	return threshold < height
}
