const it_is_our_turn = () => {
	let clock_bottom = document.querySelector('div.rclock-bottom')
	let first_move = document.querySelector('rm6 .message strong')
	return (clock_bottom && (
		clock_bottom.classList.contains('running')
		|| clock_bottom.textContent === 'Your turn'
	)) || (first_move && first_move.textContent.includes('turn'))
}

const game_is_over = () => {
	let x = document.querySelector('.result-wrap .result')
	return x && x.textContent
}

const checkEl = () => {
	return it_is_our_turn() ? 'turn' : game_is_over()
}

let res = checkEl()
if (res) {
	callback(res)
} else {
	let observer = new MutationObserver((list, o) => {
		let res = checkEl()
		if (res) {
			callback(res)
			o.disconnect()
		}
	})
	observer.observe(document.querySelector('rm6'), {subtree: true, childList: true})
}
