import * as curlify from './curlify.js'

// test('adds 1 + 2 to equal 3', () => {
//   expect(sum(1, 2)).toBe(3);
// });

describe('processing plain text', () => {
	test('converts single quotes', () => {
		expect(curlify.plainText(`'Hello'`)).toBe(`‘Hello’`)
	})

	test('converts double quotes', () => {
		expect(curlify.plainText(`"Hello"`)).toBe(`“Hello”`)
	})

	test('converts apostrophes', () => {
		expect(curlify.plainText(`I'm`)).toBe(`I’m`)
	})

	test('converts nested quotes and apostrophes', () => {
		let input = `"That's a 'magic' shoe."`
		expect(curlify.plainText(input)).toBe(`“That’s a ‘magic’ shoe.”`)
	})

	test('converts double quotes adjacent to single quotes', () => {
		let input = `"'Stop!' is what he said."`
		let expected = `“‘Stop!’ is what he said.”`
		expect(curlify.plainText(input)).toBe(expected)
	})

	test('converts quotes adjacent to brackets', () => {
		let input = `She said "[t]his is good."`
		let expected = `She said “[t]his is good.”`
		expect(curlify.plainText(input)).toBe(expected)
	})

	test('converts apostrophes nested inside single quotes', () => {
		let input = `'Frank's mother asked about Peter's situation from '95 to '98.'`
		let expected = `‘Frank’s mother asked about Peter’s situation from ’95 to ‘98.’`
		expect(curlify.plainText(input)).toBe(expected)
	})
})

let a = `<meta charset="utf-8"><p dir="ltr" style="line-height:1.38;margin-left: 36pt;margin-top:0pt;margin-bottom:0pt;" id="docs-internal-guid-48cc829d-7fff-c23e-56be-42703aeed53d"><span style="font-size:11pt;font-family:Arial,sans-serif;color:#000000;background-color:transparent;font-weight:400;font-style:normal;font-variant:normal;text-decoration:none;vertical-align:baseline;white-space:pre;white-space:pre-wrap;">&ldquo;Something in the water.&rdquo;</span></p><p dir="ltr" style="line-height:1.38;margin-left: 36pt;margin-top:0pt;margin-bottom:0pt;"><span style="font-size:11pt;font-family:Arial,sans-serif;color:#000000;background-color:transparent;font-weight:400;font-style:normal;font-variant:normal;text-decoration:none;vertical-align:baseline;white-space:pre;white-space:pre-wrap;">&quot;Hello world.&quot;</span></p><br /><p dir="ltr" style="line-height:1.38;margin-left: 36pt;margin-top:0pt;margin-bottom:0pt;"><span style="font-size:11pt;font-family:Arial,sans-serif;color:#000000;background-color:transparent;font-weight:400;font-style:normal;font-variant:normal;text-decoration:none;vertical-align:baseline;white-space:pre;white-space:pre-wrap;">&quot;He's always doing that, O'Leary.&quot;</span></p><br /><br />`

describe('processing html', () => {
	test('converts single quotes', () => {
		let input = `<meta charset="utf-8"><p dir="ltr"><span>'Hello.'</span></p><br /><br />`
		let expected = `<meta charset="utf-8"><p dir="ltr"><span>‘Hello.’</span></p><br><br>`
		expect(curlify.html(input)).toBe(expected)
	})

	test('converts double quotes', () => {
		let input = `<meta charset="utf-8"><p dir="ltr"><span>&quot;Hello.&quot;</span></p><br /><br />`
		let expected = `<meta charset="utf-8"><p dir="ltr"><span>“Hello.”</span></p><br><br>`
		expect(curlify.html(input)).toBe(expected)
	})

	test('converts nested quotes', () => {
		let input = `<meta charset="utf-8"><p dir="ltr"><span>&quot;That's a 'magic' shoe.&quot;</span></p>`
		let expected = `<meta charset="utf-8"><p dir="ltr"><span>“That’s a ‘magic’ shoe.”</span></p>`
		expect(curlify.html(input)).toBe(expected)
	})

	test('converts double quotes adjacent to single quotes', () => {
		let input = `<meta charset="utf-8"><p dir="ltr"><span>&quot;'Stop!' is what he said.&quot;</span></p>`
		let expected = `<meta charset="utf-8"><p dir="ltr"><span>“‘Stop!’ is what he said.”</span></p>`
		expect(curlify.html(input)).toBe(expected)
	})

	test('converts double quotes adjacent to brackets', () => {
		let input = `<meta charset="utf-8"><p dir="ltr"><span>She said &quot;[t]his is good.&quot;</span></p>`
		let expected = `<meta charset="utf-8"><p dir="ltr"><span>She said “[t]his is good.”</span></p>`
		expect(curlify.html(input)).toBe(expected)
	})

	test('converts multiple lines of text at once', () => {
		let input = `<meta charset="utf-8"><p dir="ltr"><span>She said &quot;[t]his is good.&quot;</span></p><p dir="ltr"><span>&quot;She </span><span style="font-style:italic;">didn't</span><span style="font-style:normal;">!&quot;</span></p>`
		let expected = `<meta charset="utf-8"><p dir="ltr"><span>She said “[t]his is good.”</span></p><p dir="ltr"><span>“She </span><span style="font-style:italic;">didnyt</span><span style="font-style:normal;">!”</span></p>`
	})
})
